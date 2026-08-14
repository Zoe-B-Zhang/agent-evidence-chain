"""Unit tests for baseline calibration."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from m4.baseline import DEFAULT_BASELINE, resolve_baseline


class TestBaseline(unittest.TestCase):
    def test_explicit_baseline(self) -> None:
        info = resolve_baseline(0.7)
        self.assertEqual(info["baseline"], 0.7)
        self.assertEqual(info["source"], "explicit")

    def test_auto_without_history_falls_back(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            info = resolve_baseline("auto", evidence_dir=Path(tmp))
            self.assertEqual(info["baseline"], DEFAULT_BASELINE)
            self.assertEqual(info["source"], "default_fallback")

    def test_auto_uses_historical_rate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evaluation-report.json"
            path.write_text(json.dumps({"success_rate": 0.6}), encoding="utf-8")
            info = resolve_baseline("auto", evidence_dir=Path(tmp))
            self.assertEqual(info["baseline"], 0.6)
            self.assertEqual(info["source"], "historical_success_rate")


if __name__ == "__main__":
    unittest.main()
