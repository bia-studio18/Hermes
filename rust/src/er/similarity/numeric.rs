use std::error::Error;

use crate::er::similarity::score::SimilarityScore;

#[derive(Debug, Clone)]
pub enum NumericAlgo {
    /// Same value scores 1.0; anything a full unit or more apart scores 0.0.
    AbsoluteDifference,
    RelativeDifference,
    NormalizedDifference{
        min: f64,
        max: f64
    }
}

pub struct NumericSimilarity {
    pub similarity: SimilarityScore,
}


pub fn numeric_similarity(a: f64, b: f64, algo: NumericAlgo) -> Result<NumericSimilarity, Box<dyn Error>> {

    let score: f64 = match algo {
        NumericAlgo::AbsoluteDifference => {
            1.0 - (a - b).abs().min(1.0)
        },
        NumericAlgo::RelativeDifference => {
            let nominator = (a-b).abs();
            let denominator = a.abs().max(b.abs());
            // Zero against zero is a perfect match, not a zero score.
            if denominator == 0.0 {
                1.0
            } else {
                1.0 - (nominator / denominator).min(1.0)
            }
        },
        NumericAlgo::NormalizedDifference {min, max} => {
            let nominator = (a - b).abs();
            let denominator = max - min;
            if denominator <= 0.0 {
                if a == b { 1.0 } else { 0.0 }
            } else {
                1.0 - (nominator / denominator).min(1.0)
            }
        }
    };
    
    let result = SimilarityScore { 
        score: score, 
        method: "numeric_similarity".to_string() 
    };
    
    Ok(NumericSimilarity { similarity: result })
}