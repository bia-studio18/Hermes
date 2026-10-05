//! Parquet reader.
//!
//! Parquet is already typed and columnar, so this reader is the one place where
//! the incoming types reach the pipeline intact. It is also the one source kind
//! where reading fewer row groups than exist is a cheap way to bound memory.

use std::path::PathBuf;

use crate::data::RecordBatch;
use crate::er::ErError;

use super::reader::{Reader, DEFAULT_BATCH_SIZE};
use super::source::{Source, SourceKind};

/// Which parts of a Parquet file to read.
#[derive(Debug, Clone)]
pub struct ParquetOptions {
    /// Columns to project. `None` means every column.
    pub columns: Option<Vec<String>>,
    /// Rows per emitted batch. Batch size is a ceiling, not a guarantee: a
    /// single row group is never split.
    pub batch_size: usize,
}

impl Default for ParquetOptions {
    fn default() -> Self {
        Self {
            columns: None,
            batch_size: DEFAULT_BATCH_SIZE,
        }
    }
}

/// Streams a Parquet file into Hermes batches.
pub struct ParquetReader {
    source: Source,
    options: ParquetOptions,
}

impl ParquetReader {
    /// A reader over `path` reading every column.
    pub fn new(path: PathBuf) -> Self {
        Self::with_options(path, ParquetOptions::default())
    }

    /// A reader over `path` with a column projection and batch ceiling.
    pub fn with_options(path: PathBuf, options: ParquetOptions) -> Self {
        let file = super::source::FileSource {
            path,
            format: Some(SourceKind::Parquet),
        };
        Self {
            source: Source::File(file),
            options,
        }
    }

    /// The options this reader was built with.
    pub fn options(&self) -> &ParquetOptions {
        &self.options
    }
}

impl Reader for ParquetReader {
    type Error = ErError;

    fn next_batch(&mut self) -> Result<Option<RecordBatch>, Self::Error> {
        todo!()
    }

    fn source(&self) -> &Source {
        &self.source
    }
}