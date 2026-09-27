from typing import Protocol


class ComparisonBackend(Protocol):
    def compare(self, left: str, right: str, method: str) -> float: ...


class RustComparisonBackend:
    def compare(self, left: str, right: str, method: str) -> float:
        raise NotImplementedError


__all__ = ["ComparisonBackend", "RustComparisonBackend"]
