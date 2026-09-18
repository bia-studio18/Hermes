from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Change:

    rule: str
    field: str | None = None
    old_value: Any = None
    new_value: Any = None
    record: int | str | None = None
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule": self.rule,
            "field": self.field,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "record": self.record,
            "reason": self.reason,
        }


@dataclass(slots=True)
class RuleResult:

    rule: str
    success: bool = True

    changes: list[Change] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    statistics: dict[str, Any] = field(default_factory=dict)

    @property
    def total_changes(self) -> int:
        return len(self.changes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule": self.rule,
            "success": self.success,
            "changes": [
                change.to_dict()
                for change in self.changes
            ],
            "errors": self.errors,
            "warnings": self.warnings,
            "statistics": self.statistics,
            "total_changes": self.total_changes,
        }

    def summary(self) -> str:
        return (
            f"{self.rule}: "
            f"{'success' if self.success else 'failed'}, "
            f"{self.total_changes} changes"
        )



@dataclass(slots=True)
class NormalizationResult:
    data: Any

    success: bool = True

    rules: list[str] = field(default_factory=list)

    changes: int = 0

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "data": self.data,
            "success": self.success,
            "rules": self.rules,
            "changes": self.changes,
            "errors": self.errors,
            "warnings": self.warnings,
        }

    def summary(self) -> str:
        return (
            f"Normalization "
            f"{'successful' if self.success else 'failed'}: "
            f"{len(self.rules)} rules, "
            f"{self.changes} changes, "
            f"{len(self.errors)} errors, "
            f"{len(self.warnings)} warnings"
        )