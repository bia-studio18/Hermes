//! Concrete representation strategies.
//!
//! `streaming`, `lazy`, `memory_mapped` and `remote` land here later as sibling
//! modules; each only adds a type and its `DatasetRepresentation` impl.

mod in_memory;

pub use in_memory::InMemoryRepresentation;