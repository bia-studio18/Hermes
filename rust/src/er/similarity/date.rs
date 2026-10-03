use chrono::{NaiveDate, Datelike};

use crate::er::similarity::score::SimilarityScore;

pub enum DateAlgo {
    Exact,
    DayDifference {
        max_days: u32
    },
    YearMonth
}

pub struct DateSimilarity {
    similarity: SimilarityScore
}

pub fn date_similarity(a: &NaiveDate, b: &NaiveDate, algo: DateAlgo) -> DateSimilarity {
    let score = match algo {
        DateAlgo::Exact => {
            if a == b{
                1.0
            } else { 0.0 }
        },
        DateAlgo::DayDifference { max_days }=> {
            let distance = (*b - *a).num_days() as f64;
            let _res = distance / max_days as f64;
            _res.clamp(0.0, 1.0)

        },
        DateAlgo::YearMonth => {
            if a.year() == b.year() && a.month() == b.month() {
                1.0
            } else {
                0.0
            }        
        }
    };
    let result = SimilarityScore {
        score: score,
        method: "date_similarity".to_string()
    };
    DateSimilarity { similarity: result }
}