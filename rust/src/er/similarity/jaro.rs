use textdistance;
use std::error::Error;

use crate::er::similarity::{normalize, score::SimilarityScore};

pub struct JaroSimilarity {
    similarity: SimilarityScore
}

pub struct JaroWinklerSimilarity {
    similarity: SimilarityScore
}

impl JaroSimilarity {
    pub fn jaro_similarity(a: String, b: String) -> Result<Self, Box<dyn Error>> {
        let normalized_a = normalize::normalize(&a);
        let normalized_b = normalize::normalize(&b);

        let matched_score = textdistance::nstr::jaro(&normalized_a, &normalized_b);
        
        let result = SimilarityScore { 
            score: matched_score,
            method: "jaro_similarity".to_string()
        };
        Ok(Self { similarity: result })
    }

}


impl JaroWinklerSimilarity {
    pub fn jaro_winkler_similarity(a: String, b: String) -> Result<Self, Box<dyn Error>> {
        let normalized_a = normalize::normalize(&a);
        let normalized_b = normalize::normalize(&b);

        let matched_score = textdistance::nstr::jaro_winkler(&normalized_a, &normalized_b);
        
        let result = SimilarityScore { 
            score: matched_score,
            method: "jaro_winkler_similarity".to_string()
        };
        Ok(Self { similarity: result })
    }

}

pub fn jaro_similarity(a: String, b: String) -> f64 {
    let res: JaroSimilarity = JaroSimilarity::jaro_similarity(a, b).unwrap();
    res.similarity.score
}

pub fn jaro_winkler_similarity(a: String, b: String) -> f64 {
    let res: JaroWinklerSimilarity = JaroWinklerSimilarity::jaro_winkler_similarity(a, b).unwrap();
    res.similarity.score
}