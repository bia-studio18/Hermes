//! Explainability: the answer to "why does Hermes think this?".
//!
//! Audit is a read model over provenance, not a write model. It never becomes
//! the system of record — provenance is — because an audit trail that the audit
//! trail depends on cannot be trusted to audit itself.

use crate::er::candidate::RecordId;
use crate::er::entity::EntityId;
use crate::er::ErError;

use super::provenance::{EntityLineage, Provenance, SourceRecord};

/// One decision, as it was taken.
#[derive(Debug, Clone, PartialEq)]
pub struct AuditEntry {
    pub record: RecordId,
    pub subject: EntityId,
    pub decision: crate::er::resolution::ResolutionDecision,
    pub evidence: crate::er::matching::MatchEvidence,
    pub model_version: Option<u32>,
}

impl AuditEntry {
    /// The provenance of the decision itself.
    pub fn provenance(&self) -> Provenance {
        let mut provenance = Provenance::from_record(self.record);
        provenance.produced_by(self.model_version.unwrap_or_default());
        provenance
    }
}

/// The full explanation for one link: what was decided, on what evidence, from
/// which record, under which model version.
#[derive(Debug, Clone, PartialEq)]
pub struct Explanation {
    pub record: RecordId,
    pub subject: EntityId,
    pub decision: crate::er::resolution::ResolutionDecision,
    pub evidence: crate::er::matching::MatchEvidence,
    pub lineage: EntityLineage,
    pub model_version: Option<u32>,
}

/// Retrievable history of resolutions.
pub trait AuditLog {
    /// Appends an entry.
    fn record(&mut self, entry: AuditEntry) -> Result<(), ErError>;

    /// Every entry for one entity, oldest first.
    fn entries_for(&self, entity: EntityId) -> Result<Vec<AuditEntry>, ErError>;

    /// The explanation for one decision.
    fn explain(&self, record: RecordId) -> Result<Option<Explanation>, ErError>;
}

/// Keeps the original records alongside the entities built from them.
///
/// Not persistence — nothing here writes to disk. It is the retention contract:
/// the raw values stay addressable for as long as any entity refers to them.
#[derive(Debug, Clone, Default)]
pub struct RecordArchive {
    records: Vec<SourceRecord>,
}

impl RecordArchive {
    /// An empty archive.
    pub fn empty() -> Self {
        Self::default()
    }

    /// Retains a record.
    pub fn retain(&mut self, record: SourceRecord) {
        self.records.push(record);
    }

    /// The retained record.
    pub fn get(&self, id: RecordId) -> Option<&SourceRecord> {
        self.records.iter().find(|r| r.id == id)
    }

    /// Every retained record from one source.
    pub fn from_source(&self, source: crate::er::ingestion::SourceId) -> Vec<&SourceRecord> {
        self.records
            .iter()
            .filter(|r| r.id.source == source)
            .collect()
    }

    /// Number of retained records.
    pub fn len(&self) -> usize {
        self.records.len()
    }

    /// Whether nothing is retained.
    pub fn is_empty(&self) -> bool {
        self.records.is_empty()
    }
}