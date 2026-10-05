//! The inferred shape of one source, and how two of them line up.

use std::collections::BTreeMap;

use super::field::Field;
use super::types::FieldSemantic;

/// The entity type a schema describes. Free-form on purpose: `Person`,
/// `Organization`, `Product` and `Device` are all just names here, so nothing
/// in the pipeline needs to know which one it is resolving.
pub type EntityType = String;

/// Every column of one source, in declaration order.
#[derive(Debug, Clone, Default)]
pub struct Schema {
    pub entity_type: Option<EntityType>,
    pub fields: Vec<Field>,
}

impl Schema {
    /// An empty schema, ready to be filled in by inference.
    pub fn empty() -> Self {
        Self::default()
    }

    /// Adds a column, ignoring names already present.
    pub fn push(&mut self, field: Field) {
        if self.get(&field.name).is_none() {
            self.fields.push(field);
        }
    }

    /// The field with this name.
    pub fn get(&self, name: &str) -> Option<&Field> {
        self.fields.iter().find(|f| f.name == name)
    }

    /// Every field inferred to carry `semantic`.
    pub fn fields_with(&self, semantic: &FieldSemantic) -> impl Iterator<Item = &Field> {
        self.fields.iter().filter(move |f| f.meaning() == semantic)
    }

    /// Columns that can serve as an identifier, best candidate first.
    pub fn identifier_fields(&self) -> Vec<&Field> {
        self.fields.iter().filter(|f| f.is_identifier()).collect()
    }

    /// Names of the columns, in order.
    pub fn names(&self) -> Vec<&str> {
        self.fields.iter().map(|f| f.name.as_str()).collect()
    }
}

/// How one column of `other` lines up with one column of `self`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum FieldAlignment {
    /// Same meaning under the same or a different name.
    Same,
    /// Both present, meanings compatible, names unrelated.
    Alias,
    /// No counterpart in the other schema.
    OnlyInSource,
    /// No counterpart in this schema.
    OnlyInOther,
    /// Present in both with conflicting meanings.
    Conflict,
}

/// The correspondence between two schemas, keyed by this schema's fields.
#[derive(Debug, Clone, Default)]
pub struct SchemaMapping {
    pub alignments: BTreeMap<String, FieldAlignment>,
}

impl SchemaMapping {
    /// Whether the two schemas describe the same entity type.
    pub fn is_compatible(&self) -> bool {
        !self
            .alignments
            .values()
            .any(|a| matches!(a, FieldAlignment::Conflict))
    }

    /// Alignment recorded for one of this schema's columns.
    pub fn counterpart(&self, name: &str) -> Option<&FieldAlignment> {
        self.alignments.get(name)
    }
}