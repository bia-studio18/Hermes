//! Naming things: entity ids, record ids, and the identifiers that link them.
//!
//! Three id types on purpose, because they answer different questions:
//!
//! * [`EntityId`] — which entity this is, stable for the life of the store.
//! * [`RecordId`] — which source row, meaningless outside its source.
//! * [`Identity`] — what the world calls it, and which may change over time.

use std::collections::BTreeMap;

use crate::er::value::Value;

/// Stable handle for one entity. Assigned once, never reused.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord, Default)]
pub struct EntityId(pub u64);

impl EntityId {
    /// The first entity of a store.
    pub const FIRST: EntityId = EntityId(0);

    /// The numeric form, for storage and for display as `E123`.
    pub fn get(&self) -> u64 {
        self.0
    }
}

/// How strong an identity is as evidence.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum IdentityStrength {
    /// Unique within one source only, e.g. a CRM customer number.
    ScopedToSource,
    /// Unique for the entity type, e.g. a company registration number.
    Typed,
    /// Unique across everything Hermes knows, e.g. an email address.
    Global,
}

impl IdentityStrength {
    /// Whether an equality on this identity can decide a match on its own.
    pub fn is_decisive(&self) -> bool {
        matches!(
            self,
            IdentityStrength::Typed | IdentityStrength::Global
        )
    }
}

/// What kind of thing an identity is.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum IdentityKind {
    /// Assigned by a source.
    SourceKey,
    /// Registered with an authority: registration number, tax id, passport.
    OfficialKey,
    /// Derived from a value that ought to be unique, e.g. an email address.
    Derived,
    /// A cross-reference to an entity in another system.
    ExternalRef,
}

/// One claim about how an entity can be named, and how much it can be trusted.
#[derive(Debug, Clone, PartialEq)]
pub struct Identity {
    pub kind: IdentityKind,
    /// Canonical form, after normalization. Comparison happens here.
    pub value: Value,
    /// The value as the source stated it. Never dropped.
    pub raw: Value,
    pub strength: IdentityStrength,
    /// Source the identity came from. `None` for a canonical identity.
    pub source: Option<crate::er::ingestion::SourceId>,
    /// Field this identity was read from, when it came from a record.
    pub field: Option<String>,
}

/// Every identity known for an entity, keyed by canonical value so an identity
/// learned twice collapses into one entry with two sources.
#[derive(Debug, Clone, Default)]
pub struct IdentitySet {
    identities: BTreeMap<String, Identity>,
}

impl IdentitySet {
    /// An empty set.
    pub fn empty() -> Self {
        Self::default()
    }

    /// Adds an identity, merging its source into any existing entry for the
    /// same canonical value.
    pub fn insert(&mut self, identity: Identity) -> Option<Identity> {
        let key = identity.value.as_text().unwrap_or_default();
        match self.identities.get_mut(&key) {
            Some(existing) => {
                if let Some(source) = identity.source {
                    if existing.source != Some(source) {
                        // Two sources agreeing on one identity is evidence, but
                        // the set keeps one entry; the provenance record keeps
                        // both.
                        existing.strength = stronger(existing.strength, identity.strength);
                    }
                }
                None
            }
            None => self.identities.insert(key, identity.clone()),
        }
    }

    /// The identity with this canonical value.
    pub fn get(&self, value: &str) -> Option<&Identity> {
        self.identities.get(value)
    }

    /// Whether any identity is decisive.
    pub fn has_decisive(&self) -> bool {
        self.identities
            .values()
            .any(|i| i.strength.is_decisive())
    }

    /// Every identity.
    pub fn iter(&self) -> impl Iterator<Item = &Identity> {
        self.identities.values()
    }

    /// Number of distinct identities.
    pub fn len(&self) -> usize {
        self.identities.len()
    }

    /// Whether nothing is known yet.
    pub fn is_empty(&self) -> bool {
        self.identities.is_empty()
    }
}

/// The stronger of two strengths.
fn stronger(a: IdentityStrength, b: IdentityStrength) -> IdentityStrength {
    if a.is_decisive() || b.is_decisive() {
        IdentityStrength::Global
    } else {
        IdentityStrength::ScopedToSource
    }
}