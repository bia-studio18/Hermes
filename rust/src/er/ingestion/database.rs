//! Database reader.
//!
//! Reads a result set row-group by row-group rather than materializing the
//! whole result: `fetch_many` style cursors are the point, since a resolution
//! run over a large table should not need a table-sized buffer.

use crate::data::RecordBatch;
use crate::er::ErError;

use super::reader::{Reader, DEFAULT_BATCH_SIZE};
use super::source::{DatabaseSource, Source};

/// Cursor and batching behaviour for [`DatabaseReader`].
#[derive(Debug, Clone)]
pub struct DatabaseOptions {
    pub batch_size: usize,
    /// Statement timeout in seconds, applied per fetch. `None` means the
    /// server default.
    pub timeout_secs: Option<u64>,
}

impl Default for DatabaseOptions {
    fn default() -> Self {
        Self {
            batch_size: DEFAULT_BATCH_SIZE,
            timeout_secs: None,
        }
    }
}

/// Streams a query result into Hermes batches.
///
/// The DSN is never logged or echoed into errors by this layer; connection
/// detail belongs to the driver, which reports through [`ErError::Ingestion`].
pub struct DatabaseReader {
    source: Source,
    options: DatabaseOptions,
}

impl DatabaseReader {
    /// A reader over the table `table` in the database at `dsn`.
    pub fn new(dsn: impl Into<String>, table: impl Into<String>) -> Self {
        let db = DatabaseSource {
            dsn: dsn.into(),
            table: Some(table.into()),
            sql: None,
            columns: None,
        };
        Self {
            source: Source::Database(db),
            options: DatabaseOptions::default(),
        }
    }

    /// A reader over an explicit SQL query.
    pub fn query(dsn: impl Into<String>, sql: impl Into<String>) -> Self {
        let db = DatabaseSource {
            dsn: dsn.into(),
            table: None,
            sql: Some(sql.into()),
            columns: None,
        };
        Self {
            source: Source::Database(db),
            options: DatabaseOptions::default(),
        }
    }

    /// Overrides the default batch size and timeout.
    pub fn with_options(mut self, options: DatabaseOptions) -> Self {
        self.options = options;
        self
    }

    /// The options this reader was built with.
    pub fn options(&self) -> &DatabaseOptions {
        &self.options
    }
}

impl Reader for DatabaseReader {
    type Error = ErError;

    fn next_batch(&mut self) -> Result<Option<RecordBatch>, Self::Error> {
        todo!()
    }

    fn source(&self) -> &Source {
        &self.source
    }
}