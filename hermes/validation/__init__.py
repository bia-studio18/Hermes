"""Hermes validation subsystem.

Rules observe data and report whether it satisfies conditions; they never
modify the data.
"""

from hermes.validation.context import ValidationContext
from hermes.validation.engine import ValidationEngine, validate
from hermes.validation.errors import (
    RuleConfigurationError,
    RuleExecutionError,
    ValidationError,
)
from hermes.validation.result import RuleResult, ValidationResult, Violation
from hermes.validation.rule import ValidationRule
from hermes.validation.rules import (
    CardinalityCheck,
    ColumnCheck,
    CompletenessCheck,
    ConstantCheck,
    DateOrderCheck,
    DateRangeCheck,
    DuplicateCheck,
    EnumCheck,
    ForeignKeyCheck,
    FreshnessCheck,
    LengthCheck,
    NotNull,
    NullRateCheck,
    PatternCheck,
    RangeCheck,
    ReferentialCheck,
    RegexCheck,
    RowCountCheck,
    SchemaCheck,
    TypeCheck,
    Unique,
    UniqueCombination,
    register_pattern,
)

__all__ = [
    "validate",
    "ValidationEngine",
    "ValidationRule",
    "ValidationContext",
    "ValidationResult",
    "RuleResult",
    "Violation",
    "ValidationError",
    "RuleConfigurationError",
    "RuleExecutionError",
    # Rules
    "NotNull",
    "Unique",
    "UniqueCombination",
    "TypeCheck",
    "RangeCheck",
    "EnumCheck",
    "RegexCheck",
    "LengthCheck",
    "DateRangeCheck",
    "DateOrderCheck",
    "SchemaCheck",
    "RowCountCheck",
    "ColumnCheck",
    "NullRateCheck",
    "DuplicateCheck",
    "FreshnessCheck",
    "CompletenessCheck",
    "ReferentialCheck",
    "ForeignKeyCheck",
    "PatternCheck",
    "ConstantCheck",
    "CardinalityCheck",
    "register_pattern",
]
