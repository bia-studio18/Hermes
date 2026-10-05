//! What one record's resolution produced.
//!
//! A result carries the decision *and* what should happen to the store, because
//! those are decided together: `Uncertain` implies `Queue`, and letting the two
/// disagree is how undecided records end up merged.

use crate::er::candidate::RecordId;
use crate::er::entity::EntityId;
use crate::er::matching::MatchEvidence;
use crate::er::provenance::Provenance;

use super::decision::{NoMatchReason, ResolutionDecision};

/// What the store should do with a resolved record.
#[derive(Debug, Clone, PartialEq)]
pub enum EntityAction {
    /// Fold the record into an existing entity.
    Link(EntityId),
    /// Nothing matched; create a new entity and link into it.
    Create,
    /// Nothing matched and creation is suppressed, e.g. the record failed a
    /// quality gate.
    Discard(NoMatchReason),
    /// Human review needed before the store changes.
    Queue,
}

/// One record's outcome.
#[derive(Debug, Clone, PartialEq)]
pub struct ResolutionResult {
    pub record: RecordId,
    pub decision: ResolutionDecision,
    pub action: EntityAction,
    pub evidence: MatchEvidence,
    pub provenance: Option<Provenance>,
    /// Configuration version the decision was taken under.
    pub model_version: Option<u32>,
}

impl ResolutionResult {
    /// A result with no evidence yet.
    pub fn pending(record: RecordId, decision: ResolutionDecision) -> Self {
        Self {
            record,
            decision,
            action: EntityAction::Queue,
            evidence: MatchEvidence::new(
                Vec::new(),
                crate::er::matching::MatchScore::new(
                    0.0,
                    0.0,
                    crate::er::matching::ScoringMethod::WeightedMean,
                ),
            ),
            provenance: None,
            model_version: None,
        }
    }

    /// The entity the record was assigned to, if any.
    pub fn assigned_entity(&self) -> Option<EntityId> {
        self.decision.matched_entity()
    }

    /// Whether this result can be written to the store without review.
    pub fn is_actionable(&self) -> bool {
        !matches!(self.action, EntityAction::Queue)
    }
}

/// Everything one resolve pass produced.
#[derive(Debug, Clone, Default, PartialEq)]
pub struct ResolutionReport {
    pub results: Vec<ResolutionResult>,
}

impl ResolutionReport {
    /// An empty report.
    pub fn empty() -> Self {
        Self::default()
    }

    /// Adds a result.
    pub fn push(&mut self, result: ResolutionResult) {
        self.results.push(result);
    }

    /// Results matching a decision.
    pub fn by_decision<'a>(
        &'a self,
        predicate: impl Fn(&'a ResolutionResult) -> bool,
    ) -> Vec<&'a ResolutionResult> {
        self.results.iter().filter(|r| predicate(r)).collect()
    }

    /// Results headed for review. The review queue.
    pub fn queued(&self) -> Vec<&ResolutionResult> {
        self.by_decision(|r| !r.is_actionable())
    }

    /// Records that were linked to an existing entity.
    pub fn linked(&self) -> Vec<&ResolutionResult> {
        self.by_decision(|r| matches!(r.action, EntityAction::Link(_)))
    }

    /// Number of results.
    pub fn len(&self) -> usize {
        self.results.len()
    }

    /// Whether the pass resolved nothing.
    pub fn is_empty(&self) -> bool {
        self.results.is_empty()
    }
}