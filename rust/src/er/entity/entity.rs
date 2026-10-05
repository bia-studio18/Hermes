//! The entity: what Hermes concludes a thing is.
//!
//! Generic by construction. An entity is an id, a type *name*, attributes,
//! identities, relationships and lineage — nothing in this struct says whether
//! it is a person, a company or a device, and nothing needs to. That is what
//! lets the same pipeline resolve every entity type without a branch for each.

use crate::er::ErError;
use crate::er::schema::EntityType;
use crate::er::value::Value;

use super::attribute::{Attribute, AttributeSet};
use super::identity::{EntityId, Identity, IdentitySet};
use super::relationship::RelationshipSet;

/// A resolved real-world thing.
#[derive(Debug, Clone, Default)]
pub struct Entity {
    pub id: EntityId,
    /// Which kind of thing this is. A name, not a type: the pipeline never
    /// switches on it.
    pub entity_type: Option<EntityType>,
    pub attributes: AttributeSet,
    pub identities: IdentitySet,
    pub relationships: RelationshipSet,
    /// How much the entity as a whole is trusted, 0.0..=1.0.
    pub confidence: f64,
    /// How this entity came to exist and change.
    pub lineage: crate::er::provenance::EntityLineage,
    /// Records folded into this entity.
    pub source_records: Vec<crate::er::ingestion::SourceId>,
}

impl Entity {
    /// A new entity of `entity_type` with no attributes yet.
    pub fn new(id: EntityId, entity_type: EntityType) -> Self {
        Self {
            id,
            entity_type: Some(entity_type),
            confidence: 0.0,
            ..Default::default()
        }
    }

    /// Adds an attribute.
    pub fn add_attribute(&mut self, attribute: Attribute) {
        self.attributes.push(attribute);
    }

    /// Adds an identity.
    pub fn add_identity(&mut self, identity: Identity) {
        self.identities.insert(identity);
    }

    /// Records that this entity was built from `source`.
    pub fn add_source_record(&mut self, source: crate::er::ingestion::SourceId) {
        self.source_records.push(source);
    }

    /// The value of `field` on this entity, if it has one.
    pub fn field(&self, field: &str) -> Option<&Value> {
        self.attributes
            .get(field)
            .next()
            .map(super::attribute::Attribute::value)
    }

    /// Absorbs `other` into `self`, keeping every value from both sides.
    ///
    /// Attribute and identity sets are unions, never overwrites: the record that
    /// disagreed stays visible with its own provenance, which is what makes the
    /// merge auditable and reversible.
    pub fn absorb(&mut self, other: Entity) -> Result<(), ErError> {
        if self.id == other.id {
            return Err(ErError::Entity(format!(
                "cannot absorb E{} into itself",
                self.id.0
            )));
        }
        for attribute in other.attributes.iter() {
            self.attributes.push(attribute.clone());
        }
        for identity in other.identities.iter() {
            self.identities.insert(identity.clone());
        }
        for relationship in other.relationships.iter() {
            self.relationships.push(relationship.clone());
        }
        self.source_records.extend(other.source_records);
        self.confidence = self.confidence.min(other.confidence);
        Ok(())
    }
}