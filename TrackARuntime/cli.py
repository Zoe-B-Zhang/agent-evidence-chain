#!/usr/bin/env python3
"""TrackARuntime CLI — anchor project for Track A residency."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from m1_m2.errors import FatalAgentError
from m1_m2.llm_client import MockLLMClient
from m1_m2.loop_engine import LoopConfig, LoopEngine
from m1_m2.metrics import MetricsCollector
from m3.cost_monitor import CostMonitor
from m3.model_router import ModelRouter
from m3.pipeline import run_harness, write_harness_report
from m3.rollout_controller import (
    load_rollout_state,
    reset_rollout_state,
    run_watch_cycle,
    save_rollout_state,
)
from m3.token_counter import estimate_tokens
from m4.baseline import DEFAULT_BASELINE
from m4.runner import run_eval, write_eval_report

M1_M2_EVIDENCE = ROOT / "m1_m2" / "evidence"
M3_EVIDENCE = ROOT / "m3" / "evidence"
M4_EVIDENCE = ROOT / "m4" / "evidence"


def _configure_stdio() -> None:
    """Reconfigure stdout/stderr to UTF-8 when supported (Windows cp1252 safe)."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8")
            except (AttributeError, OSError, ValueError):
                pass


def _parse_unit_interval(value: str, flag: str) -> float:
    """把命令行数值解析为闭区间 [0, 1] 的浮点数。

    Parameters:
        value (str): 原始参数字符串。
        flag (str): 参数名，写入错误信息。

    Returns:
        float: 落在 [0, 1] 内的数值。
    """
    try:
        number = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"{flag} must be a number between 0 and 1"
        ) from exc
    if not 0.0 <= number <= 1.0:
        raise argparse.ArgumentTypeError(f"{flag} must be between 0 and 1")
    return number


def _eval_baseline(value: str) -> str:
    """解析 eval --baseline：允许 auto，或 [0, 1] 内的数字。

    Parameters:
        value (str): 用户传入的 baseline。

    Returns:
        str: ``auto`` 或原始数字字符串。
    """
    if value == "auto":
        return value
    _parse_unit_interval(value, "baseline")
    return value


def _promote_baseline(value: str) -> float:
    """解析 harness --eval-baseline。

    Parameters:
        value (str): 用户传入的门槛。

    Returns:
        float: [0, 1] 内的门槛。
    """
    return _parse_unit_interval(value, "baseline")


def _gray_percent(value: str) -> int:
    """解析灰度百分比，必须是 0 到 100 的整数。

    Parameters:
        value (str): 用户传入的百分比。

    Returns:
        int: 合法灰度百分比。
    """
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "gray-percent must be an integer between 0 and 100"
        ) from exc
    if number < 0 or number > 100:
        raise argparse.ArgumentTypeError("gray-percent must be between 0 and 100")
    return number


def _max_rounds(value: str) -> int:
    """解析最大轮次，必须是正整数。

    Parameters:
        value (str): 用户传入的轮次。

    Returns:
        int: 至少为 1 的轮次。
    """
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("max-rounds must be an integer >= 1") from exc
    if number < 1:
        raise argparse.ArgumentTypeError("max-rounds must be >= 1")
    return number


def _build_run_config(args: argparse.Namespace) -> LoopConfig:
    """Build LoopConfig from CLI run arguments."""
    llm_client = MockLLMClient() if getattr(args, "llm", None) == "mock" else None
    checkpoint_dir = Path(args.checkpoint_dir) if getattr(args, "checkpoint_dir", None) else None
    return LoopConfig(
        max_rounds=args.max_rounds,
        simulate_container_death_after_round=args.simulate_container_death,
        always_fail_tests=args.always_fail_tests,
        pseudo_replan=args.pseudo_replan,
        llm_client=llm_client,
        checkpoint_dir=checkpoint_dir,
        require_hitl=args.require_hitl,
        max_retries=args.max_retries,
        retry_backoff_s=args.retry_backoff_s,
    )


