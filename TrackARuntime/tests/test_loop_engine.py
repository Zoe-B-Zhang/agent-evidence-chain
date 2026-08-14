"""Unit tests for the M1/M2 loop engine."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from m1_m2.errors import FatalAgentError
from m1_m2.llm_client import MockLLMClient
from m1_m2.loop_engine import LoopConfig, LoopEngine, _PSEUDO_REPLAN_PLAN


class TestLoopEngine(unittest.TestCase):
    def test_successful_run(self) -> None:
        engine = LoopEngine(task="fix failing test")
        engine.run()
        self.assertTrue(engine.success)
        self.assertEqual(engine.round, 2)
        self.assertIn("Task completed", [h["detail"] for h in engine.history])

    def test_container_death_raises_fatal(self) -> None:
        config = LoopConfig(simulate_container_death_after_round=1)
        engine = LoopEngine(task="container death", config=config)
        with self.assertRaises(FatalAgentError):
            engine.run()
        self.assertFalse(engine.success)
        fatal_events = [
            e for e in engine.trace.events if e.error_class == "fatal"
        ]
        self.assertTrue(fatal_events)

    def test_fingerprint_detects_stuck_loop(self) -> None:
        config = LoopConfig(
            max_rounds=5,
            always_fail_tests=True,
            pseudo_replan=True,
        )
        engine = LoopEngine(task="stuck loop", config=config)
        with self.assertRaises(FatalAgentError) as ctx:
            engine.run()
        self.assertIn("Loop fingerprint detected", str(ctx.exception))

    def test_pseudo_replan_freezes_plan(self) -> None:
        config = LoopConfig(pseudo_replan=True, max_rounds=3)
        engine = LoopEngine(task="pseudo replan", config=config)
        engine.run()
        plans = [
            h["detail"]
            for h in engine.history
            if h["phase"] == "plan"
        ]
        self.assertGreater(len(plans), 1)
        self.assertEqual(plans[0], "Apply minimal patch without reading test output")
        for plan in plans[1:]:
            self.assertEqual(plan, _PSEUDO_REPLAN_PLAN)

    def test_tool_executor_receives_hitl_and_retry_config(self) -> None:
        """B1: __post_init__ must forward require_hitl / max_retries / backoff."""
        config = LoopConfig(
            require_hitl=True,
            max_retries=5,
            retry_backoff_s=0.2,
        )
        engine = LoopEngine(task="cfg", config=config)
        self.assertTrue(engine.tools._require_hitl)
        self.assertEqual(engine.tools._max_retries, 5)
        self.assertEqual(engine.tools._retry_backoff_s, 0.2)

    def test_mock_llm_client_injection(self) -> None:
        config = LoopConfig(llm_client=MockLLMClient())
        engine = LoopEngine(task="fix failing test", config=config)
        engine.run()
        self.assertTrue(engine.success)

    def test_hitl_blocks_docker_exec(self) -> None:
        config = LoopConfig(require_hitl=True)
        engine = LoopEngine(task="hitl demo", config=config)
        with self.assertRaises(FatalAgentError) as ctx:
            engine.run()
        self.assertIn("HITL", str(ctx.exception))

    def test_checkpoint_and_resume_preserves_tool_executor_params(self) -> None:
        """B1: resume_from must rebuild ToolExecutor with same HITL/retry settings."""
        with tempfile.TemporaryDirectory() as tmp:
            ckpt_dir = Path(tmp)
            config = LoopConfig(
                max_rounds=2,
                always_fail_tests=True,
                checkpoint_dir=ckpt_dir,
                require_hitl=False,
                max_retries=4,
                retry_backoff_s=0.12,
            )
            engine = LoopEngine(task="checkpoint demo", config=config)
            engine.run()
            ckpt_path = ckpt_dir / f"{engine.run_id}.json"
            self.assertTrue(ckpt_path.exists())

            resumed = LoopEngine.resume_from(ckpt_path)
            self.assertEqual(resumed.run_id, engine.run_id)
            self.assertEqual(resumed.round, 2)
            self.assertEqual(resumed.task, "checkpoint demo")
            self.assertFalse(resumed.success)
            self.assertEqual(resumed.tools._max_retries, 4)
            self.assertEqual(resumed.tools._retry_backoff_s, 0.12)
            self.assertFalse(resumed.tools._require_hitl)
            self.assertTrue(resumed.tools._always_fail_tests)

    def test_plan_routes_model_and_records_cost(self) -> None:
        """Phase C: context + router run before plan; cost_monitor accumulates."""
        client = MockLLMClient()
        config = LoopConfig(llm_client=client, max_rounds=2)
        engine = LoopEngine(task="refactor entire architecture", config=config)
        engine.run()
        self.assertTrue(engine.route_decisions)
        self.assertEqual(engine.route_decisions[0]["tier"], "complex")
        self.assertEqual(client.last_model, "mock-large")
        self.assertGreater(engine.cost_monitor.total_input_tokens, 0)
        self.assertGreater(len(engine.last_context_prompt), 0)


if __name__ == "__main__":
    unittest.main()
