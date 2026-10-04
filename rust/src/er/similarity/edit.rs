use textdistance;
use std::error::Error;

use crate::er::similarity::{normalize, score::SimilarityScore};


struct LevenshteinSimilarity {
    similarity: SimilarityScore,
}

struct DamerauLevenshteinSimilarity {
    similarity: SimilarityScore,
}

/// `textdistance`'s normalized edit distance runs from 0.0 (identical) to 1.0
/// (nothing in common); a similarity runs the other way.
fn to_similarity(normalized_distance: f64) -> f64 {
    1.0 - normalized_distance.clamp(0.0, 1.0)
}

impl LevenshteinSimilarity {
    pub fn levenshtein_similarity(a: String, b: String) -> Result<Self, Box<dyn Error>> {
                
        let matched_score = to_similarity(textdistance::nstr::levenshtein(&a, &b));
        
        let result = SimilarityScore{
            score: matched_score,
            method: "levenshtein_similarity".to_string()
        };
        
        Ok(Self { similarity: result })
    }
}

impl DamerauLevenshteinSimilarity {
    pub fn damerau_levenshtein_similarity(a: String, b: String) -> Result<Self, Box<dyn Error>> {
        
        let matched_score = to_similarity(textdistance::nstr::damerau_levenshtein(&a, &b));
        
        let result = SimilarityScore{
            score: matched_score,
            method: "damerau_levenshtein_similarity".to_string()
        };
        
        Ok(Self { similarity: result })
    }
}

pub fn levenshtein_similarity(a: String, b: String) -> f64 {
    let normalized_a = normalize::normalize(&a);
    let normalized_b = normalize::normalize(&b);

    let n = LevenshteinSimilarity::levenshtein_similarity(normalized_a, normalized_b).unwrap();
    n.similarity.score
}

pub fn damerau_levenshtein_similarity(a: String, b: String) -> f64 {
    let normalized_a = normalize::normalize(&a);
    let normalized_b = normalize::normalize(&b);

    let n = DamerauLevenshteinSimilarity::damerau_levenshtein_similarity(normalized_a, normalized_b).unwrap();
    n.similarity.score
}