def _collect_run_metrics(engine: LoopEngine, out_dir: Path) -> Path | None:
    """Write latency/token/cost metrics using in-loop platform stubs (Phase C)."""
    cost = engine.cost_monitor.summary()
    last_route = engine.route_decisions[-1] if engine.route_decisions else {}
    metrics = MetricsCollector(
        run_id=engine.run_id,
        task=engine.task,
        model=engine.selected_model,
        route_tier=str(last_route.get("tier", "simple")),
        rate_limited=engine.rate_limited,
        extra={
            "route_reason": last_route.get("reason", ""),
            "route_decisions": engine.route_decisions,
            "context_chars": len(engine.last_context_prompt),
            "cost_calls": cost.get("calls", 0),
        },
    )
    for event in engine.trace.events:
        metrics.add_latency(event.latency_ms)
        # Attach token/cost summary onto each span via metrics file (trace stays lean).
    metrics.set_cost(
        input_tokens=cost.get("total_input_tokens", 0),
        output_tokens=cost.get("total_output_tokens", 0),
        cost_usd=cost.get("total_cost_usd", 0.0),
    )
    return metrics.write(out_dir)


def _write_harness_metrics(report: dict, out_dir: Path) -> Path:
    """Estimate token/cost for a harness tick and write metrics JSON."""
    router = ModelRouter()
    decision = router.route(f"harness prompt {report.get('prompt_version', 'v1')}")
    text = f"{report.get('output', '')} {report.get('message', '')}"
    in_tok = estimate_tokens(text)
    out_tok = estimate_tokens(report.get("action", ""))
    cost_mon = CostMonitor()
    cost_mon.record(input_tokens=in_tok, output_tokens=out_tok, model=decision.model)
    run_id = f"harness-{report.get('prompt_version', 'v1')}"
    metrics = MetricsCollector(
        run_id=run_id,
        task=f"harness:{report.get('prompt_version')}",
        model=decision.model,
        route_tier=decision.tier,
        extra={"harness_action": report.get("action"), "guardrail_ok": report.get("guardrail_ok")},
    )
    metrics.set_cost(
        input_tokens=cost_mon.total_input_tokens,
        output_tokens=cost_mon.total_output_tokens,
        cost_usd=cost_mon.total_cost_usd,
    )
    return metrics.write(out_dir)


def cmd_run(args: argparse.Namespace) -> int:
    if not str(args.task).strip():
        print("Fatal: task must be non-empty", file=sys.stderr)
        return 2
    config = _build_run_config(args)
    if args.resume_from:
        try:
            engine = LoopEngine.resume_from(
                Path(args.resume_from),
                task=args.task,
                config=config,
            )
        except FatalAgentError as exc:
            print(f"Fatal: {exc}", file=sys.stderr)
            return 2
    else:
        engine = LoopEngine(task=args.task, config=config)
    try:
        engine.run()
    except FatalAgentError as exc:
        engine.abort_fatal(str(exc))
        run_dir = engine.persist(Path(args.out))
        metrics_path = _collect_run_metrics(engine, Path(args.out))
        print(f"Fatal: {exc}")
        print(f"  trace: {run_dir / 'trace.json'}")
        if metrics_path:
            print(f"  metrics: {metrics_path}")
        return 2
    run_dir = engine.persist(Path(args.out))
    metrics_path = _collect_run_metrics(engine, Path(args.out))
    print(f"Run {engine.run_id}: success={engine.success}")
    print(f"  state: {run_dir / 'state.json'}")
    print(f"  trace: {run_dir / 'trace.json'}")
    if metrics_path:
        print(f"  metrics: {metrics_path}")
    return 0 if engine.success else 1


def cmd_harness(args: argparse.Namespace) -> int:
    out_dir = Path(args.out)
    if args.reset_rollout:
        state_path = out_dir / "rollout-state.json"
        state = reset_rollout_state(
            load_rollout_state(state_path, fail_streak_limit=args.fail_streak_limit)
        )
        save_rollout_state(state_path, state)
        print(f"Rollout state reset: {state_path}")
        return 0

    if args.watch:
        state_path = out_dir / "rollout-state.json"
        state = load_rollout_state(state_path, fail_streak_limit=args.fail_streak_limit)
        state, report, summary = run_watch_cycle(
            state,
            candidate_version=args.prompt,
            gray_percent=args.gray_percent,
            guardrail_check=run_harness,
            eval_gate=(lambda: run_eval(baseline=args.eval_baseline))
            if args.promote_if_ready
            else None,
            promote_if_ready=args.promote_if_ready,
        )
        save_rollout_state(state_path, state)
        if report:
            write_harness_report(report, out_dir / "harness-report.json")
            metrics_path = _write_harness_metrics(report, out_dir)
        print(json.dumps({"rollout_state": state_path.name, "summary": summary}, indent=2))
        if report:
            print(json.dumps({"harness_report": report}, indent=2))
        print(f"  state:   {state_path}")
        print(f"  report:  {out_dir / 'harness-report.json'}")
        if report:
            print(f"  metrics: {metrics_path}")
        if state.get("version_locked"):
            return 2
        return 0 if summary.get("tick") in {"gray_ok", "rejected"} else 1

    report = run_harness(args.prompt, args.gray_percent)
    write_harness_report(report, out_dir / "harness-report.json")
    metrics_path = _write_harness_metrics(report, out_dir)
    print(json.dumps(report, indent=2))
    print(f"  metrics: {metrics_path}")
    return 0 if report["guardrail_ok"] else 1


