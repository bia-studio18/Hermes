use std::error::Error;

use crate::er::similarity::score::SimilarityScore;

pub enum NumericAlgo {
    AbsoluteDifference,
    RelativeDifference,
    NormalizedDifference{
        min: f64,
        max: f64
    }
}

pub struct NumericSimilarity {
    similarity: SimilarityScore
}


pub fn numeric_similarity(a: f64, b: f64, algo: NumericAlgo) -> Result<NumericSimilarity, Box<dyn Error>> {

    let score: f64 = match algo {
        NumericAlgo::AbsoluteDifference => {
            (a - b).abs()            
        },
        NumericAlgo::RelativeDifference => {
            let nominator = (a-b).abs();
            let denominator = a.abs().max(b.abs());
            
            if denominator == 0.0 {
                0.0;
            }
            let _score = 1.0 - (nominator / denominator);
            _score

        },
        NumericAlgo::NormalizedDifference {min, max} => {
            // |a - b| / (max - min)
            let nominator = (a - b).abs();
            let denominator = max - min;
            if denominator == 0.0 {
                0.0;
            }
            nominator / denominator
            
        }
    };
    
    let result = SimilarityScore { 
        score: score, 
        method: "numeric_similarity".to_string() 
    };
    
    Ok(NumericSimilarity { similarity: result })
}