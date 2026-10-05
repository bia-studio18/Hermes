//! Comparing a candidate pair.
//!
//! The matcher is the only stage that reads field values. It receives values
//! that normalization has already canonicalized, compares them with the
//! configured comparators, and reports evidence. It does not decide, and it
//! never sees an entity — only records, because "record vs record" and "record
//! vs entity" are the same comparison once the entity's values are read.

use crate::er::value::Value;
use crate::er::ErError;

use super::evidence::{FieldEvidence, MatchEvidence};
use super::score::{Comparator, Confidence, FieldRule, MatchScore, ScoringMethod};

/// The values of one record, by field name.
#[derive(Debug, Clone, Default)]
pub struct RecordView {
    pub fields: Vec<(String, Value)>,
}

impl RecordView {
    /// A view over `fields`, in schema order.
    pub fn new(fields: Vec<(String, Value)>) -> Self {
        Self { fields }
    }

    /// The value of `field`, if the record has it.
    pub fn get(&self, field: &str) -> Option<&Value> {
        self.fields
            .iter()
            .find(|(name, _)| name == field)
            .map(|(_, value)| value)
    }

    /// A view holding only `fields`, for comparing one block of columns.
    pub fn project(&self, fields: &[String]) -> RecordView {
        RecordView::new(
            self.fields
                .iter()
                .filter(|(name, _)| fields.contains(name))
                .cloned()
                .collect(),
        )
    }
}

/// One configurable way of comparing pairs.
#[derive(Debug, Clone)]
pub enum MatchingStrategy {
    /// Compare the configured fields and aggregate their evidence.
    RuleBased {
        rules: Vec<FieldRule>,
        scoring: ScoringMethod,
    },
    /// Always compare, never block: correctness baseline, unusable at scale.
    Exhaustive {
        rules: Vec<FieldRule>,
    },
    /// Match only on exact strong identifiers.
    IdentifierOnly,
    /// Combine several strategies and take the strongest evidence.
    Ensemble(Vec<MatchingStrategy>),
}

impl MatchingStrategy {
    /// The name recorded in provenance.
    pub fn as_str(&self) -> &'static str {
        match self {
            MatchingStrategy::RuleBased { .. } => "rule_based",
            MatchingStrategy::Exhaustive { .. } => "exhaustive",
            MatchingStrategy::IdentifierOnly => "identifier_only",
            MatchingStrategy::Ensemble(_) => "ensemble",
        }
    }

    /// The field rules this strategy compares.
    pub fn rules(&self) -> Vec<&FieldRule> {
        match self {
            MatchingStrategy::RuleBased { rules, .. }
            | MatchingStrategy::Exhaustive { rules } => rules.iter().collect(),
            MatchingStrategy::IdentifierOnly | MatchingStrategy::Ensemble(_) => Vec::new(),
        }
    }
}

/// Compares two record views into evidence.
///
/// `Send + Sync` for the same reason as `CandidateGenerator`: a resolver held by
/// a PyO3 class may cross threads.
pub trait Matcher: Send + Sync {
    /// Compares one pair and reports the evidence behind the score.
    fn compare(
        &self,
        left: &RecordView,
        right: &RecordView,
    ) -> Result<MatchEvidence, ErError>;

    /// Compares one pair and reports only the decision-relevant numbers.
    fn score(
        &self,
        left: &RecordView,
        right: &RecordView,
    ) -> Result<(MatchScore, Confidence), ErError> {
        let evidence = self.compare(left, right)?;
        let confidence = Confidence::from_score(&evidence.score);
        Ok((evidence.score, confidence))
    }
}

/// Compares the configured fields, one [`FieldRule`] at a time.
pub struct RuleBasedMatcher {
    rules: Vec<FieldRule>,
    scoring: ScoringMethod,
}

impl RuleBasedMatcher {
    /// A matcher over `rules`, aggregating with `scoring`.
    pub fn new(rules: Vec<FieldRule>, scoring: ScoringMethod) -> Self {
        Self { rules, scoring }
    }

    /// The rules this matcher applies.
    pub fn rules(&self) -> &[FieldRule] {
        &self.rules
    }

    /// How field evidence is aggregated into one score.
    pub fn scoring(&self) -> ScoringMethod {
        self.scoring
    }
}

impl Matcher for RuleBasedMatcher {
    fn compare(
        &self,
        __left: &RecordView,
        __right: &RecordView,
    ) -> Result<MatchEvidence, ErError> {
        todo!()
    }
}

/// Matches on strong identifiers only. Cheapest matcher, and the one used to
/// bootstrap identifiers before anything else is known.
pub struct IdentifierMatcher;

impl Matcher for IdentifierMatcher {
    fn compare(
        &self,
        _left: &RecordView,
        _right: &RecordView,
    ) -> Result<MatchEvidence, ErError> {
        todo!()
    }
}

/// Compares one field with one comparator, outside any aggregation.
///
/// Exposed so blocking, review queues and feedback tooling can reuse the same
/// comparison the matcher uses.
pub fn compare_field(
    _field: &str,
    _comparator: &Comparator,
    _left: &Value,
    _right: &Value,
    _weight: f64,
) -> Result<FieldEvidence, ErError> {
    todo!()
}