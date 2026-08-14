"""Tool executor with allowlist, schema validation, timeout tiers and retry (M2 + D1)."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from m1_m2.errors import ErrorClass
from m1_m2.trace import TraceCollector

# Reproduction pattern from Cline #8448 (grep with no matches → zero output → hang).
_NO_OUTPUT_HANG_PATTERN = "ABCDEFGH0193746458"

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class ToolSpec:
    """Specification for an allowlisted tool."""

    name: str
    description: str
    schema: dict[str, Any] = field(default_factory=dict)
    handler: Callable[[dict], dict] | None = None
    read_only: bool = False
    dangerous: bool = False


def _type_check(value: Any, expected: str) -> bool:
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "array":
        return isinstance(value, list)
    return True


def validate_schema(payload: dict[str, Any], schema: dict[str, Any]) -> tuple[bool, str]:
    """Minimal JSON-Schema-like validator for required fields and basic types."""
    required = schema.get("required", [])
    properties = schema.get("properties", {})
    for key in required:
        if key not in payload:
            return False, f"missing required field: {key}"
    for key, value in payload.items():
        prop = properties.get(key, {})
        expected = prop.get("type")
        if expected and not _type_check(value, expected):
            return False, f"field {key} expects {expected}, got {type(value).__name__}"
    return True, ""


def _read_file_handler(payload: dict[str, Any]) -> dict[str, Any]:
    """Read a file relative to the project root (read-only sandbox)."""
    raw_path = payload.get("path", "")
    target = (ROOT / raw_path).resolve()
    # Sandbox: only allow reading inside the project root.
    if not str(target).startswith(str(ROOT)):
        return {
            "error": "path outside project sandbox",
            "error_class": ErrorClass.RECOVERABLE.value,
            "exit_code": 1,
        }
    if not target.exists():
        return {
            "error": f"file not found: {raw_path}",
            "error_class": ErrorClass.RECOVERABLE.value,
            "exit_code": 1,
        }
    try:
        lines = target.read_text(encoding="utf-8").splitlines()
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "error": f"read failed: {exc}",
            "error_class": ErrorClass.RECOVERABLE.value,
            "exit_code": 1,
        }
    offset = int(payload.get("offset", 0))
    limit = payload.get("limit")
    if limit is not None:
        limit = int(limit)
    selected = lines[offset:] if limit is None else lines[offset : offset + limit]
    return {
        "path": str(target.relative_to(ROOT)),
        "content": "\n".join(selected),
        "lines_read": len(selected),
        "total_lines": len(lines),
        "offset": offset,
        "exit_code": 0,
    }


def _grep_handler(payload: dict[str, Any]) -> dict[str, Any]:
    """Search for a pattern in a file or return a deterministic mock match."""
    pattern = payload.get("pattern", "")
    if payload.get("simulate_shell_integration_hang") or pattern == _NO_OUTPUT_HANG_PATTERN:
        return _grep_no_output_hang(payload)

    path = payload.get("path")
    if path:
        target = (ROOT / path).resolve()
        if not str(target).startswith(str(ROOT)) or not target.exists():
            return {
                "matches": [],
                "stdout": "",
                "exit_code": 1,
                "error": f"path not found or outside sandbox: {path}",
                "error_class": ErrorClass.RECOVERABLE.value,
            }
        text = target.read_text(encoding="utf-8")
        matches = [line for line in text.splitlines() if pattern in line]
        return {
            "pattern": pattern,
            "path": str(target.relative_to(ROOT)),
            "matches": matches,
            "stdout": "\n".join(matches),
            "exit_code": 0 if matches else 1,
            "completion": "completed",
        }

    return {
        "matches": [pattern] if pattern else [],
        "stdout": pattern,
        "exit_code": 0,
        "completion": "completed",
    }


def _grep_no_output_hang(payload: dict[str, Any]) -> dict[str, Any]:
    """Simulate Cline #8448: zero stdout, shell integration never signals completion."""
    idle_s = float(payload.get("idle_timeout_s", 10.0))
    if payload.get("observe_stalled"):
        return {
            "matches": [],
            "stdout": "",
            "exit_code": 1,
            "completion": "stalled",
            "message": (
                f"observe_stalled: no completion signal after {idle_s}s idle "
                "(grep exited with no output; #8448)"
            ),
            "error_class": ErrorClass.STALLED.value,
        }
    return {
        "matches": [],
        "stdout": "",
        "completion": "pending",
        "message": "waiting for shell integration completion signal (never arrives on zero output)",
        "error_class": None,
    }


