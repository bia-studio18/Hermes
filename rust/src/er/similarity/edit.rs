use textdistance;
use std::error::Error;

use crate::er::similarity::{normalize, score::SimilarityScore};


struct LevenshteinSimilarity {
    similarity: SimilarityScore,
}

struct DamerauLevenshteinSimilarity {
    similarity: SimilarityScore,
}

impl LevenshteinSimilarity {
    pub fn levenshtein_similarity(a: String, b: String) -> Result<Self, Box<dyn Error>> {
                
        let matched_score = textdistance::nstr::levenshtein(&a, &b);
        
        let result = SimilarityScore{
            score: matched_score,
            method: "levenshtein_similarity".to_string()
        };
        
        Ok(Self { similarity: result })
    }
}

impl DamerauLevenshteinSimilarity {
    pub fn damerau_levenshtein_similarity(a: String, b: String) -> Result<Self, Box<dyn Error>> {
        
        let matched_score = textdistance::nstr::damerau_levenshtein(&a, &b);
        
        let result = SimilarityScore{
            score: matched_score as f64,
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