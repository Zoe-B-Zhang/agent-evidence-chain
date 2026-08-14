"""Unit tests for the M4 eval runner."""

from __future__ import annotations

import unittest

from m4.golden_dataset import load_golden_dataset, validate_dataset
from m4.runner import run_eval


class TestRunner(unittest.TestCase):
    def test_eval_report_structure(self) -> None:
        report = run_eval(baseline=0.45)
        self.assertEqual(report["total"], 22)
        self.assertEqual(report["successes"], 10)
        self.assertEqual(report["success_rate"], 0.455)
        self.assertTrue(report["gate_pass"])
        self.assertIn("failure_distribution", report)
        self.assertIn("remediation_advice", report)
        self.assertIn("category_split", report)
        self.assertIn("p95_latency_ms", report)
        self.assertIn("results", report)
        self.assertEqual(report["dataset_version"], 1)

    def test_eval_gate_can_fail(self) -> None:
        report = run_eval(baseline=0.9)
        self.assertFalse(report["gate_pass"])

    def test_failure_distribution_counts_all_failures(self) -> None:
        report = run_eval(baseline=0.5)
        failures = report["failure_distribution"]
        self.assertEqual(sum(failures.values()), report["total"] - report["successes"])

    def test_category_split_present(self) -> None:
        report = run_eval(baseline=0.5)
        split = report["category_split"]
        self.assertIn("retrieval", split)
        self.assertIn("generation", split)
        total = sum(v["total"] for v in split.values())
        self.assertEqual(total, 22)

    def test_golden_dataset_validates(self) -> None:
        data = load_golden_dataset()
        self.assertEqual(validate_dataset(data), [])

    def test_remediation_reads_taxonomy_file(self) -> None:
        report = run_eval(baseline=0.5)
        tip = report["remediation_advice"].get("RETRIEVAL_MISS", "")
        self.assertIn("检索", tip)
        self.assertIn("检测信号", tip)


if __name__ == "__main__":
    unittest.main()
