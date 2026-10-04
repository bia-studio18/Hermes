use std::error::Error;

use crate::er::similarity::score::SimilarityScore;

pub enum EmailAlgo {
    Exact,
    Username,
    Domain,
    Combined,
}

pub struct EmailSimilarity {
    pub similarity: SimilarityScore,
}

pub fn email_similarity(a: String, b:String, algo: EmailAlgo) -> Result<EmailSimilarity, Box<dyn Error>> {
    let (user_a, domain_a) = a.split_once('@').ok_or("left value is not an email address")?;
    let (user_b, domain_b) = b.split_once('@').ok_or("right value is not an email address")?;

    let score = match algo {
        EmailAlgo::Combined => {
            let user_score = if user_a == user_b {1.0} else {0.0};
            let domain_score = if domain_a == domain_b {1.0} else {0.0};
            (user_score + domain_score) / 2.0
        },
        EmailAlgo::Domain => {
            if domain_a == domain_b {
                1.0
            } else {
                0.0
            }
        },
        EmailAlgo::Username => {
            if user_a == user_b {
                1.0
            } else { 
                0.0 
            }
        }
        EmailAlgo::Exact => {
            if a == b {
                1.0
            } else {
                0.0
            }
        }
    };

    let result = SimilarityScore{
        score: score,
        method: "email_similarity".to_string()
    };
    Ok(EmailSimilarity { similarity: result })
}