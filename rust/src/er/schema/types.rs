//! What a column is, and what it means.
//!
//! Two orthogonal axes, deliberately separate:
//!
//! * [`FieldType`] is the physical type observed in the data.
//! * [`FieldSemantic`] is the role the column plays in the world.
//!
//! `date_of_birth` is `String` physically and `DateOfBirth` semantically. Code
//! that needs to know how to compare values reads the type; code that needs to
//! know what an entity is reads the semantic. Neither implies the other.

use std::collections::BTreeMap;

/// Physical type of a column, as observed rather than declared.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum FieldType {
    Null,
    Boolean,
    Integer,
    Decimal,
    Float,
    Date,
    Time,
    Timestamp,
    Duration,
    /// Anything unparseable stays text; Hermes never guesses past this.
    Text,
    /// Homogeneous nested list.
    List(Box<FieldType>),
    /// Nested key/value structure, kept generic until schema inference
    /// decides the keys are worth promoting to columns.
    Struct(BTreeMap<String, FieldType>),
    /// Two or more concrete types in one column.
    Mixed(Vec<FieldType>),
    /// Too few non-null values to call.
    Unknown,
}

impl FieldType {
    /// Whether the type can be ordered or compared as a number.
    pub fn is_numeric(&self) -> bool {
        matches!(
            self,
            FieldType::Integer | FieldType::Decimal | FieldType::Float
        )
    }

    /// Whether the type has a chronological order.
    pub fn is_temporal(&self) -> bool {
        matches!(
            self,
            FieldType::Date
                | FieldType::Time
                | FieldType::Timestamp
                | FieldType::Duration
        )
    }
}

/// What a column is about, independent of how it is stored.
///
/// Open-ended on purpose: `Person`, `Organization`, `Product` and `Device` are
/// peers here, and a domain that needs a concept this enum lacks adds it once
/// rather than special-casing the pipeline.
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum FieldSemantic {
    // Identity
    Identifier,
    /// Unique key within one source.
    SourceIdentifier,
    // People
    PersonName,
    GivenName,
    FamilyName,
    DateOfBirth,
    // Organizations
    OrganizationName,
    OrganizationIdentifier,
    // Contact
    Email,
    Phone,
    PostalAddress,
    Location,
    // Web
    Url,
    Domain,
    // Generic
    Date,
    Amount,
    Quantity,
    Category,
    FreeText,
    /// Nothing recognised yet.
    Unknown,
}

impl FieldSemantic {
    /// Whether two columns sharing this semantic are likely to describe the
    /// same real-world value, and so worth blocking on.
    pub fn is_joinable(&self) -> bool {
        matches!(
            self,
            FieldSemantic::Identifier
                | FieldSemantic::SourceIdentifier
                | FieldSemantic::Email
                | FieldSemantic::Phone
                | FieldSemantic::Domain
        )
    }

    /// Whether the semantic identifies an entity on its own.
    pub fn is_strong_identifier(&self) -> bool {
        matches!(
            self,
            FieldSemantic::Identifier
                | FieldSemantic::SourceIdentifier
                | FieldSemantic::OrganizationIdentifier
        )
    }
}

/// An inferred semantic plus the alternatives still in play.
///
/// Keeping the runner-up is what lets a later stage ask "are you sure?" without
/// re-running inference.
#[derive(Debug, Clone, PartialEq)]
pub struct FieldSemanticGuess {
    pub chosen: FieldSemantic,
    pub alternatives: Vec<FieldSemantic>,
    /// 0.0..=1.0. Below the configured floor the field stays `Unknown`.
    pub confidence: f64,
}