//! The single value type the ER stages exchange.
//!
//! Ingestion emits Arrow-backed batches and never needs this, but every stage
//! after schema inference does: normalization rewrites values, matching
//! reports them as evidence, entities hold them as attributes. One enum with
//! one meaning ("a value as it arrived, untyped beyond what the source said")
//! beats three near-identical copies.
//!
//! Arrow and Python types stay on their own side of the boundary.

use std::collections::BTreeMap;

/// A value as the source presented it.
#[derive(Debug, Clone, PartialEq)]
pub enum Value {
    Null,
    Bool(bool),
    Int(i64),
    Float(f64),
    Text(String),
    /// Dates and timestamps stay textual here; `NormalizationRule::DateCanonical`
    /// is what turns them into something comparable.
    List(Vec<Value>),
    Map(BTreeMap<String, Value>),
}

impl Value {
    /// The value as text, for rules and comparators that work on strings.
    /// Non-text scalars render; `Null` and containers do not.
    pub fn as_text(&self) -> Option<String> {
        match self {
            Value::Text(s) => Some(s.clone()),
            Value::Int(i) => Some(i.to_string()),
            Value::Float(f) => Some(f.to_string()),
            Value::Bool(b) => Some(b.to_string()),
            _ => None,
        }
    }

    /// The value as a number, when it is one or parses as one.
    pub fn as_f64(&self) -> Option<f64> {
        match self {
            Value::Int(i) => Some(*i as f64),
            Value::Float(f) => Some(*f),
            Value::Text(s) => s.trim().parse().ok(),
            _ => None,
        }
    }

    /// Whether the value carries no information.
    pub fn is_null(&self) -> bool {
        matches!(self, Value::Null)
    }
}

impl From<&str> for Value {
    fn from(value: &str) -> Self {
        Value::Text(value.to_string())
    }
}

impl From<String> for Value {
    fn from(value: String) -> Self {
        Value::Text(value)
    }
}