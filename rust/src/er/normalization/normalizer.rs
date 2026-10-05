//! Canonicalizing values so they can be compared.
//!
//! Two rules the whole stage obeys:
//!
//! * **Raw is never discarded.** [`NormalizationResult`] carries the input
//!   value next to its canonical form, because provenance has to be able to
//!   show what the source actually said.
//! * **No canonical form is not an error.** An unparseable phone number yields
//!   `normalized: None`, following the convention
//!   [`crate::er::similarity::Normalizer::phone_normalize`] already sets.
//!
//! String canonicalization itself is not reinvented here: casing, whitespace
//! and NFC are [`crate::er::similarity::StringNormalizer`]'s job, and this
//! layer only decides *which* rules run.

use crate::er::value::Value;
use crate::er::ErError;

use super::rules::{NormalizationRule, NormalizationRules};

/// A value before and after canonicalization.
#[derive(Debug, Clone, PartialEq)]
pub struct NormalizationResult {
    /// The value as it arrived, untouched.
    pub raw: Value,
    /// The canonical form. `None` when no rule could parse the value, which is
    /// a normal outcome and not a failure.
    pub normalized: Option<Value>,
    /// Rules that ran, in order.
    pub applied: Vec<NormalizationRule>,
}

impl NormalizationResult {
    /// A result whose value passed through unchanged.
    pub fn unchanged(raw: Value) -> Self {
        Self {
            normalized: Some(raw.clone()),
            raw,
            applied: Vec::new(),
        }
    }

    /// A result for a value no rule could canonicalize.
    pub fn unparsed(raw: Value) -> Self {
        Self {
            normalized: None,
            raw,
            applied: Vec::new(),
        }
    }

    /// The canonical text, when there is one.
    pub fn normalized_text(&self) -> Option<String> {
        self.normalized.as_ref().and_then(Value::as_text)
    }

    /// The value to compare: canonical when available, raw otherwise.
    pub fn comparable(&self) -> &Value {
        self.normalized.as_ref().unwrap_or(&self.raw)
    }
}

/// Turns a value into its canonical form under a rule set.
///
/// One implementation per normalization *family* (names, addresses, phones),
/// all reachable through the same config, rather than one trait per technique.
pub trait Normalizer {
    /// Identifies the family, e.g. `"name"`. Recorded in provenance so a
    /// canonical value can be traced to the transformation that made it.
    fn name(&self) -> &str;

    /// Canonicalizes `value` under `rules`.
    fn normalize(
        &self,
        value: &Value,
        rules: &NormalizationRules,
    ) -> Result<NormalizationResult, ErError>;
}

/// Applies a rule list step by step, delegating string canonicalization to
/// [`StringNormalizer`].
///
/// The generic fallback: anything more specific than string canonicalization
/// belongs in a family normalizer.
pub struct RuleNormalizer;

impl Normalizer for RuleNormalizer {
    fn name(&self) -> &str {
        "rules"
    }

    fn normalize(
        &self,
        _value: &Value,
        _rules: &NormalizationRules,
    ) -> Result<NormalizationResult, ErError> {
        todo!()
    }
}

/// Normalizes free text: the case and whitespace rules, nothing else.
pub struct TextNormalizer;

impl Normalizer for TextNormalizer {
    fn name(&self) -> &str {
        "text"
    }

    fn normalize(
        &self,
        __value: &Value,
        __rules: &NormalizationRules,
    ) -> Result<NormalizationResult, ErError> {
        todo!()
    }
}

/// Normalizes person and organization names: text rules plus abbreviation and
/// honorific expansion.
pub struct NameNormalizer;

impl Normalizer for NameNormalizer {
    fn name(&self) -> &str {
        "name"
    }

    fn normalize(
        &self,
        __value: &Value,
        __rules: &NormalizationRules,
    ) -> Result<NormalizationResult, ErError> {
        todo!()
    }
}

/// Normalizes postal addresses down to their comparable components.
pub struct AddressNormalizer;

impl Normalizer for AddressNormalizer {
    fn name(&self) -> &str {
        "address"
    }

    fn normalize(
        &self,
        __value: &Value,
        __rules: &NormalizationRules,
    ) -> Result<NormalizationResult, ErError> {
        todo!()
    }
}

/// Normalizes phone numbers to significant digits, reusing
/// [`StringNormalizer::phone_normalize`] for the parsing itself.
pub struct PhoneNormalizer {
    region: Option<String>,
}

impl PhoneNormalizer {
    /// Numbers are parsed with an explicit default region where one is known.
    pub fn new(region: Option<String>) -> Self {
        Self { region }
    }

    /// The region numbers are parsed against when the value carries none.
    pub fn region(&self) -> Option<&str> {
        self.region.as_deref()
    }
}

impl Normalizer for PhoneNormalizer {
    fn name(&self) -> &str {
        "phone"
    }

    fn normalize(
        &self,
        __value: &Value,
        __rules: &NormalizationRules,
    ) -> Result<NormalizationResult, ErError> {
        todo!()
    }
}