//! Driving the pipeline: candidate pairs in, decisions out.
//!
//! [`Resolver`] is the orchestrator every other stage plugs into, and it owns
//! no logic of its own beyond ordering: generate candidates, match them,
//! classify, and hand the results to the entity store. Anything it decides is
//! recorded so the store can be updated without the resolver running again.

use crate::er::candidate::{CandidateGenerator, RecordId};
use crate::er::ingestion::IngestedDataset;
use crate::er::matching::{Matcher, MatchingStrategy, RecordView};
use crate::er::ErError;

use super::decision::{ResolutionDecision, Thresholds};
use super::result::{EntityAction, ResolutionReport, ResolutionResult};

/// The default pipeline: one generator, one matcher, one set of thresholds.
///
/// Held as a struct rather than a free function because every part of it is
/// replaceable, and a caller who only wants `resolve(data)` should not have to
/// learn that.
#[derive(Default)]
pub struct Resolver {
    generator: Option<Box<dyn CandidateGenerator>>,
    matcher: Option<Box<dyn Matcher>>,
    thresholds: Thresholds,
    /// Bumped whenever the configuration changes, and stamped onto every
    /// decision so a result can be tied to the settings that produced it.
    model_version: u32,
}

impl Resolver {
    /// A resolver with automatic configuration: the caller supplies no stages
    /// and the pipeline picks defaults. This is the mode the Python
    /// `hermes.resolve(data)` API runs in.
    pub fn automatic() -> Self {
        Self::default()
    }

    /// A resolver using `generator` for candidate generation.
    pub fn with_generator(mut self, generator: Box<dyn CandidateGenerator>) -> Self {
        self.generator = Some(generator);
        self
    }

    /// A resolver using `matcher`.
    pub fn with_matcher(mut self, matcher: Box<dyn Matcher>) -> Self {
        self.matcher = Some(matcher);
        self
    }

    /// A resolver using `thresholds` to classify confidences.
    pub fn with_thresholds(mut self, thresholds: Thresholds) -> Self {
        self.thresholds = thresholds;
        self
    }

    /// A resolver using `strategy` for matching, discarding any matcher set.
    pub fn with_matching_strategy(self, strategy: MatchingStrategy) -> Self {
        self.with_matcher(Box::new(crate::er::matching::RuleBasedMatcher::new(
            strategy.rules().into_iter().cloned().collect(),
            crate::er::matching::ScoringMethod::WeightedMean,
        )))
    }

    /// The thresholds in force.
    pub fn thresholds(&self) -> &Thresholds {
        &self.thresholds
    }

    /// The version stamped onto decisions.
    pub fn model_version(&self) -> u32 {
        self.model_version
    }

    /// Resolves one record against the entities already in `existing`.
    pub fn resolve_record(
        &mut self,
        _record: RecordId,
        __record_view: &RecordView,
        __existing: &mut dyn crate::er::entity::EntityStore,
    ) -> Result<ResolutionResult, ErError> {
        todo!()
    }

    /// Resolves every record of `dataset` into `existing`.
    pub fn resolve_all(
        &mut self,
        _dataset: &IngestedDataset,
        _existing: &mut dyn crate::er::entity::EntityStore,
    ) -> Result<ResolutionReport, ErError> {
        todo!()
    }
}

/// Resolves `dataset` with the default configuration.
///
/// The one-line entry point the Python API wraps. Automatic configuration is the
/// default, not a shortcut: an explicit [`Resolver`] is available when the
/// defaults are wrong, never required to get started.
pub fn resolve(
    dataset: &IngestedDataset,
    existing: &mut dyn crate::er::entity::EntityStore,
) -> Result<ResolutionReport, ErError> {
    Resolver::automatic().resolve_all(dataset, existing)
}

/// The outcome of a decision before it is applied to the store.
pub fn action_for(_decision: &ResolutionDecision) -> EntityAction {
    todo!()
}