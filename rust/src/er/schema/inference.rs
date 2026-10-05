//! Working out what a source's columns are and what they mean.
//!
//! Two steps that stay separate, because they fail differently and are useful
//! separately:
//!
//! * [`infer_schema`] / [`infer_field_type`] look only at values.
//! * [`infer_field_semantics`] looks at values *and* names, and is allowed to
//!   be wrong — hence the confidence and the retained alternatives.
//!
//! Both are sampling operations: a bounded number of rows decides the whole
//! schema, so inference cost does not grow with the source.

use crate::data::HermesDataset;
use crate::er::config::SchemaConfig;
use crate::er::ErError;

use super::field::FieldHint;
use super::schema::{EntityType, Schema, SchemaMapping};
use super::types::{FieldSemantic, FieldType};

/// Infers a schema from a dataset's columns and a bounded sample of rows.
///
/// Trusting the declared Arrow types first is deliberate: when a source declares
/// its types, sampling only has to resolve what the declaration left open.
pub fn infer_schema(_dataset: &HermesDataset, _config: &SchemaConfig) -> Result<Schema, ErError> {
    todo!()
}

/// Infers the physical type of one column from its values.
pub fn infer_field_type(__values: &[FieldType]) -> Result<FieldType, ErError> {
    todo!()
}

/// Infers what one column is about, given its name, type and value patterns.
///
/// Hints win over inference; a hint whose `confidence` exceeds
/// [`SchemaConfig::hint_override`] replaces the answer outright rather than
/// being averaged with it.
pub fn infer_field_semantics(
    __name: &str,
    __field_type: &FieldType,
    __config: &SchemaConfig,
) -> Result<FieldSemantic, ErError> {
    todo!()
}

/// Like [`infer_field_semantics`], but keeps the runner-up candidates so a
/// later stage can weigh them.
pub fn infer_field_semantic_guess(
    __name: &str,
    __field_type: &FieldType,
    __config: &SchemaConfig,
) -> Result<super::types::FieldSemanticGuess, ErError> {
    todo!()
}

/// Applies caller hints to an inferred schema, overriding semantics in place.
pub fn apply_field_hints(schema: &mut Schema, hints: &[FieldHint]) -> Result<(), ErError> {
    for hint in hints {
        let field = schema
            .fields
            .iter_mut()
            .find(|f| f.name == hint.field)
            .ok_or_else(|| {
                ErError::Configuration(format!("hint names unknown field `{}`", hint.field))
            })?;
        hint.apply(field)?;
    }
    Ok(())
}

/// Names the entity type these columns describe.
pub fn infer_entity_type(__schema: &Schema) -> Result<Option<EntityType>, ErError> {
    todo!()
}

/// Matches two inferred schemas column by column.
pub fn map_schemas(
    __left: &Schema,
    __right: &Schema,
) -> Result<SchemaMapping, ErError> {
    todo!()
}