"""Agent loop engine: plan → act → observe → replan (M1 + D1)."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from m1_m2.context_manager import ContextManager
from m1_m2.errors import ErrorClass, FatalAgentError
from m1_m2.llm_client import LLMClient, PlanContext
from m1_m2.tool_executor import ToolExecutor
from m1_m2.trace import TraceCollector
from m3.cost_monitor import CostMonitor
from m3.model_router import ModelRouter
from m3.rate_limiter import RateLimiter
from m3.token_counter import estimate_tokens


class Phase(str, Enum):
    PARSE = "parse_intent"
    PLAN = "plan"
    ACT = "act"
    OBSERVE = "observe"
    REPLAN = "replan"
    DONE = "done"


_PSEUDO_REPLAN_PLAN = (
    "Let me fix the parameter name — use indexPattern not index_pattern"
)


@dataclass
class LoopConfig:
    max_rounds: int = 3
    step_limit: int = 20
    detect_loop_fingerprint: bool = True
    simulate_container_death_after_round: int | None = None
    always_fail_tests: bool = False
    pseudo_replan: bool = False
    llm_client: LLMClient | None = None
    checkpoint_dir: Path | None = None
    require_hitl: bool = False
    max_retries: int = 2
    retry_backoff_s: float = 0.05


@dataclass
class LoopEngine:
    task: str
    config: LoopConfig = field(default_factory=LoopConfig)
    trace: TraceCollector = field(default_factory=TraceCollector)
    tools: ToolExecutor = field(init=False)
    history: list[dict[str, Any]] = field(default_factory=list)
    round: int = 0
    success: bool = False
    observation: str = ""
    plan: str = ""
    run_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    _fingerprints: list[str] = field(default_factory=list)
    context_manager: ContextManager = field(default_factory=ContextManager)
    model_router: ModelRouter = field(default_factory=ModelRouter)
    rate_limiter: RateLimiter = field(default_factory=RateLimiter)
    cost_monitor: CostMonitor = field(default_factory=CostMonitor)
    route_decisions: list[dict[str, Any]] = field(default_factory=list)
    last_context_prompt: str = ""
    selected_model: str = "mock-small"
    rate_limited: bool = False

    def __post_init__(self) -> None:
        self.tools = ToolExecutor(
            self.trace,
            always_fail_tests=self.config.always_fail_tests,
            require_hitl=self.config.require_hitl,
            max_retries=self.config.max_retries,
            retry_backoff_s=self.config.retry_backoff_s,
        )

    def _record_phase(self, phase: Phase, detail: str) -> None:
        self.history.append(
            {
                "ts": datetime.now(timezone.utc).isoformat(),
                "round": self.round,
                "phase": phase.value,
                "detail": detail,
            }
        )

    def _make_plan(self) -> str:
        """Build layered context, route model, then produce plan (Phase C)."""
        layers = self.context_manager.build(
            task=self.task,
            observation=self.observation,
            history=self.history,
            plan=self.plan,
        )
        prompt = layers.render()
        self.last_context_prompt = prompt

        decision = self.model_router.route(self.task)
        limited = not self.rate_limiter.allow(1.0)
        if limited:
            self.rate_limited = True
        model = decision.fallback if limited else decision.model
        self.selected_model = model
        self.route_decisions.append(
            {
                "round": self.round,
                "model": model,
                "tier": decision.tier,
                "fallback": decision.fallback,
                "rate_limited": limited,
                "reason": decision.reason,
            }
        )

        client = self.config.llm_client
        if client is not None:
            ctx = PlanContext(
                task=self.task,
                observation=self.observation,
                history=self.history,
                round=self.round,
                pseudo_replan=self.config.pseudo_replan,
                model=model,
                context_prompt=prompt,
            )
            plan = client.generate_plan(ctx)
        elif self.config.pseudo_replan and self.round > 1:
            plan = _PSEUDO_REPLAN_PLAN
        elif self.round <= 1:
            plan = "Apply minimal patch without reading test output"
        else:
            plan = (
                f"Replan using observation: {self.observation}; "
                "read test file and fix assertion"
            )

        in_tok = estimate_tokens(prompt)
        out_tok = estimate_tokens(plan)
        self.cost_monitor.record(
            input_tokens=in_tok,
            output_tokens=out_tok,
            model=model,
        )
        return plan

    def _fingerprint(self, tool: str, payload: dict) -> str:
        raw = json.dumps({"tool": tool, "payload": payload}, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def _check_fingerprint_loop(self, tool: str, payload: dict) -> None:
        if not self.config.detect_loop_fingerprint:
            return
        fp = self._fingerprint(tool, payload)
        self._fingerprints.append(fp)
        if self._fingerprints.count(fp) >= 3:
            raise FatalAgentError(
                f"Loop fingerprint detected: {tool} called 3x with identical args",
                ErrorClass.FATAL,
            )

    def _observe_tests(self, round_idx: int) -> tuple[bool, str, ErrorClass]:
        result = self.tools.call("act", "run_tests", {"round": round_idx - 1})
        if result.get("error_class") == ErrorClass.FATAL.value:
            raise FatalAgentError(result.get("stdout", "fatal tool error"), ErrorClass.FATAL)
        if result.get("exit_code") == 0:
            return True, result.get("summary", "ok"), ErrorClass.RECOVERABLE
        return False, result.get("summary", "failed"), ErrorClass.RETRYABLE

    def _save_checkpoint(self) -> None:
        """Persist intermediate state so a long task can resume after interruption."""
        if self.config.checkpoint_dir is None:
            return
        self.config.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "run_id": self.run_id,
            "task": self.task,
            "config": asdict(self.config),
            "round": self.round,
            "success": self.success,
            "plan": self.plan,
            "observation": self.observation,
            "history": self.history,
            "_fingerprints": self._fingerprints,
            "container_alive": self.tools._container_alive,
        }
        # Remove non-serializable llm_client from config snapshot.
        payload["config"].pop("llm_client", None)
        path = self.config.checkpoint_dir / f"{self.run_id}.json"
        path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")

    @classmethod
    def resume_from(
        cls,
        checkpoint_path: Path,
        *,
        task: str | None = None,
        config: LoopConfig | None = None,
    ) -> "LoopEngine":
        """Resume an engine from a checkpoint file."""
        data = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        if config is None:
            config_data = data.get("config", {})
            config_data.pop("llm_client", None)
            ckpt = config_data.get("checkpoint_dir")
            if isinstance(ckpt, str):
                config_data["checkpoint_dir"] = Path(ckpt)
            config = LoopConfig(**config_data)
        engine = cls(task=task or data["task"], config=config)
        engine.run_id = data["run_id"]
        engine.round = data["round"]
        engine.success = data["success"]
        engine.plan = data["plan"]
        engine.observation = data["observation"]
        engine.history = data["history"]
        engine._fingerprints = data.get("_fingerprints", [])
        engine.tools._container_alive = data.get("container_alive", True)
        return engine

    def run(self) -> "LoopEngine":
        self._record_phase(Phase.PARSE, f"Intent: resolve task — {self.task}")

        steps = 0
        while self.round < self.config.max_rounds and steps < self.config.step_limit:
            self.round += 1
            steps += 1

            if (
                self.config.simulate_container_death_after_round is not None
                and self.round > self.config.simulate_container_death_after_round
            ):
                self.tools.kill_container()

            self.plan = self._make_plan()
            self._record_phase(Phase.PLAN, self.plan)

            self._check_fingerprint_loop("docker_exec", {"command": self.plan})
            exec_out = self.tools.call("act", "docker_exec", {"command": self.plan})
            if exec_out.get("error_class") == ErrorClass.FATAL.value:
                raise FatalAgentError(
                    exec_out.get("error") or exec_out.get("stdout", "container dead"),
                    ErrorClass.FATAL,
                )
            self._record_phase(Phase.ACT, f"Executed: {self.plan}")

            ok, obs, err_class = self._observe_tests(self.round)
            self.observation = obs
            self._record_phase(
                Phase.OBSERVE,
                f"{obs} [{err_class.value}]",
            )

            self._save_checkpoint()

            if ok:
                self.success = True
                self._record_phase(Phase.DONE, "Task completed")
                break

            if self.round >= self.config.max_rounds:
                self._record_phase(Phase.DONE, "Max rounds exceeded")
                break

            self._record_phase(Phase.REPLAN, "Scheduling replan with error context")

        return self

    def abort_fatal(self, message: str) -> None:
        self._record_phase(Phase.DONE, f"FatalAgentError: {message}")

    def persist(self, out_dir: Path) -> Path:
        run_dir = out_dir / self.run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        self.trace.write(run_dir / "trace.json")
        self.trace.write_state(
            run_dir / "state.json",
            {
                "run_id": self.run_id,
                "task": self.task,
                "round": self.round,
                "success": self.success,
                "plan": self.plan,
                "observation": self.observation,
                "history": self.history,
            },
        )
        self._save_checkpoint()
        return run_dir
