//! Where every value came from, and how it got here.
//!
//! The rule this module exists to enforce: the original record is never lost.
//! Every value Hermes stores can be traced to a source record, and every change
//! to it through the transformations applied on the way. A merge that cannot be
//! explained is indistinguishable from a bug.

use std::collections::BTreeMap;

use crate::er::candidate::RecordId;
use crate::er::ingestion::SourceId;
use crate::er::value::Value;

/// One source record, as it was read.
#[derive(Debug, Clone, PartialEq)]
pub struct SourceRecord {
    pub id: RecordId,
    /// The values exactly as the source stated them. Never normalized.
    pub values: BTreeMap<String, Value>,
    /// Position within the source, for human-facing error messages.
    pub position: Option<String>,
}

impl SourceRecord {
    /// A record with no values yet.
    pub fn empty(id: RecordId) -> Self {
        Self {
            id,
            values: BTreeMap::new(),
            position: None,
        }
    }

    /// The raw value of `field`.
    pub fn raw(&self, field: &str) -> Option<&Value> {
        self.values.get(field)
    }
}

/// One step a value went through, in order.
#[derive(Debug, Clone, PartialEq)]
pub struct Transformation {
    /// The stage that applied it: `normalization`, `resolution`, `merge`.
    pub stage: String,
    /// The specific rule, normalizer name or merge id.
    pub operation: String,
    /// Input value, so the step can be replayed or inspected.
    pub before: Value,
    /// Output value.
    pub after: Value,
}

impl Transformation {
    /// A step with no before/after values recorded.
    pub fn named(stage: impl Into<String>, operation: impl Into<String>) -> Self {
        Self {
            stage: stage.into(),
            operation: operation.into(),
            before: Value::Null,
            after: Value::Null,
        }
    }

    /// Records the values this step changed.
    pub fn with_values(mut self, before: Value, after: Value) -> Self {
        self.before = before;
        self.after = after;
        self
    }
}

/// The full story of one value or one decision.
#[derive(Debug, Clone, PartialEq, Default)]
pub struct Provenance {
    /// Sources the value was read from, in the order they were seen.
    pub sources: Vec<SourceId>,
    /// Records the value came from.
    pub records: Vec<RecordId>,
    /// Steps applied, oldest first.
    pub transformations: Vec<Transformation>,
    /// Model or configuration version that accepted the value.
    pub model_version: Option<u32>,
}

impl Provenance {
    /// Provenance for a value read straight from one record.
    pub fn from_record(record: RecordId) -> Self {
        Self {
            sources: vec![record.source],
            records: vec![record],
            transformations: Vec::new(),
            model_version: None,
        }
    }

    /// Appends a transformation step.
    pub fn apply(&mut self, transformation: Transformation) {
        self.transformations.push(transformation);
    }

    /// Adds another source this value was corroborated by.
    pub fn corroborate(&mut self, record: RecordId) {
        if !self.records.contains(&record) {
            self.sources.push(record.source);
            self.records.push(record);
        }
    }

    /// Records which model version produced this value.
    pub fn produced_by(&mut self, version: u32) {
        self.model_version = Some(version);
    }

    /// Whether the value is traceable to at least one source record.
    pub fn is_traceable(&self) -> bool {
        !self.records.is_empty()
    }
}

/// One thing that happened to an entity.
#[derive(Debug, Clone, PartialEq)]
pub enum LineageEvent {
    Created {
        entity: crate::er::entity::EntityId,
        from_record: Option<RecordId>,
    },
    Linked {
        entity: crate::er::entity::EntityId,
        record: RecordId,
        confidence: f64,
    },
    Merged {
        kept: crate::er::entity::EntityId,
        absorbed: crate::er::entity::EntityId,
    },
    /// A merge was undone; the absorbed entity comes back with its own id.
    Unmerged {
        kept: crate::er::entity::EntityId,
        restored: crate::er::entity::EntityId,
    },
    Corrected {
        entity: crate::er::entity::EntityId,
        reason: String,
    },
}

/// The ordered history of one entity.
#[derive(Debug, Clone, PartialEq, Default)]
pub struct EntityLineage {
    pub events: Vec<LineageEvent>,
}

impl EntityLineage {
    /// An empty history.
    pub fn empty() -> Self {
        Self::default()
    }

    /// Appends an event.
    pub fn record(&mut self, event: LineageEvent) {
        self.events.push(event);
    }

    /// Events of one kind.
    pub fn of_kind<'a, F>(&'a self, kind: F) -> Vec<&'a LineageEvent>
    where
        F: Fn(&LineageEvent) -> bool,
    {
        self.events.iter().filter(|e| kind(e)).collect()
    }

    /// Entities this one absorbed, in order. The list a rollback walks in
    /// reverse.
    pub fn absorbed_entities(&self) -> Vec<crate::er::entity::EntityId> {
        self.events
            .iter()
            .filter_map(|e| match e {
                LineageEvent::Merged { absorbed, .. } => Some(*absorbed),
                _ => None,
            })
            .collect()
    }

    /// How many events are recorded.
    pub fn len(&self) -> usize {
        self.events.len()
    }

    /// Whether nothing has happened yet.
    pub fn is_empty(&self) -> bool {
        self.events.is_empty()
    }
}