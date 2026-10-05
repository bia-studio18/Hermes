//! What an entity is known by, field by field.
//!
//! Two things make an attribute different from a plain value:
//!
//! * It keeps the canonical value *and* the raw one, so a merge can be undone
//!   or explained later.
//! * It keeps multiple values per field over time ([`AttributeSet`]), because
//!   an entity's address changes and an old record still has to resolve
//!   against it.

use crate::er::normalization::NormalizationResult;
use crate::er::value::Value;

/// When an attribute value was true, for sources that say.
#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct Validity {
    pub from: Option<String>,
    pub to: Option<String>,
}

impl Validity {
    /// No known period.
    pub fn unknown() -> Self {
        Self::default()
    }

    /// Whether the value was current at `date` (`YYYY-MM-DD`).
    pub fn covers(&self, date: &str) -> bool {
        let after_start = self.from.as_deref().is_none_or(|f| f <= date);
        let before_end = self.to.as_deref().is_none_or(|t| date < t);
        after_start && before_end
    }
}

/// One value of one field, with its provenance and its history.
#[derive(Debug, Clone, PartialEq)]
pub struct Attribute {
    pub field: String,
    /// What normalization produced.
    pub normalized: NormalizationResult,
    pub validity: Validity,
    /// 0.0..=1.0: how much this value is trusted, from source reliability and
    /// past conflicts.
    pub confidence: f64,
    /// Where the value came from. Filled in by the entity layer.
    pub provenance: Option<crate::er::provenance::Provenance>,
}

impl Attribute {
    /// An attribute holding `value`, unnormalized.
    pub fn new(field: impl Into<String>, value: Value) -> Self {
        Self {
            field: field.into(),
            normalized: NormalizationResult::unchanged(value),
            validity: Validity::unknown(),
            confidence: 1.0,
            provenance: None,
        }
    }

    /// The canonical value, when normalization produced one.
    pub fn value(&self) -> &Value {
        self.normalized.comparable()
    }

    /// The value as the source stated it.
    pub fn raw(&self) -> &Value {
        &self.normalized.raw
    }
}

/// Every attribute of one entity, keyed by field.
#[derive(Debug, Clone, Default)]
pub struct AttributeSet {
    attributes: Vec<Attribute>,
}

impl AttributeSet {
    /// An empty set.
    pub fn empty() -> Self {
        Self::default()
    }

    /// Adds an attribute.
    pub fn push(&mut self, attribute: Attribute) {
        self.attributes.push(attribute);
    }

    /// Every value recorded for `field`, newest period last.
    pub fn get(&self, field: &str) -> impl Iterator<Item = &Attribute> {
        self.attributes.iter().filter(move |a| a.field == field)
    }

    /// The value of `field` current at `date`, if any.
    pub fn current(&self, field: &str, date: &str) -> Option<&Attribute> {
        self.get(field).find(|a| a.validity.covers(date))
    }

    /// Field names present.
    pub fn fields(&self) -> Vec<&str> {
        let mut names: Vec<&str> = self.attributes.iter().map(|a| a.field.as_str()).collect();
        names.sort_unstable();
        names.dedup();
        names
    }

    /// Every attribute.
    pub fn iter(&self) -> impl Iterator<Item = &Attribute> {
        self.attributes.iter()
    }

    /// Number of attributes.
    pub fn len(&self) -> usize {
        self.attributes.len()
    }

    /// Whether nothing is known yet.
    pub fn is_empty(&self) -> bool {
        self.attributes.is_empty()
    }
}