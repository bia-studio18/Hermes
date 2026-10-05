//! Why two records look alike, field by field.
//!
//! Evidence is the explainability surface: every decision downstream carries the
//! evidence that produced it, so a human can see which field agreed, which
//! disagreed, and what it scored. Nothing here decides anything — it only
//! reports.

use crate::er::value::Value;
use crate::er::ErError;

use super::score::{MatchScore, ScoringMethod};

/// One field's contribution to a pair comparison.
#[derive(Debug, Clone, PartialEq)]
pub struct FieldEvidence {
    /// Column the comparison ran on.
    pub field: String,
    /// Left value as it arrived.
    pub left: Value,
    /// Right value as it arrived.
    pub right: Value,
    /// Left canonical form, when normalization produced one.
    pub left_normalized: Option<Value>,
    /// Right canonical form, when normalization produced one.
    pub right_normalized: Option<Value>,
    /// What the comparison concluded.
    pub outcome: ComparisonOutcome,
    /// 0.0..=1.0 similarity for this field alone.
    pub score: f64,
    /// Contribution weight applied when aggregating.
    pub weight: f64,
    /// Algorithm that produced `score`, e.g. `levenshtein_similarity`.
    pub method: String,
}

impl FieldEvidence {
    /// A field whose two values are identical after normalization.
    pub fn exact(field: impl Into<String>, score: f64) -> Self {
        Self {
            field: field.into(),
            left: Value::Null,
            right: Value::Null,
            left_normalized: None,
            right_normalized: None,
            outcome: ComparisonOutcome::Equal,
            score,
            weight: 1.0,
            method: "exact_similarity".to_string(),
        }
    }

    /// Whether this evidence supports a match.
    pub fn supports_match(&self) -> bool {
        self.outcome.supports_match()
    }
}

/// How two values of one field compared.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ComparisonOutcome {
    /// Identical after normalization.
    Equal,
    /// Similar enough to count as partial agreement.
    Similar,
    /// Both values present and clearly different.
    Different,
    /// At least one side is null or unparsable. Never evidence *against* a
    /// match: absence of evidence is not contradiction.
    Missing,
    /// One side carries a strong identifier the other contradicts.
    Conflict,
    /// Compared by a rule rather than a value algorithm, e.g. a shared address
    /// component.
    Derived,
}

impl ComparisonOutcome {
    /// Whether this outcome argues for a match.
    pub fn supports_match(&self) -> bool {
        matches!(
            self,
            ComparisonOutcome::Equal | ComparisonOutcome::Similar | ComparisonOutcome::Derived
        )
    }

    /// Whether this outcome argues against one.
    pub fn contradicts_match(&self) -> bool {
        matches!(
            self,
            ComparisonOutcome::Different | ComparisonOutcome::Conflict
        )
    }
}

/// All field evidence for one candidate pair, and the score derived from it.
#[derive(Debug, Clone, PartialEq)]
pub struct MatchEvidence {
    pub fields: Vec<FieldEvidence>,
    pub score: MatchScore,
    /// Source reliability folded in by the scorer, when configured.
    pub source_reliability: Option<f64>,
}

impl MatchEvidence {
    /// Evidence over `fields`, scored by `method`.
    pub fn new(fields: Vec<FieldEvidence>, score: MatchScore) -> Self {
        Self {
            fields,
            score,
            source_reliability: None,
        }
    }

    /// Evidence for a single field, scored exactly.
    pub fn single(field: FieldEvidence) -> Self {
        let score = MatchScore::from_field(&field);
        Self::new(vec![field], score)
    }

    /// Evidence for the fields that argue against a match.
    pub fn contradictions(&self) -> impl Iterator<Item = &FieldEvidence> {
        self.fields
            .iter()
            .filter(|f| f.outcome.contradicts_match())
    }

    /// Aggregates the evidence with `method`.
    pub fn aggregate(&self, _method: ScoringMethod) -> Result<MatchScore, ErError> {
        todo!()
    }
}