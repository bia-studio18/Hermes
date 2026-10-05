//! Entity resolution.
//!
//! The pipeline, stage by stage:
//!
//! ```text
//! External Source -> ingestion -> schema -> normalization
//!   -> candidate -> matching -> resolution -> entity -> provenance -> learning
//! ```
//!
//! Each stage owns one question and hands the next stage a Hermes type:
//!
//! | Stage          | Question                        | Output                    |
//! |----------------|---------------------------------|---------------------------|
//! | `ingestion`    | where does the data come from?  | `RecordBatch`             |
//! | `schema`       | what are these columns?         | `Schema`                  |
//! | `normalization`| what is the canonical value?    | `NormalizationResult`     |
//! | `candidate`    | which pairs are worth comparing?| `CandidateSet`            |
//! | `matching`     | how alike are they?             | `MatchEvidence`           |
//! | `resolution`   | are they the same thing?        | `ResolutionResult`        |
//! | `entity`       | what do we now know?            | `Entity`                  |
//! | `provenance`   | why do we believe that?         | `Provenance`              |
//! | `learning`     | what did we get wrong last time?| `LearningModel`           |
//! |
//! Ingestion is deliberately the narrowest stage: source to batches, nothing
//! inferred. Everything after it is allowed to interpret the data, and each one
//! states what it concluded rather than acting on it implicitly.

pub mod candidate;
pub mod config;
pub mod entity;
pub mod error;
pub mod ingestion;
pub mod learning;
pub mod matching;
pub mod normalization;
pub mod provenance;
pub mod resolution;
pub mod schema;
pub mod similarity;

mod python;
mod value;

pub use config::ErConfig;
pub use entity::{Entity, EntityId};
pub use error::{ErError, ErResult};
pub use ingestion::{ingest, IngestedDataset, Source};
pub use resolution::{resolve, ResolutionReport, ResolutionResult, Resolver};
pub use schema::Schema;
pub use value::Value;

pub(crate) use python::register;

#[cfg(test)]
mod tests {
    use chrono::NaiveDate;

    use super::candidate::Candidate;
    use super::candidate::RecordId;
    use super::config::ErConfig;
    use super::ingestion::{identify_source, Source, SourceId, SourceKind};
    use super::similarity::{
        DateAlgo, EmailAlgo, Normalizer, NumericAlgo, StringNormalizer, TokenAlgo,
        date_similarity, email_similarity, exact_similarity, jaro_similarity,
        levenshtein_similarity, numeric_similarity, token_similarity,
    };

    fn date(y: i32, m: u32, d: u32) -> NaiveDate {
        NaiveDate::from_ymd_opt(y, m, d).unwrap()
    }

    fn record(source: u64, batch: usize, row: usize) -> RecordId {
        RecordId {
            source: SourceId(source),
            batch,
            row,
        }
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

        let normalized = |min, max| NumericAlgo::NormalizedDifference { min, max };
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

    #[test]
    fn source_detection_reads_extension_then_scheme() {
        assert_eq!(identify_source("/tmp/people.csv"), SourceKind::Csv);
        assert_eq!(identify_source("/tmp/events.JSONL"), SourceKind::Json);
        assert_eq!(identify_source("s3://bucket/x.parquet"), SourceKind::Parquet);
        assert_eq!(identify_source("https://api.example/people"), SourceKind::Api);
        assert_eq!(identify_source("postgres://localhost/hermes"), SourceKind::Database);
        assert_eq!(identify_source("kafka://broker/topic"), SourceKind::Streaming);
        assert_eq!(identify_source("mystery"), SourceKind::Unknown);
    }

    #[test]
    fn an_unknown_source_cannot_be_opened() {
        let source = Source::File(crate::er::ingestion::FileSource {
            path: "/tmp/mystery".into(),
            format: None,
        });
        assert!(matches!(
            source.open(),
            Err(super::ErError::Configuration(_))
        ));
    }

    #[test]
    fn candidate_pairs_are_ordered_and_merged() {
        let mut set = super::candidate::CandidateSet::empty();
        set.insert(Candidate::new(record(0, 0, 5), record(0, 1, 2), "exact"));
        set.insert(Candidate::new(record(0, 1, 2), record(0, 0, 5), "phonetic"));

        assert_eq!(set.len(), 1, "reversed pair must not become a second candidate");
        let candidate = &set.candidates[0];
        assert_eq!((candidate.left, candidate.right), (record(0, 0, 5), record(0, 1, 2)));
        assert!(candidate.found_by("exact") && candidate.found_by("phonetic"));
    }

    #[test]
    fn default_config_is_valid_and_rejects_inverted_thresholds() {
        let config = ErConfig::default();
        assert!(config.validate().is_ok());

        let mut bad = ErConfig::default();
        bad.resolution.thresholds.review = 0.99;
        bad.resolution.thresholds.link = 0.10;
        assert!(matches!(
            bad.validate(),
            Err(super::ErError::Configuration(_))
        ));
    }

    #[test]
    fn uncertain_decisions_are_never_actionable() {
        use super::candidate::RecordId as R;
        use super::entity::EntityId;
        use super::matching::{Confidence, ConfidenceBasis};
        use super::resolution::ResolutionDecision;

        let id = R {
            source: SourceId(0),
            batch: 0,
            row: 0,
        };
        let _ = id;
        let uncertain = ResolutionDecision::Uncertain {
            candidates: Vec::new(),
            confidence: Confidence::adjusted(0.7, ConfidenceBasis::EvidenceOnly),
        };
        assert!(!uncertain.is_actionable());
        assert!(uncertain.matched_entity().is_none());

        let matched = ResolutionDecision::Match {
            entity: EntityId::FIRST,
            confidence: Confidence::adjusted(0.95, ConfidenceBasis::PriorDecisions(3)),
        };
        assert!(matched.is_actionable());
        assert_eq!(matched.matched_entity(), Some(EntityId::FIRST));
    }
}