def cmd_demo_no_output_hang(args: argparse.Namespace) -> int:
    """M2-I02 / Cline #8448: grep zero output → no completion signal → observe_stalled."""
    from m1_m2.tool_executor import ToolExecutor, _NO_OUTPUT_HANG_PATTERN
    from m1_m2.trace import TraceCollector

    trace = TraceCollector()
    executor = ToolExecutor(trace)

    pending = executor.call(
        "act",
        "grep",
        {
            "pattern": _NO_OUTPUT_HANG_PATTERN,
            "simulate_shell_integration_hang": True,
        },
    )

    stalled = executor.call(
        "act",
        "grep",
        {
            "pattern": _NO_OUTPUT_HANG_PATTERN,
            "simulate_shell_integration_hang": True,
            "observe_stalled": True,
            "idle_timeout_s": args.idle_timeout,
        },
    )

    run_dir = Path(args.out) / "m2-8448-demo"
    run_dir.mkdir(parents=True, exist_ok=True)
    trace.write(run_dir / "trace.json")
    state = {
        "issue": "Cline #8448",
        "pattern": _NO_OUTPUT_HANG_PATTERN,
        "event1_completion": pending.get("completion"),
        "event2_completion": stalled.get("completion"),
    }
    trace.write_state(run_dir / "state.json", state)

    print("M2 #8448 demo: no-output grep hang")
    print(f"  Event 1 (bug):   completion={pending.get('completion')!r}")
    print(f"  Event 2 (fix):   completion={stalled.get('completion')!r} error_class={stalled.get('error_class')!r}")
    print(f"  trace:  {run_dir / 'trace.json'}")
    print(f"  state:  {run_dir / 'state.json'}")
    return 0


def cmd_demo_allowlist(args: argparse.Namespace) -> int:
    """M2-I02: invoke a disallowed tool once; trace records allowlist reject."""
    from m1_m2.tool_executor import ToolExecutor
    from m1_m2.trace import TraceCollector

    trace = TraceCollector()
    executor = ToolExecutor(trace)
    result = executor.call("act", args.tool, {})
    run_dir = Path(args.out) / "m2-allowlist-demo"
    run_dir.mkdir(parents=True, exist_ok=True)
    trace.write(run_dir / "trace.json")
    allowlist_rejected = result.get("error") == "tool not in allowlist"
    print(f"Allowlist demo: tool={args.tool!r} rejected={allowlist_rejected}")
    print(json.dumps(result, indent=2))
    print(f"  trace: {run_dir / 'trace.json'}")
    print("  (Normal `cli.py run` only uses allowlisted tools - no rm_rf in loop trace.)")
    return 0 if allowlist_rejected else 1


def cmd_eval(args: argparse.Namespace) -> int:
    baseline_arg: float | str
    if args.baseline == "auto":
        baseline_arg = "auto"
    else:
        baseline_arg = float(args.baseline)
    out_dir = Path(args.out)
    report = run_eval(
        baseline=baseline_arg,
        enable_judge=args.enable_judge,
        evidence_dir=out_dir,
    )
    json_path, md_path = write_eval_report(report, out_dir)
    print(f"Success rate: {report['success_rate']:.1%} gate={'PASS' if report['gate_pass'] else 'FAIL'}")
    print(f"  baseline={report['baseline']} source={report.get('baseline_meta', {}).get('source')}")
    print(f"  {json_path}")
    print(f"  {md_path}")
    return 0 if report["gate_pass"] else 1