# Static tool metadata (descriptions + schemas).  Handlers for stateful tools are
# bound in ToolExecutor.__init__ so they can access instance state.
BASE_TOOL_SPECS: dict[str, ToolSpec] = {
    "read_file": ToolSpec(
        name="read_file",
        description="Read a text file from the project (read-only, sandboxed).",
        schema={
            "required": ["path"],
            "properties": {
                "path": {"type": "string"},
                "offset": {"type": "integer"},
                "limit": {"type": "integer"},
            },
        },
        handler=_read_file_handler,
        read_only=True,
    ),
    "grep": ToolSpec(
        name="grep",
        description="Search for a pattern in a file or return a mock match.",
        schema={
            "required": ["pattern"],
            "properties": {
                "pattern": {"type": "string"},
                "path": {"type": "string"},
                "simulate_shell_integration_hang": {"type": "boolean"},
                "observe_stalled": {"type": "boolean"},
                "idle_timeout_s": {"type": "number"},
            },
        },
        handler=_grep_handler,
        read_only=True,
    ),
    "run_tests": ToolSpec(
        name="run_tests",
        description="Run the test suite and report pass/fail.",
        schema={
            "required": ["round"],
            "properties": {
                "round": {"type": "integer"},
                "force_retryable": {"type": "boolean"},
            },
        },
        read_only=True,
    ),
    "docker_exec": ToolSpec(
        name="docker_exec",
        description="Execute a command in the (mock) container. Dangerous without HITL.",
        schema={
            "required": ["command"],
            "properties": {
                "command": {"type": "string"},
                "confirmed": {"type": "boolean"},
            },
        },
        dangerous=True,
    ),
}


class ToolExecutor:
    ALLOWLIST = frozenset(BASE_TOOL_SPECS.keys())

    def __init__(
        self,
        trace: TraceCollector,
        timeouts: dict[str, float] | None = None,
        *,
        always_fail_tests: bool = False,
        max_retries: int = 2,
        retry_backoff_s: float = 0.05,
        require_hitl: bool = False,
    ) -> None:
        self._trace = trace
        self._always_fail_tests = always_fail_tests
        self._max_retries = max_retries
        self._retry_backoff_s = retry_backoff_s
        self._require_hitl = require_hitl
        self._timeouts = timeouts or {
            "run_tests": 120.0,
            "read_file": 5.0,
            "grep": 10.0,
            "docker_exec": 30.0,
        }
        self._container_alive = True
        self._specs = {name: ToolSpec(**spec.__dict__) for name, spec in BASE_TOOL_SPECS.items()}
        # Bind stateful handlers.
        self._specs["run_tests"].handler = self._run_tests
        self._specs["docker_exec"].handler = self._docker_exec

    def kill_container(self) -> None:
        """Simulate container_timeout expiry (Issue #803)."""
        self._container_alive = False

    def _run_tests(self, payload: dict[str, Any]) -> dict[str, Any]:
        if payload.get("force_retryable"):
            return {
                "exit_code": -1,
                "summary": "transient test runner error",
                "error_class": ErrorClass.RETRYABLE.value,
            }
        if self._always_fail_tests:
            return {
                "exit_code": 1,
                "summary": "pytest: 1 failed — AssertionError in test_handler",
            }
        round_idx = payload.get("round", 0)
        if round_idx == 0:
            return {"exit_code": 1, "summary": "pytest: 1 failed — AssertionError in test_handler"}
        return {"exit_code": 0, "summary": "pytest: 1 passed"}

    def _docker_exec(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not self._container_alive:
            return {
                "returncode": -1,
                "stdout": "Error: No such container: container is not running",
                "error_class": ErrorClass.FATAL.value,
            }
        return {"returncode": 0, "stdout": payload.get("command", "")}

    def call(self, step: str, tool: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}
        if tool not in self.ALLOWLIST:
            self._trace.record(
                step,
                tool,
                payload,
                {"error": "tool not in allowlist"},
                0,
                fallback_used=True,
                error_class=ErrorClass.FATAL.value,
            )
            return {"error": "tool not in allowlist", "error_class": ErrorClass.FATAL.value}

        spec = self._specs[tool]

        # Schema validation.
        ok, err = validate_schema(payload, spec.schema)
        if not ok:
            self._trace.record(
                step,
                tool,
                payload,
                {"error": err},
                0,
                fallback_used=True,
                error_class=ErrorClass.RECOVERABLE.value,
            )
            return {"error": err, "error_class": ErrorClass.RECOVERABLE.value}

        # HITL for dangerous tools.
        if self._require_hitl and spec.dangerous and not payload.get("confirmed"):
            msg = f"dangerous tool {tool} requires confirmed=True (HITL)"
            self._trace.record(
                step,
                tool,
                payload,
                {"error": msg},
                0,
                fallback_used=True,
                error_class=ErrorClass.FATAL.value,
            )
            return {"error": msg, "error_class": ErrorClass.FATAL.value}

        # Execute with retry for RETRYABLE errors.
        start = time.perf_counter()
        attempt = 0
        out: dict[str, Any] = {}
        while True:
            handler = spec.handler
            if handler is None:
                raise RuntimeError(f"tool {tool} has no bound handler")
            out = handler(payload)
            error_class = out.get("error_class")
            if error_class != ErrorClass.RETRYABLE.value or attempt >= self._max_retries:
                break
            attempt += 1
            time.sleep(self._retry_backoff_s * (2**attempt))

        elapsed = int((time.perf_counter() - start) * 1000)
        completion = out.get("completion", "completed")
        fallback = bool(out.get("error")) or completion == "stalled"
        if completion == "stalled":
            fallback = True
            error_class = error_class or ErrorClass.STALLED.value
        self._trace.record(
            step,
            tool,
            payload,
            out,
            elapsed,
            fallback_used=fallback,
            error_class=error_class,
        )
        return out
