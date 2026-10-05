//! JSON and JSON Lines reader.
//!
//! Both shapes arrive here: a single array document, and newline-delimited
//! objects. They differ only in how records are framed, so one reader handles
//! both and takes the framing as configuration.

use std::path::PathBuf;

use crate::data::RecordBatch;
use crate::er::ErError;

use super::reader::{Reader, DEFAULT_BATCH_SIZE};
use super::source::{Source, SourceKind};

/// How records are framed inside a JSON document.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum JsonLayout {
    /// A top-level array of objects.
    Array,
    /// One object per line.
    Lines,
    /// A top-level object wrapping the records, e.g. `{"data": [...]}`.
    Envelope(Vec<String>),
}

/// Layout detection plus batching for [`JsonReader`].
#[derive(Debug, Clone)]
pub struct JsonOptions {
    /// `None` means "decide from the file extension, else sniff".
    pub layout: Option<JsonLayout>,
    /// Object keys to lift out of every record, across all batches.
    pub envelope_path: Option<Vec<String>>,
    pub batch_size: usize,
}

impl Default for JsonOptions {
    fn default() -> Self {
        Self {
            layout: None,
            envelope_path: None,
            batch_size: DEFAULT_BATCH_SIZE,
        }
    }
}

/// Streams a JSON document into Hermes batches.
///
/// Values arrive with their source types preserved; widening them into typed
/// columns is schema inference's job.
pub struct JsonReader {
    source: Source,
    options: JsonOptions,
}

impl JsonReader {
    /// A reader over `path` with default options.
    pub fn new(path: PathBuf) -> Self {
        Self::with_options(path, JsonOptions::default())
    }

    /// A reader over `path` with explicit layout and batch settings.
    pub fn with_options(path: PathBuf, options: JsonOptions) -> Self {
        let file = super::source::FileSource {
            path,
            format: Some(SourceKind::Json),
        };
        Self {
            source: Source::File(file),
            options,
        }
    }

    /// The options this reader was built with.
    pub fn options(&self) -> &JsonOptions {
        &self.options
    }
}

impl Reader for JsonReader {
    type Error = ErError;

    fn next_batch(&mut self) -> Result<Option<RecordBatch>, Self::Error> {
        todo!()
    }

    fn source(&self) -> &Source {
        &self.source
    }
}