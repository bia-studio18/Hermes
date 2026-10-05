//! Entities, and the identifiers and edges that connect them.
//!
//! Nothing in this module resolves anything. It owns the *shape* of an entity
//! and the operations that change that shape (absorb, link, add identity), so
//! the resolution stage has somewhere to put its conclusions.

mod attribute;
mod entity;
mod identity;
mod relationship;

pub use attribute::{Attribute, AttributeSet, Validity};
pub use entity::Entity;
pub use identity::{EntityId, Identity, IdentityKind, IdentitySet, IdentityStrength};
pub use relationship::{kinds, Direction, Relationship, RelationshipSet};

use crate::er::candidate::RecordId;
use crate::er::ErError;

/// Stores entities and answers questions about them.
///
/// A trait rather than a struct because the storage question is deliberately
/// open: an in-memory map for a first run, a graph database later, and neither
/// is decided here. What the trait fixes is the vocabulary — create, link,
/// merge — so a store cannot quietly grow a different one.
pub trait EntityStore {
    /// Adds a new entity, assigning its id.
    fn create(&mut self, entity: Entity) -> Result<EntityId, ErError>;

    /// Reads an entity.
    fn get(&self, id: EntityId) -> Option<&Entity>;

    /// Folds `record` into `entity`, recording the link in its lineage.
    fn link(
        &mut self,
        entity: EntityId,
        record: RecordId,
        evidence: &crate::er::matching::MatchEvidence,
    ) -> Result<(), ErError>;

    /// Folds one entity into another, keeping the surviving entity's id.
    fn merge(&mut self, keep: EntityId, absorb: EntityId) -> Result<(), ErError>;

    /// Every entity of one type, for blocking against a single type.
    fn by_type(&self, entity_type: &str) -> Vec<EntityId>;

    /// Finds entities carrying this exact canonical identity value.
    fn by_identity(&self, value: &str) -> Vec<EntityId>;
}