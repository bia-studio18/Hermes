"""Validation-specific exceptions.

``ValidationError`` re-exports the core error so that existing
:class:`hermes.core.errors.ValidationError` handlers keep working.
"""

from hermes.core.errors import ValidationError


class RuleConfigurationError(ValidationError):
    """A rule is configured incorrectly (e.g. unknown pattern name)."""


class RuleExecutionError(ValidationError):
    """A rule failed while running (e.g. a target column is missing)."""


__all__ = [
    "ValidationError",
    "RuleConfigurationError",
    "RuleExecutionError",
]
