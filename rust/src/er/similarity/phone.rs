use phonelib;

use crate::er::similarity::score::SimilarityScore;

/*
| Item                 | Type     | Purpose                   |
| -------------------- | -------- | ------------------------- |
| `PhoneAlgo`          | enum     | Select comparison method  |
| `PhoneSimilarity`    | struct   | Holds `SimilarityScore`   |
| `phone_similarity()` | function | Compare two phone numbers |
 */

pub enum PhoneAlgo {
    Exact,
    Suffix {
        digits: usize,
    },
    Edit,
}

pub struct PhoneSimilarity {
    similarity: SimilarityScore
}

pub fn phone_similarity(a: String, b: String, algo: PhoneAlgo) -> PhoneSimilarity {
    
    let score = match algo {
        PhoneAlgo::Edit => {
            0.0
        },
        PhoneAlgo::Exact => {
            0.0
        },
        PhoneAlgo::Suffix { digits } => {
            0.0
        }
    };
    let result = SimilarityScore { 
        score: score, 
        method: "phone_similarity".to_string() 
    };
    PhoneSimilarity { similarity: result }
}