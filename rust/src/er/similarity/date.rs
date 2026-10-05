use chrono::{NaiveDate, Datelike};

use crate::er::similarity::score::SimilarityScore;

#[derive(Debug, Clone)]
pub enum DateAlgo {
    Exact,
    DayDifference {
        max_days: u32
    },
    YearMonth
}

pub struct DateSimilarity {
    pub similarity: SimilarityScore,
}

pub fn date_similarity(a: &NaiveDate, b: &NaiveDate, algo: DateAlgo) -> DateSimilarity {
    let score = match algo {
        DateAlgo::Exact => {
            if a == b{
                1.0
            } else { 0.0 }
        },
        // Decays from 1.0 on the same day to 0.0 once the gap reaches
        // `max_days`; a zero tolerance means "same day or nothing".
        DateAlgo::DayDifference { max_days } => {
            let distance = (*b - *a).num_days().unsigned_abs() as f64;
            if max_days == 0 {
                if distance == 0.0 { 1.0 } else { 0.0 }
            } else {
                1.0 - (distance / f64::from(max_days)).min(1.0)
            }
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