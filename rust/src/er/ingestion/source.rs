//! What an external source is, and how Hermes refers to it once read.
//!
//! `Source` is a description, never a connection: holding one does not open a
//! socket or touch a file. `ingest` turns a `Source` into a live reader.
//! `SourceKind` is the coarse tag used by source detection and by provenance
//! (which source did this value come from).

use std::path::Path;

/// Coarse classification of a source, used for detection and for provenance.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum SourceKind {
    Csv,
    Json,
    Parquet,
    Database,
    Api,
    Streaming,
    Unknown,
}

impl SourceKind {
    /// The tag as it appears in provenance and error messages.
    pub fn as_str(&self) -> &'static str {
        match self {
            SourceKind::Csv => "CSV",
            SourceKind::Json => "JSON",
            SourceKind::Parquet => "PARQUET",
            SourceKind::Database => "DATABASE",
            SourceKind::Api => "API",
            SourceKind::Streaming => "STREAMING",
            SourceKind::Unknown => "UNKNOWN",
        }
    }
}

/// Stable handle for a source across a run, so provenance can name it without
/// holding the description.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub struct SourceId(pub u64);

impl SourceId {
    /// First source of a run.
    pub const FIRST: SourceId = SourceId(0);
}

/// A file on the local filesystem. `format` overrides extension detection when
/// the extension lies or is missing.
#[derive(Debug, Clone)]
pub struct FileSource {
    pub path: std::path::PathBuf,
    pub format: Option<SourceKind>,
}

/// A relational query. `table` and `where` are conveniences; `sql` wins when
/// both are given.
#[derive(Debug, Clone)]
pub struct DatabaseSource {
    pub dsn: String,
    pub table: Option<String>,
    pub sql: Option<String>,
    /// Columns to select, in output order. `None` means every column.
    pub columns: Option<Vec<String>>,
}

/// An HTTP endpoint returning records, either as a bare array or wrapped in an
/// envelope reachable at `envelope_path` (e.g. `data.items`).
#[derive(Debug, Clone)]
pub struct ApiSource {
    pub url: String,
    pub method: crate::http::Method,
    pub headers: Vec<(String, String)>,
    pub query: Vec<(String, String)>,
    pub body: Option<String>,
    pub envelope_path: Option<Vec<String>>,
}

/// A long-lived stream: broker topic, websocket, or tail of a growing file.
#[derive(Debug, Clone)]
pub struct StreamSource {
    pub uri: String,
    /// Expected record format on the stream.
    pub format: SourceKind,
}

/// Everything ingestion can be pointed at.
#[derive(Debug, Clone)]
pub enum Source {
    File(FileSource),
    Database(DatabaseSource),
    Api(ApiSource),
    Stream(StreamSource),
}

impl Source {
    /// The coarse kind of this source.
    pub fn kind(&self) -> SourceKind {
        match self {
            Source::File(file) => file
                .format
                .or_else(|| detect_format(&file.path))
                .unwrap_or(SourceKind::Unknown),
            Source::Database(_) => SourceKind::Database,
            Source::Api(_) => SourceKind::Api,
            Source::Stream(stream) => stream.format,
        }
    }

    /// Builds the reader for this source. `ingest` does this; call it directly
    /// only to drive a source incrementally.
    pub fn open(&self) -> Result<super::reader::BoxedReader, crate::er::ErError> {
        super::open_reader(self)
    }
}

/// Guesses how a source should be read: file extension first, then URL scheme.
///
/// Pure string inspection — it never opens the source. A `SourceKind::Unknown`
/// answer is not an error here; `ingest` rejects it.
pub fn identify_source(source: &str) -> SourceKind {
    if let Some(kind) = detect_format(Path::new(source)) {
        return kind;
    }

    let lower = source.to_lowercase();
    if lower.starts_with("http://") || lower.starts_with("https://") {
        SourceKind::Api
    } else if lower.starts_with("postgres://")
        || lower.starts_with("postgresql://")
        || lower.starts_with("mysql://")
        || lower.starts_with("sqlite://")
        || lower.starts_with("mongodb://")
    {
        SourceKind::Database
    } else if lower.starts_with("kafka://")
        || lower.starts_with("amqp://")
        || lower.starts_with("mqtt://")
        || lower.starts_with("ws://")
        || lower.starts_with("wss://")
    {
        SourceKind::Streaming
    } else {
        SourceKind::Unknown
    }
}

/// Recognized file extension, or `None` when the path is not a known format.
fn detect_format(path: &Path) -> Option<SourceKind> {
    match path.extension().and_then(|e| e.to_str())?.to_lowercase().as_str() {
        "csv" | "tsv" => Some(SourceKind::Csv),
        "json" | "jsonl" | "ndjson" => Some(SourceKind::Json),
        "parquet" | "pq" => Some(SourceKind::Parquet),
        _ => None,
    }
}