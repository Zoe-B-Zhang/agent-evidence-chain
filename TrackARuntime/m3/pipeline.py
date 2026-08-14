"""Harness: prompt version, gray release, rollback (M3)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from m3.guardrails import check_formality

MOCK_OUTPUTS = {
    "v1": "The route has been updated. Please review the changes.",
    "v2": "Amazing!!! This exciting route is awesome!!!",
}


def load_prompt(version: str) -> dict[str, Any]:
    path = Path(__file__).parent / "prompts" / f"{version}.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def run_harness(version: str, gray_percent: int) -> dict[str, Any]:
    prompt = load_prompt(version)
    output = MOCK_OUTPUTS[version]
    ok, score, msg = check_formality(output, prompt.get("style_formality_min", 0.7))
    report: dict[str, Any] = {
        "prompt_version": version,
        "gray_percent": gray_percent,
        "output": output,
        "guardrail_ok": ok,
        "formality_score": score,
        "message": msg,
        "action": "promote" if ok else "rollback_to_v1",
    }
    if not ok and gray_percent > 0:
        report["rollback_reason"] = "guardrail_failed_during_gray"
    return report


def write_harness_report(report: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
