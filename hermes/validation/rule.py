"""Base class for all validation rules.

A validation rule *observes* data and reports whether it satisfies a
condition. It never modifies the data.
"""

from abc import ABC, abstractmethod
from typing import Any

from hermes.validation.result import RuleResult


class ValidationRule(ABC):
    @property
    def name(self) -> str:
        return type(self).__name__

    @abstractmethod
    def check(self, data: Any, context: Any = None) -> RuleResult:
        """Inspect *data* and return a RuleResult."""
        raise NotImplementedError

    def validate(self) -> None:
        """Validate this rule's own configuration (raises RuleConfigurationError)."""
        pass

    def describe(self) -> dict[str, Any]:
        return {"name": self.name}

    def __repr__(self) -> str:
        return f"{self.name}()"


__all__ = ["ValidationRule"]
