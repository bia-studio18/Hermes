use crate::er::types::{EvidenceItem, ResolutionResult};

#[derive(Debug, Clone, PartialEq)]
pub struct FieldWeight {
    pub field: String,
    pub weight: f64,
}

#[derive(Debug, Clone, PartialEq)]
pub struct ScoreConfig {
    pub match_threshold: f64,
    pub uncertain_threshold: f64,
    pub field_weights: Vec<FieldWeight>,
}

pub fn score(_evidence: &[EvidenceItem], _config: &ScoreConfig) -> ResolutionResult {
    unimplemented!("resolution scoring")
}
