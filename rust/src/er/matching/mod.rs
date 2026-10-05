//! Comparing candidate pairs and reporting the evidence.

mod evidence;
mod matcher;
mod score;

pub use evidence::{ComparisonOutcome, FieldEvidence, MatchEvidence};
pub use matcher::{compare_field, IdentifierMatcher, Matcher, MatchingStrategy, RecordView, RuleBasedMatcher};
pub use score::{Comparator, Confidence, ConfidenceBasis, FieldRule, MatchScore, ScoringMethod};