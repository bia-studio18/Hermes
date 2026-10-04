//! The representation abstraction owned by every [`crate::data::HermesDataset`].

/// Which concrete strategy backs a dataset.
///
/// Adding a strategy means adding a variant here plus an implementation of
/// [`DatasetRepresentation`]; `HermesDataset` itself never changes.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum RepresentationKind {
    InMemory,
    Streaming,
    Lazy,
    MemoryMapped,
    Remote,
}

/// A dataset's storage strategy.
///
/// Implementors own *how* the data lives (materialized batches, an iterator, a
/// query plan, a file, a remote endpoint) and answer questions about it. They do
/// not need to expose their storage: `HermesDataset` only ever sees this trait.
///
/// The surface is intentionally minimal while the strategies are placeholders.
/// `Send + Sync` is required because `HermesDataset` is held by a PyO3 class,
/// which Python may share and move between threads.
pub trait DatasetRepresentation: Send + Sync {
    /// Identifies the strategy behind this representation.
    fn kind(&self) -> RepresentationKind;
}