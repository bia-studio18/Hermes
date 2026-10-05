//! Narrowing records to the pairs worth comparing.

mod generator;
mod strategy;

pub use generator::{
    BlockingGenerator, Candidate, CandidateGenerator, CandidateSet, CompositeGenerator, RecordId,
};
pub use strategy::{BlockingKey, BlockingRule, BlockingStrategy, KeySpec};