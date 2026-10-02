use unicode_normalization::UnicodeNormalization;

pub trait Normalizer {
    fn normalize(&self, value: &str) -> String;
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
}

pub fn normalize(value: &str) -> String {
    StringNormalizer.normalize(value)
}