//! Hermes Dataset intermediate representation.
//!
//! Python talks to Hermes; Hermes talks to Arrow. The layering is:
//!
//! ```text
//! HermesDataset
//!     └─ DatasetRepresentation   (InMemory, Streaming, Lazy, MemoryMapped, Remote)
//!         └─ data::RecordBatch
//!             └─ arrow_array::RecordBatch
//! ```
//!
//! Arrow never escapes this module tree, and no Python type mirrors it.

mod batch;
mod dataset;
mod hdr;
mod representation;
mod representations;

mod python;

pub use batch::RecordBatch;
pub use dataset::HermesDataset;
pub use representation::{DatasetRepresentation, RepresentationKind};
pub use representations::InMemoryRepresentation;

pub(crate) use python::register;