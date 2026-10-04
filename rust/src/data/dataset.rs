//! The top-level dataset type. Knows a representation, never a storage detail.

use super::batch::RecordBatch;
use super::representation::{DatasetRepresentation, RepresentationKind};
use super::representations::InMemoryRepresentation;

/// A Hermes dataset.
///
/// Deliberately representation-agnostic: it holds a boxed
/// [`DatasetRepresentation`], never `Vec<RecordBatch>` and never a concrete
/// representation type. Both rules are what let a new strategy drop in without
/// touching this struct or the Python API.
pub struct HermesDataset {
    representation: Box<dyn DatasetRepresentation>,
}

impl HermesDataset {
    /// Placeholder constructor over materialized batches.
    pub fn in_memory(batches: Vec<RecordBatch>) -> Self {
        Self {
            representation: Box::new(InMemoryRepresentation::new(batches)),
        }
    }

    /// Wraps any representation, including ones added later.
    pub fn from_representation(representation: Box<dyn DatasetRepresentation>) -> Self {
        Self { representation }
    }

    /// The strategy backing this dataset.
    pub fn kind(&self) -> RepresentationKind {
        self.representation.kind()
    }

    /// Borrowed access to the representation for the operations that need it.
    pub fn representation(&self) -> &dyn DatasetRepresentation {
        self.representation.as_ref()
    }
}