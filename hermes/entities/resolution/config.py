from dataclasses import dataclass

from hermes.entities.records import ConflictPolicy, FieldRole


@dataclass(frozen=True)
class FieldBinding:
    field: str
    role: FieldRole
    method: str = "exact"
    weight: float = 1.0
    blocking: bool = False


@dataclass(frozen=True)
class ResolutionPolicy:
    match_threshold: float
    uncertain_threshold: float
    conflict_policy: ConflictPolicy = ConflictPolicy.UNCERTAIN
    field_bindings: tuple[FieldBinding, ...] = ()
    source_priority: tuple[tuple[str, int], ...] = ()


__all__ = ["FieldBinding", "ResolutionPolicy"]
