//! Producing the pairs worth comparing, without comparing everything.
//!
//! Output is a [`CandidateSet`], not a stream of pairs, because a set can be
//! counted, sampled and scored — which is how candidate recall gets measured
//! separately from match precision.

use crate::er::ErError;

use super::strategy::BlockingStrategy;

/// Identifies a record inside a source, stable for the run.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub struct RecordId {
    pub source: crate::er::ingestion::SourceId,
    /// Batch index within the source.
    pub batch: usize,
    /// Row index within the batch.
    pub row: usize,
}

/// A pair that might be the same entity.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Candidate {
    pub left: RecordId,
    pub right: RecordId,
    /// Strategy that produced this pair. A pair found two ways is one
    /// candidate with two strategies, not two candidates.
    pub found_by: Vec<String>,
}

impl Candidate {
    /// A pair found by one strategy.
    pub fn new(left: RecordId, right: RecordId, strategy: impl Into<String>) -> Self {
        Self {
            left,
            right,
            found_by: vec![strategy.into()],
        }
    }

    /// Records the pair in canonical order so a pair is never emitted twice.
    pub fn ordered(mut self) -> Self {
        if self.left > self.right {
            std::mem::swap(&mut self.left, &mut self.right);
        }
        self
    }

    /// Whether this pair was already produced by `strategy`.
    pub fn found_by(&self, strategy: &str) -> bool {
        self.found_by.iter().any(|s| s == strategy)
    }
}

/// Every pair one generator pass produced, deduplicated.
#[derive(Debug, Clone, Default)]
pub struct CandidateSet {
    pub candidates: Vec<Candidate>,
    /// Records the generator examined. `generated / records` is the selectivity
    /// of the strategy, worth logging per run.
    pub examined: usize,
}

impl CandidateSet {
    /// An empty set.
    pub fn empty() -> Self {
        Self::default()
    }

    /// Adds a pair unless it is already present, merging strategy names.
    pub fn insert(&mut self, candidate: Candidate) {
        let candidate = candidate.ordered();
        match self
            .candidates
            .iter_mut()
            .find(|c| c.left == candidate.left && c.right == candidate.right)
        {
            Some(existing) => {
                for strategy in candidate.found_by {
                    if !existing.found_by.contains(&strategy) {
                        existing.found_by.push(strategy);
                    }
                }
            }
            None => self.candidates.push(candidate),
        }
    }

    /// Number of distinct pairs.
    pub fn len(&self) -> usize {
        self.candidates.len()
    }

    /// Whether no pair was produced.
    pub fn is_empty(&self) -> bool {
        self.candidates.is_empty()
    }

    /// Pairs found by a named strategy.
    pub fn by_strategy(&self, strategy: &str) -> impl Iterator<Item = &Candidate> {
        self.candidates
            .iter()
            .filter(move |c| c.found_by(strategy))
    }
}

/// Narrows records down to pairs worth comparing.
///
/// `Send + Sync` because a resolver built in Python may be moved and shared
/// across threads, the same reason `DatasetRepresentation` requires it.
pub trait CandidateGenerator: Send + Sync {
    /// Strategy this generator implements, recorded on every candidate.
    fn strategy(&self) -> &BlockingStrategy;

    /// Generates candidates for the records of one source against `existing`.
    ///
    /// `existing` is the set of records already known, so the same generator
    /// serves both deduplication (record vs record) and cross-source linking
    /// (record vs entity).
    fn generate(
        &self,
        records: &[RecordId],
        existing: &[RecordId],
    ) -> Result<CandidateSet, ErError>;
}

/// Exact-key blocking: the default, and the baseline every other strategy is
/// measured against.
pub struct BlockingGenerator {
    strategy: BlockingStrategy,
}

impl BlockingGenerator {
    /// A generator for `strategy`.
    pub fn new(strategy: BlockingStrategy) -> Self {
        Self { strategy }
    }

    /// Exact-key blocking on one field.
    pub fn exact_on(field: impl Into<String>) -> Self {
        Self::new(BlockingStrategy::exact_on(field))
    }
}

impl CandidateGenerator for BlockingGenerator {
    fn strategy(&self) -> &BlockingStrategy {
        &self.strategy
    }

    fn generate(
        &self,
        __records: &[RecordId],
        __existing: &[RecordId],
    ) -> Result<CandidateSet, ErError> {
        todo!()
    }
}

/// Runs several generators and unions their output.
pub struct CompositeGenerator {
    generators: Vec<Box<dyn CandidateGenerator>>,
}

impl CompositeGenerator {
    /// A generator combining `generators`.
    pub fn new(generators: Vec<Box<dyn CandidateGenerator>>) -> Self {
        Self { generators }
    }

    /// The strategies being combined.
    pub fn strategies(&self) -> Vec<&BlockingStrategy> {
        self.generators.iter().map(|g| g.strategy()).collect()
    }
}

impl CandidateGenerator for CompositeGenerator {
    fn strategy(&self) -> &BlockingStrategy {
        // No single strategy describes a union; name the union and let every
        // candidate carry its real strategy name instead.
        static UNION: std::sync::OnceLock<BlockingStrategy> = std::sync::OnceLock::new();
        UNION.get_or_init(|| {
            BlockingStrategy::new(
                "union",
                super::strategy::KeySpec::Composite(Vec::new()),
                super::strategy::BlockingRule::Union(Vec::new()),
            )
        })
    }

    fn generate(
        &self,
        __records: &[RecordId],
        __existing: &[RecordId],
    ) -> Result<CandidateSet, ErError> {
        todo!()
    }
}