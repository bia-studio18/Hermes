from hermes.core.errors import NormalizationError


class RuleConfigurationError(NormalizationError):
    """A rule is configured incorrectly (e.g. unknown cast target type)."""


class RuleExecutionError(NormalizationError):
    """A rule failed while applying to data (e.g. a target column is missing)."""


class TransformationError(RuleExecutionError):
    """A value-level conversion failed during rule execution."""


__all__ = [
    "NormalizationError",
    "RuleConfigurationError",
    "RuleExecutionError",
    "TransformationError",
]
