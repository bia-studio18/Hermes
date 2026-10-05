//! Streaming source reader.
//!
//! A stream has no end, so `next_batch` returning `Ok(None)` means "nothing
//! available right now", not "exhausted". Downstream stages must treat the
//! difference as normal operation rather than as completion, which is why
//! [`StreamReader`] reports poll intervals instead of pretending to be a file.

use crate::data::RecordBatch;
use crate::er::ErError;

use super::reader::{Reader, DEFAULT_BATCH_SIZE};
use super::source::{Source, SourceKind, StreamSource};

/// Poll and batching behaviour for [`StreamReader`].
#[derive(Debug, Clone)]
pub struct StreamOptions {
    /// How long to wait before an empty poll is retried.
    pub poll_interval: std::time::Duration,
    /// Rows per emitted batch.
    pub batch_size: usize,
    /// Consumer group or subscription name.
    pub group: Option<String>,
}

impl Default for StreamOptions {
    fn default() -> Self {
        Self {
            poll_interval: std::time::Duration::from_millis(250),
            batch_size: DEFAULT_BATCH_SIZE,
            group: None,
        }
    }
}

/// Pulls messages from a broker, websocket or tailed file.
pub struct StreamReader {
    source: Source,
    options: StreamOptions,
}

impl StreamReader {
    /// A reader over `uri`, expecting records in `format`.
    pub fn new(uri: impl Into<String>, format: SourceKind) -> Self {
        let stream = StreamSource {
            uri: uri.into(),
            format,
        };
        Self {
            source: Source::Stream(stream),
            options: StreamOptions::default(),
        }
    }

    /// Overrides poll interval, batch size and consumer group.
    pub fn with_options(mut self, options: StreamOptions) -> Self {
        self.options = options;
        self
    }

    /// The options this reader was built with.
    pub fn options(&self) -> &StreamOptions {
        &self.options
    }

    /// Whether `next_batch` reaching `Ok(None)` means end of input. Always
    /// false for a live stream.
    pub fn is_exhausted(&self) -> bool {
        false
    }
}

impl Reader for StreamReader {
    type Error = ErError;

    fn next_batch(&mut self) -> Result<Option<RecordBatch>, Self::Error> {
        todo!()
    }

    fn source(&self) -> &Source {
        &self.source
    }
}