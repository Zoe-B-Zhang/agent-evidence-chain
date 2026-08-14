"""Unit tests for context manager."""

from __future__ import annotations

import unittest

from m1_m2.context_manager import ContextManager


class TestContextManager(unittest.TestCase):
    def test_build_four_layers(self) -> None:
        cm = ContextManager()
        layers = cm.build(
            task="fix failing test",
            observation="1 failed",
            history=[{"round": 1, "phase": "plan", "detail": "patch"}],
            plan="replan",
        )
        self.assertIn("coding agent", layers.system)
        self.assertIn("fix failing test", layers.long_term)
        self.assertIn("plan", layers.short_term)
        self.assertIn("1 failed", layers.current)

    def test_render_truncates(self) -> None:
        cm = ContextManager(max_chars=80)
        cm.build(task="x" * 200, observation="y" * 200, history=[], plan="z")
        rendered = cm.as_prompt()
        self.assertLessEqual(len(rendered), 80)


if __name__ == "__main__":
    unittest.main()
