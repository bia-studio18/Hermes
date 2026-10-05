//! Learning from feedback, without learning history away.
//!
//! Every learned artefact is versioned. That is the whole design constraint:
//! a resolver that silently changes its weights will quietly re-resolve
//! differently than it did yesterday, and there is no way to explain the
//! difference after the fact. A version stamp on every decision is what makes
//! that recoverable.

use std::collections::BTreeMap;

use crate::er::candidate::RecordId;
use crate::er::entity::EntityId;
use crate::er::matching::{FieldRule, ScoringMethod};
use crate::er::ErError;

use super::feedback::Feedback;

/// A fitted, versioned artefact.
#[derive(Debug, Clone, PartialEq)]
pub struct LearningModel {
    /// Increments on every fit. Stamped onto every decision made under it.
    pub version: u32,
    pub kind: ModelKind,
    /// Field weights learned from past decisions.
    pub field_weights: BTreeMap<String, f64>,
    /// Per-source trust in 0.0..=1.0.
    pub source_reliability: BTreeMap<u64, f64>,
    pub scoring: ScoringMethod,
}

/// What kind of thing was learned.
#[derive(Debug, Clone, PartialEq)]
pub enum ModelKind {
    /// Field weights, source trust, nothing more.
    FieldWeights,
    /// Alias and abbreviation tables per source.
    AliasTable,
    /// An embedding index for approximate matching.
    EmbeddingIndex,
    /// A learned combination of evidence into a score.
    LearnedScoring,
    /// Any combination of the above.
    Ensemble(Vec<ModelKind>),
}

impl LearningModel {
    /// A model that has learned nothing yet. Resolving with it is identical to
    /// resolving without one, which is what makes learning optional.
    pub fn untrained() -> Self {
        Self {
            version: 0,
            kind: ModelKind::FieldWeights,
            field_weights: BTreeMap::new(),
            source_reliability: BTreeMap::new(),
            scoring: ScoringMethod::WeightedMean,
        }
    }

    /// The weight for `field`, falling back to `default`.
    pub fn weight_for(&self, field: &str, default: f64) -> f64 {
        self.field_weights.get(field).copied().unwrap_or(default)
    }

    /// The field rules with learned weights applied.
    pub fn weighted_rules(&self, rules: &[FieldRule]) -> Vec<FieldRule> {
        rules
            .iter()
            .map(|rule| {
                let mut rule = rule.clone();
                rule.weight = self.weight_for(&rule.field, rule.weight);
                rule
            })
            .collect()
    }

    /// Whether anything has actually been learned.
    pub fn is_trained(&self) -> bool {
        self.version > 0
    }
}

/// Fits a [`LearningModel`] from feedback.
///
/// Kept separate from the resolver so a run can be reproduced: fit the model
/// from a feedback set, then resolve with that exact version.
pub trait Learning {
    /// Fits a new version from `feedback` and returns it.
    fn fit(&mut self, _feedback: &[Feedback]) -> Result<LearningModel, ErError>;

    /// Re-evaluates previously decided pairs, for measuring whether a new
    /// version would have decided differently.
    fn evaluate(
        &self,
        ___model: &LearningModel,
        ___pairs: &[(RecordId, EntityId)],
    ) -> Result<f64, ErError> {
        todo!()
    }
}

/// Learns field weights and source trust from accepted and rejected matches.
///
/// The honest default: no ML, no embeddings, just counts. If a learned model
/// cannot beat this, the feedback is not informative enough to justify one.
#[derive(Debug, Clone, Default)]
pub struct FeedbackWeights;

impl Learning for FeedbackWeights {
    fn fit(&mut self, __feedback: &[Feedback]) -> Result<LearningModel, ErError> {
        todo!()
    }
}

/// Learns nothing, so a run can opt out of learning without branching.
#[derive(Debug, Clone, Default)]
pub struct NoLearning;

impl Learning for NoLearning {
    fn fit(&mut self, _feedback: &[Feedback]) -> Result<LearningModel, ErError> {
        Ok(LearningModel::untrained())
    }
}