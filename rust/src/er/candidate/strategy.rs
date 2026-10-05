//! How candidate pairs are narrowed down.
//!
//! The point of this stage is volume: resolution is only affordable because
//! almost every pair is discarded before it is ever compared. A strategy is
//! therefore a *key* plus the comparison that key implies — cheap and lossy by
//! design, with recall measured separately from precision.

use crate::er::schema::FieldSemantic;

/// A canonical key derived from one field of a record.
#[derive(Debug, Clone)]
pub enum BlockingKey {
    /// The value as normalized, no transformation.
    Exact(String),
    /// First `n` characters.
    Prefix(String, usize),
    /// Last `n` characters.
    Suffix(String, usize),
    /// Soundex- or Metaphone-style code.
    Phonetic(String),
    /// Set of character n-grams, sorted.
    NGrams(Vec<String>),
    /// Band hash for approximate string matching.
    BandHash(u64),
    /// Fixed-length vector reduced to one bucket.
    Lsh(u64),
}

/// Which field a key is built from, and how.
#[derive(Debug, Clone)]
pub enum KeySpec {
    /// Build the key from every field with this semantic.
    Semantic(FieldSemantic),
    /// Build it from this column name.
    Field(String),
    /// Build it from several columns at once, e.g. surname + postcode.
    Composite(Vec<String>),
}

/// One way of producing comparable buckets.
#[derive(Debug, Clone)]
pub struct BlockingStrategy {
    pub name: String,
    pub key: KeySpec,
    pub rule: BlockingRule,
}

impl BlockingStrategy {
    /// A strategy description.
    pub fn new(name: impl Into<String>, key: KeySpec, rule: BlockingRule) -> Self {
        Self {
            name: name.into(),
            key,
            rule,
        }
    }

    /// Exact match on one field: the cheapest strategy, the usual default.
    pub fn exact_on(field: impl Into<String>) -> Self {
        Self::new("exact", KeySpec::Field(field.into()), BlockingRule::Exact)
    }

    /// Phonetic buckets on one field, for names that are spelled differently
    /// but pronounced the same.
    pub fn phonetic_on(field: impl Into<String>) -> Self {
        Self::new("phonetic", KeySpec::Field(field.into()), BlockingRule::Phonetic)
    }
}

/// The transformation applied to a value to get its key.
#[derive(Debug, Clone)]
pub enum BlockingRule {
    Exact,
    Prefix(usize),
    Suffix(usize),
    Phonetic,
    NGrams(usize),
    /// Bounded neighbourhood: keys within this edit distance are candidates.
    EditDistance(u32),
    /// Buckets derived from an embedding index.
    Vector { bands: usize, rows: usize },
    /// Emit the union of several strategies' candidates.
    Union(Vec<BlockingStrategy>),
}