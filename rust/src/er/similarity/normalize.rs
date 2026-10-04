use unicode_normalization::UnicodeNormalization;
use phonelib;

pub trait Normalizer {
    fn normalize(&self, value: &str) -> String;
    /// `None` when the value is not a parseable phone number.
    fn phone_normalize(&self, value: &str) -> Option<String>;
}

pub struct StringNormalizer;

impl Normalizer for StringNormalizer {
    fn normalize(&self, value: &str) -> String {
        value
            .nfc()
            .collect::<String>()
            .trim()
            .to_lowercase()
    }
    fn phone_normalize(&self, value: &str) -> Option<String> {
        phonelib::normalize_phone_number(value)
    }

}

pub fn normalize(value: &str) -> String {
    StringNormalizer.normalize(value)
}

// pub fn phone_normalize(value: &str) -> 