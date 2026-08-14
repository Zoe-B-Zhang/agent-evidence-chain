"""Unit tests for token counter and cost monitor."""

from __future__ import annotations

import unittest

from m3.cost_monitor import CostMonitor
from m3.token_counter import estimate_prompt_tokens, estimate_tokens


class TestTokenCounter(unittest.TestCase):
    def test_empty_is_zero(self) -> None:
        self.assertEqual(estimate_tokens(""), 0)

    def test_nonempty_positive(self) -> None:
        self.assertGreater(estimate_tokens("hello world"), 0)

    def test_prompt_sums_parts(self) -> None:
        total = estimate_prompt_tokens("sys", "user text here")
        self.assertEqual(total, estimate_tokens("sys") + estimate_tokens("user text here"))


class TestCostMonitor(unittest.TestCase):
    def test_records_cost(self) -> None:
        mon = CostMonitor()
        est = mon.record(input_tokens=1000, output_tokens=500, model="mock-small")
        self.assertGreater(est.cost_usd, 0)
        self.assertEqual(mon.summary()["calls"], 1)
        self.assertEqual(mon.summary()["total_input_tokens"], 1000)


if __name__ == "__main__":
    unittest.main()
