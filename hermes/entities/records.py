from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class ResolutionLabel(StrEnum):
    MATCH = "match"
    NOT_MATCH = "not_match"
    UNCERTAIN = "uncertain"


class ResolutionAction(StrEnum):
    LINKED = "linked"
    CREATED = "created"
    UNCHANGED = "unchanged"
    NEEDS_REVIEW = "needs_review"


class FieldRole(StrEnum):
    IGNORE = "ignore"
    NAME = "name"
    ALIAS = "alias"
    EXTERNAL_ID = "external_id"
    MATCHING = "matching"
    ATTRIBUTE = "attribute"


class ConflictPolicy(StrEnum):
    UNCERTAIN = "uncertain"
    NOT_MATCH = "not_match"


@dataclass(frozen=True)
class EntityIdentity:
    entity_id: str
    entity_type: str


@dataclass(frozen=True)
class CanonicalProjection:
    entity_id: str
    entity_type: str
    canonical_name: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    as_of: datetime | None = None


@dataclass(frozen=True)
class IdentifierAssertion:
    entity_id: str | None
    scheme: str
    value: str
    source: str | None = None
    status: str = "asserted"
    valid_from: datetime | None = None
    valid_to: datetime | None = None


@dataclass(frozen=True)
class NameAssertion:
    entity_id: str | None
    value: str
    name_type: str = "name"
    language: str | None = None
    source: str | None = None
    valid_from: datetime | None = None
    valid_to: datetime | None = None


@dataclass(frozen=True)
class AttributeAssertion:
    entity_id: str | None
    name: str
    value: Any
    source: str | None = None
    observed_at: datetime | None = None
    valid_from: datetime | None = None
    valid_to: datetime | None = None


@dataclass(frozen=True)
class Observation:
    observation_id: str
    source_record_ref: str
    dataset_ref: str | None = None
    payload: Any = None
    observed_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RelationshipAssertion:
    relationship_id: str
    source_entity_id: str | None
    relationship_type: str
    target_entity_id: str | None
    source: str | None = None
    confidence: float | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    observed_at: datetime | None = None
    valid_from: datetime | None = None
    valid_to: datetime | None = None


@dataclass(frozen=True)
class EvidenceItem:
    field: str
    method: str
    score: float
    left_value: Any = None
    right_value: Any = None
    source: str | None = None
    explanation: str | None = None


@dataclass(frozen=True)
class ResolutionResult:
    left_ref: str
    right_ref: str
    label: ResolutionLabel
    score: float
    evidence: tuple[EvidenceItem, ...] = ()
    matched_entity_id: str | None = None
    action: ResolutionAction = ResolutionAction.UNCHANGED
    diagnostics: tuple[str, ...] = ()


@dataclass(frozen=True)
class ResolutionRun:
    run_id: str
    results: tuple[ResolutionResult, ...] = ()
    unresolved: tuple[str, ...] = ()
    diagnostics: tuple[str, ...] = ()


@dataclass(frozen=True)
class EntityLifecycleEvent:
    event_id: str
    entity_id: str
    event_type: str
    related_entity_ids: tuple[str, ...] = ()
    source: str | None = None
    occurred_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


__all__ = [
    "AttributeAssertion",
    "CanonicalProjection",
    "ConflictPolicy",
    "EntityIdentity",
    "EntityLifecycleEvent",
    "EvidenceItem",
    "FieldRole",
    "IdentifierAssertion",
    "NameAssertion",
    "Observation",
    "RelationshipAssertion",
    "ResolutionAction",
    "ResolutionLabel",
    "ResolutionResult",
    "ResolutionRun",
]
