"""Unit tests for trace_eval."""

from __future__ import annotations

import unittest

from m4.trace_eval import evaluate_trace


class TestTraceEval(unittest.TestCase):
    def test_empty_trace(self) -> None:
        report = evaluate_trace([])
        self.assertEqual(report["total_events"], 0)
        self.assertEqual(report["fallback_rate"], 0.0)

    def test_detects_duplicates_and_fallback(self) -> None:
        events = [
            {
                "tool": "docker_exec",
                "input": {"command": "x"},
                "fallback_used": False,
                "error_class": None,
            },
            {
                "tool": "docker_exec",
                "input": {"command": "x"},
                "fallback_used": True,
                "error_class": "retryable",
            },
            {
                "tool": "grep",
                "input": {"pattern": "a"},
                "fallback_used": True,
                "error_class": "stalled",
            },
        ]
        report = evaluate_trace(events)
        self.assertEqual(report["total_events"], 3)
        self.assertGreaterEqual(report["fingerprint_duplicates"], 1)
        self.assertEqual(report["max_fingerprint_repeats"], 2)
        self.assertEqual(report["retry_count"], 1)
        self.assertEqual(report["stalled_count"], 1)
        self.assertAlmostEqual(report["fallback_rate"], 2 / 3, places=3)


if __name__ == "__main__":
    unittest.main()
