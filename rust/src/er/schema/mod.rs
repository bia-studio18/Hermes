//! Columns, their types, and what they mean.
//!
//! Inference is the stage where Hermes decides it is looking at, say, a person's
//! date of birth — but it only ever *suggests* it, with a confidence and the
//! runner-up alternatives kept. Nothing downstream is allowed to hard-code
//! "column 3 is the email": they read [`Schema`] and accept that it can be
//! wrong.

mod field;
mod inference;
mod schema;
mod types;

pub use field::{Field, FieldHint};
pub use inference::{
    apply_field_hints, infer_entity_type, infer_field_semantic_guess, infer_field_semantics,
    infer_field_type, infer_schema, map_schemas,
};
pub use schema::{EntityType, FieldAlignment, Schema, SchemaMapping};
pub use types::{FieldSemantic, FieldSemanticGuess, FieldType};