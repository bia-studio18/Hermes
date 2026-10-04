//! Value similarity. Every function returns a score in 0.0..=1.0 where 1.0
//! means "same value".

mod date;
mod edit;
mod email;
mod exact;
mod jaro;
mod normalize;
mod numeric;
mod phone;
mod score;
mod string;
mod token;

pub use date::{date_similarity, DateAlgo, DateSimilarity};
pub use edit::{damerau_levenshtein_similarity, levenshtein_similarity};
pub use email::{email_similarity, EmailAlgo, EmailSimilarity};
pub use exact::exact_similarity;
pub use jaro::{jaro_similarity, jaro_winkler_similarity};
pub use normalize::{normalize, Normalizer, StringNormalizer};
pub use numeric::{numeric_similarity, NumericAlgo, NumericSimilarity};
pub use phone::{phone_similarity, PhoneAlgo, PhoneSimilarity};
pub use score::SimilarityScore;
pub use token::{token_similarity, TokenAlgo, TokenSimilarity};