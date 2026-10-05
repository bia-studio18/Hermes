//! Turning per-field evidence into one number, and one number into a decision.
//!
//! Two different things live here on purpose, and they are not the same value:
//!
//! * [`MatchScore`] is evidence-derived, in 0.0..=1.0.
//! * [`Confidence`] is score plus history and prior, and is what the decision
//!   thresholds are compared against.
//!
//! Collapsing them early is how a resolver ends up over-confident on the first
//! record it has ever seen.

use crate::er::similarity::SimilarityScore;
use crate::er::value::Value;

use super::evidence::FieldEvidence;

/// How field scores combine into one pair score.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ScoringMethod {
    /// Sum of weight × score, over the total weight. Missing fields drop out
    /// instead of counting as zero.
    WeightedMean,
    /// The single best field, ignoring the rest. Useful for strong identifiers.
    BestField,
    /// Weighted mean, but a `Conflict` vetoes the whole pair.
    WeightedMeanVeto,
    /// Combination learned from feedback.
    Learned,
}

impl ScoringMethod {
    /// The name recorded in provenance and explainability output.
    pub fn as_str(&self) -> &'static str {
        match self {
            ScoringMethod::WeightedMean => "weighted_mean",
            ScoringMethod::BestField => "best_field",
            ScoringMethod::WeightedMeanVeto => "weighted_mean_veto",
            ScoringMethod::Learned => "learned",
        }
    }
}

/// Evidence-derived similarity for one pair.
#[derive(Debug, Clone, PartialEq)]
pub struct MatchScore {
    /// 0.0..=1.0.
    pub score: f64,
    /// Weight of the fields that contributed, for reporting.
    pub weight: f64,
    pub method: ScoringMethod,
}

impl MatchScore {
    /// A score with an explicit aggregation method.
    pub fn new(score: f64, weight: f64, method: ScoringMethod) -> Self {
        Self {
            score,
            weight,
            method,
        }
    }

    /// A score from one field, weighted by that field's weight.
    pub fn from_field(field: &FieldEvidence) -> Self {
        Self::new(field.score, field.weight, ScoringMethod::BestField)
    }

    /// Adapts the existing similarity result type, so per-field comparators
    /// report in the same shape as the value-level algorithms.
    pub fn from_similarity(similarity: SimilarityScore, weight: f64) -> Self {
        Self::new(similarity.score, weight, ScoringMethod::WeightedMean)
    }

    /// Whether the score is within `0.0..=1.0`. Every score must be.
    pub fn is_valid(&self) -> bool {
        (0.0..=1.0).contains(&self.score)
    }
}

/// How much to trust the outcome, beyond the evidence.
#[derive(Debug, Clone, PartialEq)]
pub struct Confidence {
    /// 0.0..=1.0.
    pub confidence: f64,
    /// How the confidence was arrived at, for explainability.
    pub basis: ConfidenceBasis,
}

impl Confidence {
    /// Confidence taken straight from the evidence, with no history.
    pub fn from_score(score: &MatchScore) -> Self {
        Self {
            confidence: score.score,
            basis: ConfidenceBasis::EvidenceOnly,
        }
    }

    /// Confidence adjusted by prior history. `None` means "no adjustment
    /// available", not "no adjustment needed" — the basis records which.
    pub fn adjusted(confidence: f64, basis: ConfidenceBasis) -> Self {
        Self { confidence, basis }
    }

    /// Whether the confidence is in range.
    pub fn is_valid(&self) -> bool {
        (0.0..=1.0).contains(&self.confidence)
    }
}

/// What a confidence figure is resting on.
#[derive(Debug, Clone, PartialEq)]
pub enum ConfidenceBasis {
    /// Evidence only: nothing is known about either side yet.
    EvidenceOnly,
    /// Adjusted by how this source has performed historically.
    SourceReliability(f64),
    /// Adjusted by previous decisions on this pair or entity.
    PriorDecisions(u32),
    /// Combination of the above.
    Combined(Vec<ConfidenceBasis>),
}

/// Which fields to compare, and how.
#[derive(Debug, Clone)]
pub struct FieldRule {
    pub field: String,
    /// Weight in the aggregate score.
    pub weight: f64,
    /// Value comparison to run. `None` for a rule-based field.
    pub comparator: Option<Comparator>,
    /// Whether the field must agree for a match. Vetoes the pair when it does not.
    pub required: bool,
}

impl FieldRule {
    /// A weighted field compared with `comparator`.
    pub fn weighted(field: impl Into<String>, comparator: Comparator, weight: f64) -> Self {
        Self {
            field: field.into(),
            weight,
            comparator: Some(comparator),
            required: false,
        }
    }

    /// A field that must agree: a strong identifier.
    pub fn required(field: impl Into<String>, comparator: Comparator) -> Self {
        Self {
            field: field.into(),
            weight: 1.0,
            comparator: Some(comparator),
            required: true,
        }
    }
}

/// The value comparison to run, reusing the existing similarity algorithms
/// rather than adding a parallel set.
#[derive(Debug, Clone)]
pub enum Comparator {
    /// [`crate::er::similarity::exact_similarity`]
    Exact,
    /// [`crate::er::similarity::levenshtein_similarity`]
    Levenshtein,
    /// [`crate::er::similarity::jaro_similarity`]
    Jaro,
    /// [`crate::er::similarity::jaro_winkler_similarity`]
    JaroWinkler,
    /// [`crate::er::similarity::damerau_levenshtein_similarity`]
    DamerauLevenshtein,
    /// [`crate::er::similarity::token_similarity`]
    Token(crate::er::similarity::TokenAlgo),
    /// [`crate::er::similarity::date_similarity`]
    Date(crate::er::similarity::DateAlgo),
    /// [`crate::er::similarity::email_similarity`]
    Email(crate::er::similarity::EmailAlgo),
    /// [`crate::er::similarity::phone_similarity`]
    Phone(crate::er::similarity::PhoneAlgo),
    /// [`crate::er::similarity::numeric_similarity`]
    Numeric(crate::er::similarity::NumericAlgo),
}

impl Comparator {
    /// The algorithm name recorded on the evidence.
    pub fn method_name(&self) -> &'static str {
        match self {
            Comparator::Exact => "exact_similarity",
            Comparator::Levenshtein => "levenshtein_similarity",
            Comparator::Jaro => "jaro_similarity",
            Comparator::JaroWinkler => "jaro_winkler_similarity",
            Comparator::DamerauLevenshtein => "damerau_levenshtein_similarity",
            Comparator::Token(_) => "token_similarity",
            Comparator::Date(_) => "date_similarity",
            Comparator::Email(_) => "email_similarity",
            Comparator::Phone(_) => "phone_similarity",
            Comparator::Numeric(_) => "numeric_similarity",
        }
    }

    /// Compares two canonical values. The one place a comparator is applied.
    pub fn compare(&self, _left: &Value, _right: &Value) -> Result<f64, crate::er::ErError> {
        todo!()
    }
}