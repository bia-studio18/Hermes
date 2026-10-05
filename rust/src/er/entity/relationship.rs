//! How entities relate to each other.
//!
//! Relationships are typed loosely on purpose — `RelatedTo(String)` and the
//! handful of well-known kinds share one representation — because the useful
//! edges differ per domain and the graph must not need a schema change to grow
//! one. What matters architecturally is that a relationship can *contribute
//! evidence*: two people who share an employer are not the same person, but two
//! records for the same device at the same site are worth comparing.

use crate::er::ErError;

use super::attribute::Validity;
use super::identity::EntityId;

/// Which way a relationship reads.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Direction {
    /// `from` is the subject.
    Outgoing,
    /// `to` is the subject.
    Incoming,
    /// Reads the same either way.
    Symmetric,
}

/// A typed edge between two entities.
#[derive(Debug, Clone, PartialEq)]
pub struct Relationship {
    /// Verb of the edge: `works_for`, `owns`, `located_at`.
    pub kind: String,
    pub from: EntityId,
    pub to: EntityId,
    pub direction: Direction,
    pub validity: Validity,
    /// 0.0..=1.0 trust in this edge.
    pub confidence: f64,
    /// Source records this edge was read from.
    pub provenance: Option<crate::er::provenance::Provenance>,
}

impl Relationship {
    /// An edge `from`→`to` of kind `kind`.
    pub fn new(kind: impl Into<String>, from: EntityId, to: EntityId) -> Self {
        Self {
            kind: kind.into(),
            from,
            to,
            direction: Direction::Outgoing,
            validity: Validity::unknown(),
            confidence: 1.0,
            provenance: None,
        }
    }

    /// Marks the edge as valid in both directions.
    pub fn symmetric(mut self) -> Self {
        self.direction = Direction::Symmetric;
        self
    }

    /// Sets the period the edge holds for.
    pub fn during(mut self, validity: Validity) -> Self {
        self.validity = validity;
        self
    }

    /// Whether the edge held at `date` (`YYYY-MM-DD`).
    pub fn is_valid_at(&self, date: &str) -> bool {
        self.validity.covers(date)
    }
}

/// Well-known relationship kinds, as constants. Not an enum: an open set of
/// kinds is the point, and a `String` that happens to start with one of these
/// is still a valid kind.
pub mod kinds {
    pub const WORKS_FOR: &str = "works_for";
    pub const OWNS: &str = "owns";
    pub const LOCATED_AT: &str = "located_at";
    pub const HAS_ADDRESS: &str = "has_address";
    pub const HAS_PHONE: &str = "has_phone";
    pub const PART_OF: &str = "part_of";
    pub const SUPPLIES: &str = "supplies";
    pub const RELATED_TO: &str = "related_to";
}

/// Every edge touching one entity.
#[derive(Debug, Clone, Default)]
pub struct RelationshipSet {
    relationships: Vec<Relationship>,
}

impl RelationshipSet {
    /// An empty set.
    pub fn empty() -> Self {
        Self::default()
    }

    /// Adds an edge.
    pub fn push(&mut self, relationship: Relationship) {
        self.relationships.push(relationship);
    }

    /// Edges of one kind touching `entity`.
    pub fn of_kind(&self, entity: EntityId, kind: &str) -> impl Iterator<Item = &Relationship> {
        self.relationships.iter().filter(move |r| {
            r.kind == kind && (r.from == entity || r.to == entity)
        })
    }

    /// Edges that were valid at `date`.
    pub fn valid_at(&self, date: &str) -> impl Iterator<Item = &Relationship> {
        self.relationships
            .iter()
            .filter(move |r| r.is_valid_at(date))
    }

    /// Neighbours reachable in one hop.
    pub fn neighbours(&self, entity: EntityId) -> Vec<EntityId> {
        self.relationships
            .iter()
            .filter_map(|r| {
                if r.from == entity {
                    Some(r.to)
                } else if r.to == entity {
                    Some(r.from)
                } else {
                    None
                }
            })
            .collect()
    }

    /// Rejects an edge that points at the entity it starts from.
    pub fn insert(&mut self, relationship: Relationship) -> Result<(), ErError> {
        if relationship.from == relationship.to {
            return Err(ErError::Entity(format!(
                "self-referential {} relationship on E{}",
                relationship.kind, relationship.from.0
            )));
        }
        self.relationships.push(relationship);
        Ok(())
    }

    /// Every edge.
    pub fn iter(&self) -> impl Iterator<Item = &Relationship> {
        self.relationships.iter()
    }

    /// Number of edges.
    pub fn len(&self) -> usize {
        self.relationships.len()
    }

    /// Whether there are no edges.
    pub fn is_empty(&self) -> bool {
        self.relationships.is_empty()
    }
}