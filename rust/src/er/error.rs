//! The single error type for the ER pipeline.
//!
//! One enum, one module: every stage returns `ErError`, so a caller matches on
//! the stage that failed instead of on whichever error type that stage happened
//! to import. Underlying failures (HTTP, I/O, serde) are converted at the
//! boundary rather than leaking into stage signatures.

use std::error::Error;
use std::fmt;
use std::io;

use crate::http::HermesHttpError;

/// Result of any ER stage.
pub type ErResult<T> = Result<T, ErError>;

/// Which stage failed, and why.
#[derive(Debug)]
pub enum ErError {
    /// The requested operation or source kind has no implementation yet.
    Unsupported(String),
    /// The `ErConfig` is internally inconsistent or incomplete.
    Configuration(String),
    /// Reading from an external source failed.
    Ingestion(String),
    /// Schema or field-semantic inference failed.
    Schema(String),
    /// A normalization rule could not be applied to a value.
    Normalization(String),
    /// Candidate generation failed.
    Candidate(String),
    /// Comparing a candidate pair failed.
    Matching(String),
    /// The decision layer failed.
    Resolution(String),
    /// Entity creation, linking or merging failed.
    Entity(String),
    /// Provenance could not be recorded or recovered.
    Provenance(String),
    /// Feedback ingestion or model application failed.
    Learning(String),
}

impl fmt::Display for ErError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ErError::Unsupported(m) => write!(f, "unsupported: {m}"),
            ErError::Configuration(m) => write!(f, "configuration error: {m}"),
            ErError::Ingestion(m) => write!(f, "ingestion error: {m}"),
            ErError::Schema(m) => write!(f, "schema error: {m}"),
            ErError::Normalization(m) => write!(f, "normalization error: {m}"),
            ErError::Candidate(m) => write!(f, "candidate generation error: {m}"),
            ErError::Matching(m) => write!(f, "matching error: {m}"),
            ErError::Resolution(m) => write!(f, "resolution error: {m}"),
            ErError::Entity(m) => write!(f, "entity error: {m}"),
            ErError::Provenance(m) => write!(f, "provenance error: {m}"),
            ErError::Learning(m) => write!(f, "learning error: {m}"),
        }
    }
}

impl Error for ErError {}

impl From<HermesHttpError> for ErError {
    fn from(err: HermesHttpError) -> Self {
        ErError::Ingestion(err.to_string())
    }
}

impl From<io::Error> for ErError {
    fn from(err: io::Error) -> Self {
        ErError::Ingestion(err.to_string())
    }
}

impl From<serde_json::Error> for ErError {
    fn from(err: serde_json::Error) -> Self {
        ErError::Ingestion(err.to_string())
    }
}

impl From<csv::Error> for ErError {
    fn from(err: csv::Error) -> Self {
        ErError::Ingestion(err.to_string())
    }
}