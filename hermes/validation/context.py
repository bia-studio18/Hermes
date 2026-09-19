"""Optional runtime context passed to validation rules during execution."""

from typing import Any


class ValidationContext:
    """Carries optional runtime information (e.g. ``now`` for freshness checks).

    Rules read from the context via :meth:`get` / :meth:`require`; it is
    entirely optional and never mutated by rules.
    """

    def __init__(self, **values: Any) -> None:
        self._values: dict[str, Any] = dict(values)

    def get(self, key: str, default: Any = None) -> Any:
        return self._values.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._values[key] = value

    def has(self, key: str) -> bool:
        return key in self._values

    def require(self, key: str) -> Any:
        if key not in self._values:
            raise KeyError(f"Context value {key!r} is not set")
        return self._values[key]

    def copy(self) -> "ValidationContext":
        return ValidationContext(**self._values)

    def to_dict(self) -> dict[str, Any]:
        return dict(self._values)


__all__ = ["ValidationContext"]
