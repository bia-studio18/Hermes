//! Turning an external source into Hermes data.
//!
//! Ingestion is deliberately the narrowest stage in the pipeline:
//!
//! ```text
//! External Source -> Reader -> Hermes RecordBatch
//! ```
//!
//! It does not infer what a column means, does not type or normalize values,
//! and does not decide anything about entities. Readers emit
//! [`crate::data::RecordBatch`] — the same batch type the rest of Hermes uses —
//! so nothing downstream needs an ingestion-specific record model.

mod apipayload;
mod csv;
mod database;
mod json;
mod parquet;
mod reader;
mod source;
mod streaming;

pub use apipayload::{ApiOptions, ApiReader};
pub use csv::{CsvOptions, CsvReader};
pub use database::{DatabaseOptions, DatabaseReader};
pub use json::{JsonLayout, JsonOptions, JsonReader};
pub use parquet::{ParquetOptions, ParquetReader};
pub use reader::{BoxedReader, Reader, DEFAULT_BATCH_SIZE};
pub use source::{
    identify_source, ApiSource, DatabaseSource, FileSource, Source, SourceId, SourceKind,
    StreamSource,
};
pub use streaming::{StreamOptions, StreamReader};

use crate::data::HermesDataset;
use crate::er::ErError;

/// A source that has been read, tagged with the id provenance will refer to.
pub struct IngestedDataset {
    id: SourceId,
    source: Source,
    dataset: HermesDataset,
}

impl IngestedDataset {
    /// The handle provenance and learning use to name this source.
    pub fn id(&self) -> SourceId {
        self.id
    }

    /// The description the dataset was read from.
    pub fn source(&self) -> &Source {
        &self.source
    }

    /// The batches. Representation-agnostic; ask it for `kind()` first.
    pub fn dataset(&self) -> &HermesDataset {
        &self.dataset
    }

    /// Unwraps the dataset, dropping the source bookkeeping.
    pub fn into_dataset(self) -> HermesDataset {
        self.dataset
    }
}

/// Builds the reader for `source` without reading it.
///
/// Cheap and fallible only on configuration grounds, so a caller can inspect a
/// source, then stream it incrementally.
pub fn open_reader(source: &Source) -> Result<BoxedReader, ErError> {
    match source {
        Source::File(file) => match file.format.unwrap_or_else(|| source.kind()) {
            SourceKind::Csv => Ok(Box::new(CsvReader::new(file.path.clone()))),
            SourceKind::Json => Ok(Box::new(JsonReader::new(file.path.clone()))),
            SourceKind::Parquet => Ok(Box::new(ParquetReader::new(file.path.clone()))),
            other => Err(ErError::Configuration(format!(
                "no reader for file format {}",
                other.as_str()
            ))),
        },
        Source::Database(db) => Ok(match (&db.sql, &db.table) {
            (Some(_), _) => Box::new(DatabaseReader::query(db.dsn.clone(), String::new())),
            (None, Some(table)) => Box::new(DatabaseReader::new(db.dsn.clone(), table.clone())),
            (None, None) => {
                return Err(ErError::Configuration(
                    "database source needs a table or a query".to_string(),
                ));
            }
        }),
        Source::Api(api) => {
            let reader = ApiReader::request(api.method.clone(), api.url.clone())
                .with_headers(api.headers.clone())
                .with_query(api.query.clone());
            Ok(Box::new(match api.body.clone() {
                Some(body) => reader.with_body(body),
                None => reader,
            }))
        }
        Source::Stream(stream) => Ok(Box::new(StreamReader::new(
            stream.uri.clone(),
            stream.format,
        ))),
    }
}

/// Reads `source` to completion and returns the batches as one dataset.
///
/// The one-shot entry point. Callers that must not hold the whole source use
/// [`open_reader`] and pull batches instead.
// ponytail: buffers every batch; drop in a `StreamingRepresentation` (already a
// `RepresentationKind` variant) once a source outgrows memory.
pub fn ingest(source: Source) -> Result<IngestedDataset, ErError> {
    ingest_with_id(source, SourceId::FIRST)
}

/// [`ingest`] with an explicit provenance id.
pub fn ingest_with_id(source: Source, id: SourceId) -> Result<IngestedDataset, ErError> {
    let mut reader = open_reader(&source)?;
    let batches = reader::collect_batches(reader.as_mut())?;
    Ok(IngestedDataset {
        id,
        source,
        dataset: HermesDataset::in_memory(batches),
    })
}