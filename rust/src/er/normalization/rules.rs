//! The normalization steps available, independent of which fields get them.
//!
//! A rule is data, not code: the set a source or field uses is configuration.
//! That keeps "lowercase and collapse whitespace" from being a hard-coded step
//! inside the normalizer, and lets two sources be normalized differently.

/// One canonicalization step.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum NormalizationRule {
    /// Unicode NFC, then casefold.
    UnicodeCasefold,
    /// Collapse runs of whitespace and trim.
    Whitespace,
    /// Drop punctuation.
    Punctuation,
    /// Strip diacritics, keeping base letters.
    Diacritics,
    /// Transliterate to ASCII where the script allows it.
    Transliterate,
    /// Expand abbreviations and honorifics found in names.
    NameAbbreviations,
    /// Reduce a postal address to its comparable components.
    AddressComponents,
    /// Keep significant digits only, with a country hint.
    PhoneDigits { default_region: Option<String> },
    /// Lowercase the domain part and split user from domain.
    EmailParts,
    /// Reduce a date to `YYYY-MM-DD`, or to year/month when that is all there is.
    DateCanonical,
    /// Parse a number and re-render it identically.
    NumberCanonical,
    /// A transformation registered elsewhere by name.
    Named(String),
}

impl NormalizationRule {
    /// Whether applying this rule can drop information that provenance must
    /// still be able to show. Rules marked lossy keep the raw value alongside.
    pub fn is_lossy(&self) -> bool {
        matches!(
            self,
            NormalizationRule::Punctuation
                | NormalizationRule::Diacritics
                | NormalizationRule::Transliterate
                | NormalizationRule::NameAbbreviations
                | NormalizationRule::AddressComponents
                | NormalizationRule::PhoneDigits { .. }
        )
    }
}

/// The ordered rules one field is normalized with.
#[derive(Debug, Clone, Default)]
pub struct NormalizationRules {
    pub rules: Vec<NormalizationRule>,
}

impl NormalizationRules {
    /// The rule list as-is.
    pub fn new(rules: Vec<NormalizationRule>) -> Self {
        Self { rules }
    }

    /// No rules: values pass through untouched.
    pub fn identity() -> Self {
        Self::default()
    }

    /// Whether any rule in the list is lossy.
    pub fn is_lossy(&self) -> bool {
        self.rules.iter().any(NormalizationRule::is_lossy)
    }
}