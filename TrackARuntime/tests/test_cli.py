"""CLI 契约：默认门槛、输入校验、allowlist 演示退出码。"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestCli(unittest.TestCase):
    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / "cli.py"), *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def test_eval_without_baseline_uses_ci_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proc = self._run("eval", "--out", tmp)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)
        self.assertIn("baseline=0.45", proc.stdout)
        self.assertIn("gate=PASS", proc.stdout)

    def test_invalid_baseline_is_usage_error(self) -> None:
        for value in ("notanumber", "-1", "1.5"):
            with self.subTest(value=value):
                proc = self._run("eval", "--baseline", value)
                self.assertEqual(proc.returncode, 2, proc.stderr)
                self.assertNotIn("Traceback", proc.stderr)
                self.assertIn("baseline", proc.stderr)

    def test_gray_percent_must_be_0_to_100(self) -> None:
        for value in ("-1", "101"):
            with self.subTest(value=value):
                proc = self._run("harness", "--gray-percent", value)
                self.assertEqual(proc.returncode, 2, proc.stderr)
                self.assertNotIn("Traceback", proc.stderr)
                self.assertIn("gray-percent", proc.stderr)

    def test_blank_task_and_non_positive_rounds_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for args in (
                ("run", "--task", "", "--out", tmp),
                ("run", "--task", "   ", "--out", tmp),
                ("run", "--task", "x", "--max-rounds", "0", "--out", tmp),
                ("run", "--task", "x", "--max-rounds", "-1", "--out", tmp),
            ):
                with self.subTest(args=args):
                    proc = self._run(*args)
                    self.assertEqual(proc.returncode, 2, proc.stderr)
                    self.assertNotIn("Traceback", proc.stderr)

    def test_missing_or_corrupt_checkpoint_is_fatal_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = self._run(
                "run",
                "--task",
                "x",
                "--resume-from",
                str(Path(tmp) / "missing.json"),
                "--out",
                tmp,
            )
            self.assertEqual(missing.returncode, 2, missing.stderr)
            self.assertNotIn("Traceback", missing.stderr)
            self.assertIn("checkpoint not found", missing.stderr)

            bad = Path(tmp) / "bad.json"
            bad.write_text("{not json", encoding="utf-8")
            corrupt = self._run(
                "run",
                "--task",
                "x",
                "--resume-from",
                str(bad),
                "--out",
                tmp,
            )
            self.assertEqual(corrupt.returncode, 2, corrupt.stderr)
            self.assertNotIn("Traceback", corrupt.stderr)
            self.assertIn("not valid JSON", corrupt.stderr)

    def test_allowlist_demo_only_succeeds_on_allowlist_reject(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            denied = self._run("demo-allowlist", "--tool", "rm_rf", "--out", tmp)
            self.assertEqual(denied.returncode, 0, denied.stderr)
            self.assertIn("rejected=True", denied.stdout)
            self.assertIn("tool not in allowlist", denied.stdout)

            schema = self._run("demo-allowlist", "--tool", "read_file", "--out", tmp)
            self.assertEqual(schema.returncode, 1, schema.stderr)
            self.assertIn("rejected=False", schema.stdout)
            self.assertIn("missing required field: path", schema.stdout)

    def test_promote_if_ready_uses_ci_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proc = self._run(
                "harness",
                "--prompt",
                "v1",
                "--gray-percent",
                "0",
                "--watch",
                "--promote-if-ready",
                "--out",
                tmp,
            )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        summary = json.loads(proc.stdout.split("\n{\n  \"harness_report\"")[0])
        self.assertEqual(summary["summary"]["promote"], "done")
        self.assertTrue(summary["summary"]["eval_gate_pass"])


if __name__ == "__main__":
    unittest.main()
