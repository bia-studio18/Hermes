use textdistance::nstr::{
  cosine, jaccard, sorensen_dice, overlap, tversky, bag, roberts  
};

use crate::er::similarity::score::SimilarityScore;
#[derive(Debug, Clone, Copy)]
pub enum TokenAlgo {
    Jaccard,
    Cosine,
    SorensenDice,
    Overlap,
    Tversky,
    Bag,
    Roberts,
}

pub struct TokenSimilarity {
    similarity: SimilarityScore
}

impl TokenSimilarity {
    pub fn token_similarity(
        s1: &str,
        s2: &str,
        algo: TokenAlgo,
    ) -> Self 
    
    {
        let _score = match algo {
            TokenAlgo::Jaccard => jaccard(s1, s2),
            TokenAlgo::Cosine => cosine(s1, s2),
            TokenAlgo::SorensenDice => sorensen_dice(s1, s2),
            TokenAlgo::Overlap => overlap(s1, s2),
            TokenAlgo::Tversky => tversky(s1, s2),
            TokenAlgo::Bag => bag(s1, s2),
            TokenAlgo::Roberts => roberts(s1, s2),
        };
        let result = SimilarityScore { 
            score: _score, 
            method: "token_based".to_string()
        };
        Self { similarity: result }
    }
}

pub fn token_similarity(a: String, b: String, algo: TokenAlgo) -> f64 {
    let n = TokenSimilarity::token_similarity(&a, &b, algo);
    n.similarity.score
}