import polars as pl
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationResult:
    passed: bool
    check: str
    column: str | list[str] | None = None
    statistics: dict[str, Any] = field(default_factory=dict)
    violations: int = 0
    message: str = ""


class NotNull:
    def __init__(self, column: str):
        self.column = column

    def run(self, data: pl.DataFrame) -> ValidationResult:
        null_count = data.select(pl.col(self.column).null_count()).item()
        return ValidationResult(
            passed=(null_count == 0),
            check="NotNull",
            column=self.column,
            statistics={
                "null_count": null_count,
                "null_ratio": (null_count / data.height) * 100 if data.height > 0 else 0.0,
            },
            violations=null_count,
            message=f"Column '{self.column}' has {null_count} null values",
        )
