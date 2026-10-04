//! Fully materialized representation: every row is resident.

use crate::data::batch::RecordBatch;
use crate::data::representation::{DatasetRepresentation, RepresentationKind};

/// Holds every batch in memory:
///
/// ```text
/// InMemoryRepresentation
/// ├── Hermes RecordBatch -> Arrow RecordBatch
/// ├── Hermes RecordBatch -> Arrow RecordBatch
/// └── Hermes RecordBatch -> Arrow RecordBatch
/// ```
pub struct InMemoryRepresentation {
    batches: Vec<RecordBatch>,
}

impl InMemoryRepresentation {
    pub fn new(batches: Vec<RecordBatch>) -> Self {
        Self { batches }
    }

    /// The materialized batches, in order.
    pub fn batches(&self) -> &[RecordBatch] {
        &self.batches
    }
}

impl DatasetRepresentation for InMemoryRepresentation {
    fn kind(&self) -> RepresentationKind {
        RepresentationKind::InMemory
    }
}