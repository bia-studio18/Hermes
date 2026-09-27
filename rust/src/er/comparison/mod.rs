mod exact;
mod jaro_winkler;
mod levenshtein;
mod normalized;
mod token_similarity;

use crate::er::types::{ComparisonMethod, ComparisonResult};

pub use exact::compare as compare_exact;
pub use jaro_winkler::compare as compare_jaro_winkler;
pub use levenshtein::compare as compare_levenshtein;
pub use normalized::compare as compare_normalized_exact;
pub use token_similarity::compare as compare_token_similarity;

pub fn compare(method: ComparisonMethod, left: &str, right: &str) -> ComparisonResult {
    match method {
        ComparisonMethod::Exact => exact::compare(left, right),
        ComparisonMethod::NormalizedExact => normalized::compare(left, right),
        ComparisonMethod::Levenshtein => levenshtein::compare(left, right),
        ComparisonMethod::JaroWinkler => jaro_winkler::compare(left, right),
        ComparisonMethod::TokenSimilarity => token_similarity::compare(left, right),
    }
}
