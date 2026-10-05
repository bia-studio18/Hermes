//! Canonical values for comparison, keeping the raw value alongside.
//!
//! Normalization runs after schema inference because the rules a value gets
//! depend on what the column turned out to mean: a `phone` field and a
//! `date_of_birth` field look identical to the text normalizer and completely
//! different to everyone downstream.

mod normalizer;
mod rules;

pub use normalizer::{
    AddressNormalizer, NameNormalizer, NormalizationResult, Normalizer, PhoneNormalizer,
    RuleNormalizer, TextNormalizer,
};
pub use rules::{NormalizationRule, NormalizationRules};