def main() -> None:
    _configure_stdio()
    parser = argparse.ArgumentParser(description="TrackARuntime - Track A anchor project")
    sub = parser.add_subparsers(dest="cmd", required=True)

    run_p = sub.add_parser("run", help="Run agent loop (M1+M2)")
    run_p.add_argument("--task", required=True)
    run_p.add_argument("--max-rounds", type=_max_rounds, default=3)
    run_p.add_argument(
        "--simulate-container-death",
        type=int,
        default=None,
        help="Kill container after round N (Issue #803 demo)",
    )
    run_p.add_argument(
        "--always-fail-tests",
        action="store_true",
        help="Tests never pass - stuck/pseudo-replan demos (Issue 3A/3B)",
    )
    run_p.add_argument(
        "--pseudo-replan",
        action="store_true",
        help="Freeze plan from round 2 - same tool args despite retryable obs (Issue 3B)",
    )
    run_p.add_argument(
        "--llm",
        choices=["mock"],
        default=None,
        help="Inject MockLLMClient for planning (default: hardcoded fallback)",
    )
    run_p.add_argument(
        "--checkpoint-dir",
        default=None,
        help="Directory for per-round checkpoint JSON (enables resume)",
    )
    run_p.add_argument(
        "--resume-from",
        default=None,
        help="Resume LoopEngine from a checkpoint JSON file",
    )
    run_p.add_argument(
        "--require-hitl",
        action="store_true",
        help="Dangerous tools (docker_exec) require confirmed=True",
    )
    run_p.add_argument("--max-retries", type=int, default=2)
    run_p.add_argument("--retry-backoff-s", type=float, default=0.05)
    run_p.add_argument("--out", default=str(M1_M2_EVIDENCE))

    demo_p = sub.add_parser(
        "demo-no-output-hang",
        help="M2-I02 / Cline #8448: grep zero output hang -> observe_stalled in trace",
    )
    demo_p.add_argument(
        "--idle-timeout",
        type=float,
        default=10.0,
        help="Idle seconds before observe_stalled closes the span (grep tier default)",
    )
    demo_p.add_argument("--out", default=str(M1_M2_EVIDENCE))

    allow_p = sub.add_parser(
        "demo-allowlist",
        help="M2-K01 optional: disallowed tool -> trace with fallback_used",
    )
    allow_p.add_argument(
        "--tool",
        default="rm_rf",
        help="Tool name to attempt (must NOT be in ToolExecutor.ALLOWLIST)",
    )
    allow_p.add_argument("--out", default=str(M1_M2_EVIDENCE))

    h_p = sub.add_parser("harness", help="Harness gray/rollback demo (M3)")
    h_p.add_argument("--prompt", choices=["v1", "v2"], default="v1")
    h_p.add_argument("--gray-percent", type=_gray_percent, default=0)
    h_p.add_argument(
        "--watch",
        action="store_true",
        help="M3-K04 L3: one rollout tick -> rollout-state.json + auto-rollback/lock",
    )
    h_p.add_argument(
        "--promote-if-ready",
        action="store_true",
        help="With --watch: promote candidate when guardrail OK and eval gate_pass",
    )
    h_p.add_argument(
        "--fail-streak-limit",
        type=int,
        default=3,
        help="Consecutive gray guardrail failures before locking candidate (default 3)",
    )
    h_p.add_argument(
        "--eval-baseline",
        type=_promote_baseline,
        default=DEFAULT_BASELINE,
        help=f"Eval gate baseline when --promote-if-ready (default {DEFAULT_BASELINE})",
    )
    h_p.add_argument(
        "--reset-rollout",
        action="store_true",
        help="Reset m3/evidence/rollout-state.json for demo replay",
    )
    h_p.add_argument("--out", default=str(M3_EVIDENCE))

    e_p = sub.add_parser("eval", help="Run 22-scenario benchmark (M4)")
    e_p.add_argument(
        "--baseline",
        type=_eval_baseline,
        default=str(DEFAULT_BASELINE),
        help="Gate baseline in [0, 1], or 'auto' to calibrate from historical report",
    )
    e_p.add_argument(
        "--enable-judge",
        action="store_true",
        help="Enable heuristic LLM-as-Judge sample (still offline)",
    )
    e_p.add_argument("--out", default=str(M4_EVIDENCE))

    args = parser.parse_args()
    if args.cmd == "run":
        raise SystemExit(cmd_run(args))
    if args.cmd == "demo-no-output-hang":
        raise SystemExit(cmd_demo_no_output_hang(args))
    if args.cmd == "demo-allowlist":
        raise SystemExit(cmd_demo_allowlist(args))
    if args.cmd == "harness":
        raise SystemExit(cmd_harness(args))
    if args.cmd == "eval":
        raise SystemExit(cmd_eval(args))


if __name__ == "__main__":
    main()
