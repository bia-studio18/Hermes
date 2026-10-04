//! Hermes' record batch.

/// A chunk of rows.
///
/// Thin wrapper: Arrow is the storage format, this type is the Hermes name for
/// it. Keeping the wrapper means the rest of the codebase depends on
/// `RecordBatch` and never on `arrow_array` directly.
pub struct RecordBatch {
    inner: arrow_array::RecordBatch,
}

impl RecordBatch {
    /// Wraps an Arrow record batch.
    pub fn new(inner: arrow_array::RecordBatch) -> Self {
        Self { inner }
    }

    /// The underlying Arrow record batch.
    pub fn inner(&self) -> &arrow_array::RecordBatch {
        &self.inner
    }
}