#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ComparisonMethod {
    Exact,
    NormalizedExact,
    Levenshtein,
    JaroWinkler,
    TokenSimilarity,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ResolutionLabel {
    Match,
    NotMatch,
    Uncertain,
}

#[derive(Debug, Clone, PartialEq)]
pub struct ComparisonResult {
    pub method: ComparisonMethod,
    pub left: String,
    pub right: String,
    pub score: f64,
}

#[derive(Debug, Clone, PartialEq)]
pub struct EvidenceItem {
    pub field: String,
    pub method: ComparisonMethod,
    pub score: f64,
    pub left_value: Option<String>,
    pub right_value: Option<String>,
}

#[derive(Debug, Clone, PartialEq)]
pub struct ResolutionResult {
    pub label: ResolutionLabel,
    pub score: f64,
    pub evidence: Vec<EvidenceItem>,
    pub entity_id: Option<String>,
}
