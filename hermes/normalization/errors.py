from hermes.core.errors import NormalizationError


class RuleConfigurationError(NormalizationError):
    pass


class RuleExecutionError(NormalizationError):
    pass


class TransformationError(RuleExecutionError):
    pass


__all__ = [
    "NormalizationError",
    "RuleConfigurationError",
    "RuleExecutionError",
    "TransformationError",
]
