"""Unit tests for the pluggable LLM client."""

from __future__ import annotations

import unittest

from m1_m2.llm_client import MockLLMClient, PlanContext
from m1_m2.loop_engine import _PSEUDO_REPLAN_PLAN


class TestMockLLMClient(unittest.TestCase):
    def test_first_round_plan(self) -> None:
        client = MockLLMClient()
        plan = client.generate_plan(PlanContext(task="fix", round=1))
        self.assertEqual(plan, "Apply minimal patch without reading test output")

    def test_replan_uses_observation(self) -> None:
        client = MockLLMClient()
        plan = client.generate_plan(
            PlanContext(task="fix", observation="1 failed", round=2)
        )
        self.assertIn("1 failed", plan)
        self.assertIn("Replan using observation", plan)

    def test_pseudo_replan_freezes_plan(self) -> None:
        client = MockLLMClient()
        plan = client.generate_plan(
            PlanContext(task="stuck", round=2, pseudo_replan=True)
        )
        self.assertEqual(plan, _PSEUDO_REPLAN_PLAN)


if __name__ == "__main__":
    unittest.main()
