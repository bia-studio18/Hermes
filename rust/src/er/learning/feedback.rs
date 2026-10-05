//! What a human (or a caller) said about a decision.

use crate::er::candidate::RecordId;
use crate::er::entity::EntityId;
use crate::er::resolution::ResolutionDecision;

/// What kind of feedback this is.
#[derive(Debug, Clone, PartialEq)]
pub enum FeedbackType {
    /// A suggested match was right.
    AcceptedMatch {
        entity: EntityId,
    },
    /// A suggested match was wrong.
    RejectedMatch {
        entity: EntityId,
    },
    /// A `NoMatch` was wrong: these two are the same.
    ForcedMerge {
        entity: EntityId,
    },
    /// Two entities were wrongly merged and must be split.
    ForcedSplit {
        entity: EntityId,
    },
    /// The record belongs somewhere the pipeline did not put it.
    Relink {
        entity: EntityId,
    },
    /// A field means something the inference missed.
    FieldSemantic {
        field: String,
        meaning: crate::er::schema::FieldSemantic,
    },
    /// A source is more or less trustworthy than assumed.
    SourceReliability {
        source: crate::er::ingestion::SourceId,
        reliability: f64,
    },
}

/// One piece of feedback, attributable and dated.
#[derive(Debug, Clone, PartialEq)]
pub struct Feedback {
    pub kind: FeedbackType,
    /// The record the decision was about.
    pub record: RecordId,
    /// The decision being corrected, kept so a model can learn from what the
    /// pipeline said as well as from what the human said.
    pub previous: Option<ResolutionDecision>,
    /// Who gave it: a reviewer id, or `None` for programmatic feedback.
    pub reviewer: Option<String>,
    pub comment: Option<String>,
}

impl Feedback {
    /// Feedback with no reviewer attached, for programmatic sources.
    pub fn automated(kind: FeedbackType, record: RecordId) -> Self {
        Self {
            kind,
            record,
            previous: None,
            reviewer: None,
            comment: None,
        }
    }

    /// Attaches the reviewer.
    pub fn by(mut self, reviewer: impl Into<String>) -> Self {
        self.reviewer = Some(reviewer.into());
        self
    }

    /// Keeps the decision this feedback corrects.
    pub fn against(mut self, previous: ResolutionDecision) -> Self {
        self.previous = Some(previous);
        self
    }

    /// Whether the feedback would, if applied, split an entity. Splits are
    /// reviewed more carefully than merges because they undo history.
    pub fn is_destructive(&self) -> bool {
        matches!(self.kind, FeedbackType::ForcedSplit { .. })
    }
}