mod blocking;
mod comparison;
mod normalization;
mod python;
mod scoring;
mod types;

pub use blocking::{BlockingKey, CandidatePair, build_keys, find_candidates};
pub use comparison::{
    compare, compare_exact, compare_jaro_winkler, compare_levenshtein, compare_normalized_exact,
    compare_token_similarity,
};
pub use normalization::normalize;
pub use scoring::{FieldWeight, ScoreConfig, score};
pub use types::{
    ComparisonMethod, ComparisonResult, EvidenceItem, ResolutionLabel, ResolutionResult,
};

pub(crate) use python::register;
