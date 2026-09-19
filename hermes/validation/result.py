"""Validation result dataclasses.

The canonical representation is a Python dataclass; ``to_dict()`` produces a
JSON-serializable view where practical.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Violation:
    """A single offending value found by a rule."""

    field: str
    row: int | None = None
    value: Any = None
    expected: Any = None
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "field": self.field,
            "row": self.row,
            "value": _json_safe(self.value),
            "expected": _json_safe(self.expected),
            "message": self.message,
        }


@dataclass(slots=True)
class RuleResult:
    """Outcome of a single rule."""

    rule: str
    passed: bool
    statistics: dict[str, Any] = field(default_factory=dict)
    violations: list[Violation] = field(default_factory=list)
    message: str = ""
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule": self.rule,
            "passed": self.passed,
            "statistics": _json_safe(self.statistics),
            "violations": [v.to_dict() for v in self.violations],
            "message": self.message,
            "warnings": self.warnings,
        }

    def summary(self) -> str:
        return f"{self.rule}: {'passed' if self.passed else 'FAILED'} - {self.message}"


@dataclass(slots=True)
class ValidationResult:
    """Aggregate outcome of a validation run.

    ``success`` means the validation process itself completed without engine
    errors. ``passed`` means every rule passed and there were no engine errors.
    """

    success: bool = True
    passed: bool = True
    results: list[RuleResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "passed": self.passed,
            "results": [r.to_dict() for r in self.results],
            "errors": self.errors,
            "warnings": self.warnings,
        }

    def summary(self) -> str:
        total = len(self.results)
        passed_count = sum(1 for r in self.results if r.passed)
        failed_count = total - passed_count
        status = "PASSED" if self.passed else ("FAILED" if self.success else "ERROR")
        lines = [
            f"Validation {status}",
            f"  rules: {total}, passed: {passed_count}, failed: {failed_count}",
            f"  errors: {len(self.errors)}, warnings: {len(self.warnings)}",
        ]
        for result in self.results:
            lines.append(f"  {'ok ' if result.passed else 'FAIL'} {result.summary()}")
        return "\n".join(lines)

    def __bool__(self) -> bool:
        return self.passed


def _json_safe(value: Any) -> Any:
    import datetime

    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return value.isoformat()
    return value


__all__ = ["Violation", "RuleResult", "ValidationResult"]
