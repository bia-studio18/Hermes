use crate::er::similarity::score::SimilarityScore;

/*
| Item                 | Type     | Purpose                   |
| -------------------- | -------- | ------------------------- |
| `PhoneAlgo`          | enum     | Select comparison method  |
| `PhoneSimilarity`    | struct   | Holds `SimilarityScore`   |
| `phone_similarity()` | function | Compare two phone numbers |
 */

#[derive(Debug, Clone)]
pub enum PhoneAlgo {
    Exact,
    Suffix {
        digits: usize,
    },
    Edit,
}

pub struct PhoneSimilarity {
    pub similarity: SimilarityScore,
}

pub fn phone_similarity(_a: String, _b: String, algo: PhoneAlgo) -> PhoneSimilarity {
    
    let score = match algo {
        PhoneAlgo::Edit => {
            0.0
        },
        PhoneAlgo::Exact => {
            0.0
        },
        PhoneAlgo::Suffix { digits: _ } => {
            0.0
        }
    };
    let result = SimilarityScore { 
        score: score, 
        method: "phone_similarity".to_string() 
    };
    PhoneSimilarity { similarity: result }
}