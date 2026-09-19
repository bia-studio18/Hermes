from hermes.core.errors import ValidationError


class RuleConfigurationError(ValidationError): ...


class RuleExecutionError(ValidationError): ...


__all__ = [
    "ValidationError",
    "RuleConfigurationError",
    "RuleExecutionError",
]
