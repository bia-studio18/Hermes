//! CSV / TSV reader.

use std::path::PathBuf;

use crate::data::RecordBatch;
use crate::er::ErError;

use super::reader::{Reader, DEFAULT_BATCH_SIZE};
use super::source::{Source, SourceKind};

/// Delimiter and header handling for [`CsvReader`].
#[derive(Debug, Clone)]
pub struct CsvOptions {
    /// Field separator. `None` means "sniff from the file".
    pub delimiter: Option<u8>,
    pub has_header: bool,
    /// Rows per emitted batch.
    pub batch_size: usize,
}

impl Default for CsvOptions {
    fn default() -> Self {
        Self {
            delimiter: None,
            has_header: true,
            batch_size: DEFAULT_BATCH_SIZE,
        }
    }
}

/// Streams a delimited file into Hermes batches.
///
/// All columns arrive as strings; typing them is schema inference's job, not
/// ingestion's.
pub struct CsvReader {
    source: Source,
    options: CsvOptions,
}

impl CsvReader {
    /// A reader over `path` with default options.
    pub fn new(path: PathBuf) -> Self {
        Self::with_options(path, CsvOptions::default())
    }

    /// A reader over `path` with explicit delimiter, header and batch settings.
    pub fn with_options(path: PathBuf, options: CsvOptions) -> Self {
        let file = super::source::FileSource {
            path,
            format: Some(SourceKind::Csv),
        };
        Self {
            source: Source::File(file),
            options,
        }
    }

    /// The options this reader was built with.
    pub fn options(&self) -> &CsvOptions {
        &self.options
    }
}

impl Reader for CsvReader {
    type Error = ErError;

    fn next_batch(&mut self) -> Result<Option<RecordBatch>, Self::Error> {
        todo!()
    }

    fn source(&self) -> &Source {
        &self.source
    }
}