"""Golden dataset 加载与校验（D4）。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REQUIRED_SCENARIO_KEYS = {"id", "task", "expect"}
VALID_EXPECT = {"pass", "fail"}
VALID_CATEGORIES = {"retrieval", "generation", "mixed"}


def load_golden_dataset(path: Path | None = None) -> dict[str, Any]:
    """加载 scenarios.json 并校验版本与字段。"""
    path = path or Path(__file__).parent / "scenarios.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_dataset(data)
    if errors:
        raise ValueError("golden dataset validation failed:\n- " + "\n- ".join(errors))
    return data


def validate_dataset(data: dict[str, Any]) -> list[str]:
    """返回校验错误列表；空列表表示通过。"""
    errors: list[str] = []
    if "version" not in data:
        errors.append("missing top-level 'version' field")
    elif not isinstance(data["version"], int):
        errors.append("'version' must be an integer")

    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        errors.append("'scenarios' must be a non-empty list")
        return errors

    seen_ids: set[str] = set()
    for i, s in enumerate(scenarios):
        if not isinstance(s, dict):
            errors.append(f"scenario[{i}] is not an object")
            continue
        missing = REQUIRED_SCENARIO_KEYS - set(s)
        if missing:
            errors.append(f"scenario[{i}] missing keys: {sorted(missing)}")
        expect = s.get("expect")
        if expect not in VALID_EXPECT:
            errors.append(f"scenario[{i}] invalid expect: {expect!r}")
        sid = s.get("id")
        if sid in seen_ids:
            errors.append(f"duplicate scenario id: {sid}")
        if sid:
            seen_ids.add(sid)
        if expect == "fail" and not s.get("failure_code"):
            errors.append(f"scenario[{i}] ({sid}) expect=fail but no failure_code")
        cat = s.get("category")
        if cat is not None and cat not in VALID_CATEGORIES:
            errors.append(f"scenario[{i}] invalid category: {cat!r}")
    return errors
