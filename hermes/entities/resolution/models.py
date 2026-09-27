from dataclasses import dataclass


@dataclass(frozen=True)
class Candidate:
    left_ref: str
    right_ref: str
    blocking_keys: tuple[str, ...] = ()


__all__ = ["Candidate"]
