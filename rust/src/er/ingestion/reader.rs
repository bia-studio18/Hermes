//! The reader contract every source kind implements.
//!
//! A reader is an incremental iterator over [`RecordBatch`] — the Hermes batch
//! type, not Arrow and not a competing record model. Batches are the unit
//! because that is what the rest of the pipeline consumes: schema inference
//! sees whole columns, candidate generation can hold a block resident without
//! copying it, and Python sees batches it already knows how to build.
//!
//! Contract:
//!
//! * `next_batch` yields `Ok(None)` once, at end of input, and never again.
//! * Readers are pulled, never pushed: no background threads, no prefetch.
//! * Memory is bounded by the batch size the reader is configured with.

use crate::data::RecordBatch;
use crate::er::ErError;

/// Rows per batch for readers that choose their own batch size.
pub const DEFAULT_BATCH_SIZE: usize = 8_192;

/// Pulls an external source into Hermes batches.
///
/// Incremental reading is the whole point of this trait: implementations
/// stream, so a source larger than memory resolves fine.
pub trait Reader {
    /// Failure of this source kind. Bounded by [`ErError`] because every
    /// variant funnels into the one ER error type.
    type Error: Into<ErError>;

    /// The next batch, or `Ok(None)` at end of input.
    fn next_batch(&mut self) -> Result<Option<RecordBatch>, Self::Error>;

    /// Source this reader was built from. Provenance needs it.
    fn source(&self) -> &super::source::Source;
}

/// A `Reader` over the shared error type, i.e. what `ingest` hands around.
pub type BoxedReader = Box<dyn Reader<Error = ErError>>;

/// Drains a reader into the batches it produces.
///
/// Convenience for callers that do want the whole source in memory; the
/// streaming path calls `next_batch` directly instead.
pub fn collect_batches(reader: &mut dyn Reader<Error = ErError>) -> Result<Vec<RecordBatch>, ErError> {
    let mut batches = Vec::new();
    while let Some(batch) = reader.next_batch()? {
        batches.push(batch);
    }
    Ok(batches)
}