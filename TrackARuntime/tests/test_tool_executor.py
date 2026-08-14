"""Unit tests for the M2 tool executor."""

from __future__ import annotations

import unittest

from m1_m2.errors import ErrorClass
from m1_m2.tool_executor import ToolExecutor, _NO_OUTPUT_HANG_PATTERN
from m1_m2.trace import TraceCollector


class TestToolExecutor(unittest.TestCase):
    def _make_executor(self, **kwargs) -> tuple[ToolExecutor, TraceCollector]:
        trace = TraceCollector()
        return ToolExecutor(trace, **kwargs), trace

    def test_allowlist_rejects_disallowed_tool(self) -> None:
        executor, trace = self._make_executor()
        result = executor.call("act", "rm_rf", {})
        self.assertEqual(result["error"], "tool not in allowlist")
        self.assertEqual(result["error_class"], ErrorClass.FATAL.value)
        self.assertTrue(trace.events[-1].fallback_used)

    def test_read_file_reads_existing_file(self) -> None:
        executor, _ = self._make_executor()
        result = executor.call("act", "read_file", {"path": "requirements.txt"})
        self.assertEqual(result["exit_code"], 0)
        self.assertIn("content", result)
        self.assertIn("pyyaml", result["content"].lower())

    def test_read_file_not_found(self) -> None:
        executor, _ = self._make_executor()
        result = executor.call("act", "read_file", {"path": "src/foo.py"})
        self.assertEqual(result["exit_code"], 1)
        self.assertIn("file not found", result["error"])

    def test_run_tests_passes_after_first_round(self) -> None:
        executor, _ = self._make_executor()
        r0 = executor.call("act", "run_tests", {"round": 0})
        self.assertEqual(r0["exit_code"], 1)
        r1 = executor.call("act", "run_tests", {"round": 1})
        self.assertEqual(r1["exit_code"], 0)

    def test_run_tests_always_fail_mode(self) -> None:
        executor, _ = self._make_executor(always_fail_tests=True)
        for round_idx in range(3):
            result = executor.call("act", "run_tests", {"round": round_idx})
            self.assertEqual(result["exit_code"], 1)

    def test_grep_normal_pattern(self) -> None:
        executor, _ = self._make_executor()
        result = executor.call("act", "grep", {"pattern": "hello"})
        self.assertEqual(result["matches"], ["hello"])
        self.assertEqual(result["completion"], "completed")

    def test_grep_no_output_hang_pending(self) -> None:
        executor, _ = self._make_executor()
        result = executor.call(
            "act",
            "grep",
            {"pattern": _NO_OUTPUT_HANG_PATTERN},
        )
        self.assertEqual(result["completion"], "pending")
        self.assertIsNone(result.get("error_class"))

    def test_grep_no_output_hang_stalled(self) -> None:
        executor, _ = self._make_executor()
        result = executor.call(
            "act",
            "grep",
            {
                "pattern": _NO_OUTPUT_HANG_PATTERN,
                "observe_stalled": True,
                "idle_timeout_s": 0.1,
            },
        )
        self.assertEqual(result["completion"], "stalled")
        self.assertEqual(result["error_class"], ErrorClass.STALLED.value)


if __name__ == "__main__":
    unittest.main()
