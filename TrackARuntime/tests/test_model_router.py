"""Unit tests for model router."""

from __future__ import annotations

import unittest

from m3.model_router import ModelRouter


class TestModelRouter(unittest.TestCase):
    def test_simple_task_routes_small(self) -> None:
        decision = ModelRouter().route("fix typo")
        self.assertEqual(decision.tier, "simple")
        self.assertEqual(decision.model, "mock-small")

    def test_complex_task_routes_large(self) -> None:
        decision = ModelRouter().route("refactor entire architecture")
        self.assertEqual(decision.tier, "complex")
        self.assertEqual(decision.model, "mock-large")
        self.assertEqual(decision.fallback, "mock-small")


if __name__ == "__main__":
    unittest.main()
