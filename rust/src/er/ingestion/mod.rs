//! Source ingestion. Readers land here as the empty `csv`, `json`, `parquet`,
//! `database`, `apipayload` and `streaming` modules get filled in.

mod apipayload;
mod csv;
mod database;
mod identify;
mod json;
mod parquet;
mod streaming;

pub use identify::{identify_source, Source};

/// Entry point for every source type. Takes nothing until the readers exist.
pub fn ingest(source: ()) {
    source
}