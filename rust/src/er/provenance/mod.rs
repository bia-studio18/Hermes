//! Being able to answer "where did this come from, and why was it accepted?".
//!
//! Provenance and audit point at the types they explain rather than owning
//! copies: [`crate::er::ingestion::SourceId`] for sources,
//! [`crate::er::resolution::ResolutionDecision`] for decisions,
//! [`crate::er::matching::MatchEvidence`] for the evidence behind them. One
//! definition each, referenced everywhere.

mod audit;
mod provenance;

pub use audit::{AuditEntry, AuditLog, Explanation, RecordArchive};
pub use provenance::{EntityLineage, LineageEvent, Provenance, SourceRecord, Transformation};