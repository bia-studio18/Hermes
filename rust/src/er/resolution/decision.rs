//! What the resolver concluded, and on what grounds.
//!
//! [`ResolutionDecision`] is the hinge of the whole system, and
//! `Uncertain` is the variant that matters most. A resolver that only says match
//! or no-match has to invent an answer in the middle; making the middle a
//! first-class outcome is what keeps borderline cases out of the entity store,
//! where a wrong merge contaminates everything downstream.

use crate::er::entity::EntityId;
use crate::er::matching::Confidence;
use crate::er::matching::MatchEvidence;

/// The three outcomes, and nothing else.
#[derive(Debug, Clone, PartialEq)]
pub enum ResolutionDecision {
    /// Same entity as `entity`.
    Match {
        entity: EntityId,
        confidence: Confidence,
    },
    /// A different entity: create one.
    NoMatch {
        confidence: Confidence,
    },
    /// Not enough to decide. Goes to review, never to the store.
    Uncertain {
        /// Best candidate first, best last.
        candidates: Vec<(EntityId, Confidence)>,
        confidence: Confidence,
    },
}

impl ResolutionDecision {
    /// The entity this record was assigned to, if any.
    pub fn matched_entity(&self) -> Option<EntityId> {
        match self {
            ResolutionDecision::Match { entity, .. } => Some(*entity),
            _ => None,
        }
    }

    /// Whether the decision may be written to the store without review.
    pub fn is_actionable(&self) -> bool {
        !matches!(self, ResolutionDecision::Uncertain { .. })
    }

    /// The confidence behind the decision, whichever variant it is.
    pub fn confidence(&self) -> &Confidence {
        match self {
            ResolutionDecision::Match { confidence, .. }
            | ResolutionDecision::NoMatch { confidence }
            | ResolutionDecision::Uncertain { confidence, .. } => confidence,
        }
    }
}

/// Why a record was not matched, when that is worth recording.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum NoMatchReason {
    /// No candidate was generated at all.
    NoCandidates,
    /// Candidates existed and every one scored below the threshold.
    BelowThreshold,
    /// A required identifier contradicted.
    IdentifierConflict,
    /// Candidates existed but all were rejected for another reason.
    Rejected(String),
}

/// Thresholds a confidence is compared against to become a decision.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Thresholds {
    /// At or above this, link automatically.
    pub link: f64,
    /// At or above this but below `link`, send to review.
    pub review: f64,
}

impl Default for Thresholds {
    fn default() -> Self {
        Self {
            link: 0.90,
            review: 0.60,
        }
    }
}

impl Thresholds {
    /// Turns a confidence into a decision for the best candidate found.
    ///
    /// Thresholds are inclusive at the top and exclusive below, so exactly one
    /// of the three branches applies to any confidence.
    pub fn classify(
        &self,
        __best: Option<(EntityId, Confidence)>,
        __evidence: &MatchEvidence,
    ) -> ResolutionDecision {
        todo!()
    }
}