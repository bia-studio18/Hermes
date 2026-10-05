//! One place to configure the pipeline.
//!
//! [`ErConfig::default`] is meant to be usable as-is: automatic inference and
//! automatic strategy choice are the defaults, not a mode you have to opt out
//! of. Every field here overrides something the pipeline would otherwise infer,
//! which is why they are all optional-ish (`Option`, or empty collections).
//!
//! Nothing in this module *does* anything. It holds settings; the stages read
//! them.

use crate::er::candidate::{BlockingRule, BlockingStrategy, KeySpec};
use crate::er::ingestion::DEFAULT_BATCH_SIZE;
use crate::er::matching::{FieldRule, ScoringMethod};
use crate::er::normalization::{NormalizationRule, NormalizationRules};
use crate::er::resolution::Thresholds;
use crate::er::schema::FieldSemantic;

/// Everything the pipeline needs, and nothing it does not.
#[derive(Debug, Clone, Default)]
pub struct ErConfig {
    pub ingestion: IngestionConfig,
    pub schema: SchemaConfig,
    pub normalization: NormalizationConfig,
    pub candidate: CandidateConfig,
    pub matching: MatchingConfig,
    pub resolution: ResolutionConfig,
}

impl ErConfig {
    /// The defaults, which inference then refines.
    pub fn new() -> Self {
        Self::default()
    }

    /// Checks the settings that can be checked without touching data.
    pub fn validate(&self) -> Result<(), crate::er::ErError> {
        if self.resolution.thresholds.review > self.resolution.thresholds.link {
            return Err(crate::er::ErError::Configuration(
                "review threshold must not exceed the link threshold".to_string(),
            ));
        }
        if self.ingestion.batch_size == 0 {
            return Err(crate::er::ErError::Configuration(
                "batch size must be greater than zero".to_string(),
            ));
        }
        Ok(())
    }
}

/// Reading and framing.
#[derive(Debug, Clone)]
pub struct IngestionConfig {
    pub batch_size: usize,
    /// Rows to sample per column before a type is declared.
    pub sample_size: usize,
    /// Keep records that failed to parse, tagged instead of dropped.
    pub keep_malformed: bool,
}

impl Default for IngestionConfig {
    fn default() -> Self {
        Self {
            batch_size: DEFAULT_BATCH_SIZE,
            sample_size: 1_000,
            keep_malformed: false,
        }
    }
}

/// Schema and semantic inference.
#[derive(Debug, Clone)]
pub struct SchemaConfig {
    /// Fixed entity type, when the caller knows it and inference should not
    /// guess.
    pub entity_type: Option<String>,
    /// Caller-declared meanings, applied over inference.
    pub field_hints: Vec<crate::er::schema::FieldHint>,
    /// Below this confidence a semantic stays `Unknown`.
    pub min_confidence: f64,
    /// At or above this a hint replaces inference outright.
    pub hint_override: f64,
}

impl Default for SchemaConfig {
    fn default() -> Self {
        Self {
            entity_type: None,
            field_hints: Vec::new(),
            min_confidence: 0.60,
            hint_override: 0.90,
        }
    }
}

/// Which rules a field gets, keyed by semantic.
#[derive(Debug, Clone, Default)]
pub struct NormalizationConfig {
    /// Rules for fields whose meaning is known.
    pub by_semantic: Vec<(FieldSemantic, NormalizationRules)>,
    /// Rules for fields whose meaning is unknown.
    pub fallback: NormalizationRules,
}

impl NormalizationConfig {
    /// The rules for `semantic`, or the fallback when nothing is declared.
    pub fn rules_for(&self, semantic: &FieldSemantic) -> &NormalizationRules {
        self.by_semantic
            .iter()
            .find(|(s, _)| s == semantic)
            .map(|(_, rules)| rules)
            .unwrap_or(&self.fallback)
    }

    /// The default rule set for free-text fields.
    pub fn text_defaults() -> NormalizationRules {
        NormalizationRules::new(vec![
            NormalizationRule::UnicodeCasefold,
            NormalizationRule::Whitespace,
        ])
    }
}

/// Candidate generation.
#[derive(Debug, Clone)]
pub struct CandidateConfig {
    /// Strategies to run, unioned. Empty means "choose automatically".
    pub strategies: Vec<BlockingStrategy>,
    /// Largest block to compare. Bigger blocks are truncated, so this caps cost
    /// per pass at the cost of recall.
    pub max_block_size: usize,
    /// Refuse to emit a strategy that generates more than this many candidates
    /// per record. A backstop against a badly chosen blocking rule.
    pub max_candidates_per_record: usize,
}

impl Default for CandidateConfig {
    fn default() -> Self {
        Self {
            strategies: vec![BlockingStrategy::new(
                "exact",
                KeySpec::Semantic(FieldSemantic::SourceIdentifier),
                BlockingRule::Exact,
            )],
            max_block_size: 100,
            max_candidates_per_record: 50,
        }
    }
}

/// Field comparison and score aggregation.
#[derive(Debug, Clone)]
pub struct MatchingConfig {
    /// Fields to compare and how. Empty means "choose from the schema".
    pub rules: Vec<FieldRule>,
    pub scoring: ScoringMethod,
    /// Source trust, when known. Absent means "no adjustment", not "neutral".
    pub source_weights: Vec<(crate::er::ingestion::SourceId, f64)>,
}

impl Default for MatchingConfig {
    fn default() -> Self {
        Self {
            rules: Vec::new(),
            scoring: ScoringMethod::WeightedMean,
            source_weights: Vec::new(),
        }
    }
}

/// Thresholds and what to do with the middle.
#[derive(Debug, Clone, Default)]
pub struct ResolutionConfig {
    pub thresholds: Thresholds,
    /// Automatically merge entities that later evidence connects.
    pub auto_merge: bool,
    /// Stamp onto every decision, so a result can be tied to these settings.
    pub model_version: u32,
}