use unicode_normalization::UnicodeNormalization;
use phonelib;

pub trait Normalizer {
    fn normalize(&self, value: &str) -> String;
    fn phone_normalize(&self, value: &str) -> String;
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
    fn phone_normalize(&self, value: &str) -> String {
        let normalized = phonelib::normalize_phone_number(value).unwrap();
        normalized
    }

}

pub fn normalize(value: &str) -> String {
    StringNormalizer.normalize(value)
}

// pub fn phone_normalize(value: &str) -> 