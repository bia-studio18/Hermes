//! Entity resolution: source ingestion plus value similarity.

pub mod ingestion;
pub mod similarity;

mod python;

pub(crate) use python::register;

#[cfg(test)]
mod tests {
    use chrono::NaiveDate;

    use super::similarity::{
        DateAlgo, EmailAlgo, Normalizer, NumericAlgo, StringNormalizer, TokenAlgo,
        date_similarity, email_similarity, exact_similarity, jaro_similarity,
        levenshtein_similarity, numeric_similarity, token_similarity,
    };

    fn date(y: i32, m: u32, d: u32) -> NaiveDate {
        NaiveDate::from_ymd_opt(y, m, d).unwrap()
    }

    #[test]
    fn scores_stay_between_zero_and_one() {
        assert_eq!(exact_similarity("Ada".into(), "  ADA ".into()), 1.0);
        assert_eq!(exact_similarity("Ada".into(), "Bob".into()), 0.0);
        assert_eq!(jaro_similarity("hermes".into(), "hermes".into()), 1.0);
        assert_eq!(levenshtein_similarity("kitten".into(), "kitten".into()), 1.0);
        assert_eq!(
            token_similarity("a b".into(), "a b".into(), TokenAlgo::Jaccard),
            1.0
        );

        let normalized = |min: f64, max: f64| NumericAlgo::NormalizedDifference { min, max };
        for (a, b) in [(0.0, 0.0), (3.0, 9.0), (0.0, 10.0), (1e9, -1e9)] {
            let score = numeric_similarity(a, b, normalized(0.0, 10.0)).unwrap().similarity.score;
            assert!((0.0..=1.0).contains(&score), "{a} vs {b} scored {score}");
        }
        assert_eq!(
            numeric_similarity(0.0, 0.0, NumericAlgo::RelativeDifference)
                .unwrap()
                .similarity
                .score,
            1.0
        );
    }

    #[test]
    fn day_difference_decays_with_distance() {
        let a = date(2024, 1, 1);
        let near = date(2024, 1, 6);
        let far = date(2024, 1, 11);

        let at = |b: NaiveDate| date_similarity(&a, &b, DateAlgo::DayDifference { max_days: 10 });
        assert_eq!(at(a).similarity.score, 1.0);
        assert_eq!(at(near).similarity.score, 0.5);
        assert_eq!(at(far).similarity.score, 0.0);
        // Zero tolerance: same day or nothing.
        let strict = |b: NaiveDate| date_similarity(&a, &b, DateAlgo::DayDifference { max_days: 0 });
        assert_eq!(strict(a).similarity.score, 1.0);
        assert_eq!(strict(near).similarity.score, 0.0);
    }

    #[test]
    fn malformed_values_are_errors_not_panics() {
        assert!(email_similarity("nope".into(), "a@b.com".into(), EmailAlgo::Exact).is_err());
        assert!(email_similarity("a@b.com".into(), "nope".into(), EmailAlgo::Exact).is_err());
        assert_eq!(
            email_similarity("a@b.com".into(), "a@c.com".into(), EmailAlgo::Combined)
                .unwrap()
                .similarity
                .score,
            0.5
        );
        assert!(StringNormalizer.phone_normalize("not a number").is_none());
    }
}