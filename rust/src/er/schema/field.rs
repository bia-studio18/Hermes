//! One column of an inferred [`super::Schema`].

use crate::er::ErError;

use super::types::{FieldSemantic, FieldSemanticGuess, FieldType};

/// A column: its name, observed type, inferred meaning and shape.
#[derive(Debug, Clone)]
pub struct Field {
    /// Name as it appears in the source. Not unique across sources; use
    /// [`Field::key`] when merging schemas.
    pub name: String,
    pub field_type: FieldType,
    pub semantic: FieldSemanticGuess,
    pub nullable: bool,
    /// Rows sampled when this field was inferred.
    pub sampled: usize,
}

impl Field {
    /// A field with no inference yet.
    pub fn new(name: impl Into<String>, field_type: FieldType) -> Self {
        Self {
            name: name.into(),
            field_type,
            semantic: FieldSemanticGuess {
                chosen: FieldSemantic::Unknown,
                alternatives: Vec::new(),
                confidence: 0.0,
            },
            nullable: true,
            sampled: 0,
        }
    }

    /// Stable key for this field within a schema.
    pub fn key(&self) -> &str {
        &self.name
    }

    /// The inferred meaning, or `Unknown` when inference did not commit.
    pub fn meaning(&self) -> &FieldSemantic {
        &self.semantic.chosen
    }

    /// Whether this field can carry an entity identifier.
    pub fn is_identifier(&self) -> bool {
        self.semantic.chosen.is_strong_identifier()
    }
}

/// A field named by the caller rather than inferred, e.g. "treat `cust_no` as
/// the organization identifier". User intent overrides inference, so it is a
/// separate type from [`Field`] instead of a flag on it.
#[derive(Debug, Clone)]
pub struct FieldHint {
    pub field: String,
    pub semantic: FieldSemantic,
    /// 0.0..=1.0 trust in the hint. `1.0` means the hint wins outright.
    pub confidence: f64,
}

impl FieldHint {
    /// A hint to be taken at face value.
    pub fn strong(field: impl Into<String>, semantic: FieldSemantic) -> Self {
        Self {
            field: field.into(),
            semantic,
            confidence: 1.0,
        }
    }

    /// Rejects any inferred meaning below this confidence.
    pub fn requires(mut self, confidence: f64) -> Self {
        self.confidence = confidence;
        self
    }

    /// Applies the hint to a field, overwriting the inferred meaning.
    pub fn apply(&self, field: &mut Field) -> Result<(), ErError> {
        field.semantic = FieldSemanticGuess {
            chosen: self.semantic.clone(),
            alternatives: Vec::new(),
            confidence: self.confidence,
        };
        Ok(())
    }
}