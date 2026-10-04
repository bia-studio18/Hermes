//! Thin PyO3 wrapper around the Hermes entity-resolution core.
//!
//! Exposes `hermes._rust.er`, including the `HermesErError` exception. All
//! comparison work happens in the core modules; algo names arrive as strings
//! here so the Rust enums stay out of the Python surface.

use chrono::NaiveDate;
use pyo3::create_exception;
use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use pyo3::types::PyModule;

// Aliased: the pyfunction names below deliberately shadow the core ones.
use crate::er::ingestion as ingest;
use crate::er::similarity as core;

create_exception!(_rust.er, HermesErError, PyException);

fn err(message: impl Into<String>) -> PyErr {
    HermesErError::new_err(message.into())
}

/// Guesses how a source should be read: file extension first, then URL scheme.
#[pyfunction]
fn identify_source(source: &str) -> &'static str {
    match ingest::identify_source(source) {
        ingest::Source::CSV => "CSV",
        ingest::Source::JSON => "JSON",
        ingest::Source::PARQUET => "PARQUET",
        ingest::Source::API => "API",
        ingest::Source::DATABASE => "DATABASE",
        ingest::Source::STREAMING => "STREAMING",
        ingest::Source::UNKNOWN => "UNKNOWN",
    }
}

/// NFC-normalizes, trims and lowercases a value.
#[pyfunction]
fn normalize(value: &str) -> String {
    core::normalize(value)
}

/// 1.0 when both values are equal once normalized, else 0.0.
#[pyfunction]
fn exact_similarity(a: &str, b: &str) -> f64 {
    core::exact_similarity(a.to_string(), b.to_string())
}

#[pyfunction]
fn jaro_similarity(a: &str, b: &str) -> f64 {
    core::jaro_similarity(a.to_string(), b.to_string())
}

#[pyfunction]
fn jaro_winkler_similarity(a: &str, b: &str) -> f64 {
    core::jaro_winkler_similarity(a.to_string(), b.to_string())
}

#[pyfunction]
fn levenshtein_similarity(a: &str, b: &str) -> f64 {
    core::levenshtein_similarity(a.to_string(), b.to_string())
}

#[pyfunction]
fn damerau_levenshtein_similarity(a: &str, b: &str) -> f64 {
    core::damerau_levenshtein_similarity(a.to_string(), b.to_string())
}

/// `algo` is one of jaccard, cosine, sorensen_dice, overlap, tversky, bag,
/// roberts.
#[pyfunction]
fn token_similarity(a: &str, b: &str, algo: &str) -> PyResult<f64> {
    let algo = match algo {
        "jaccard" => core::TokenAlgo::Jaccard,
        "cosine" => core::TokenAlgo::Cosine,
        "sorensen_dice" => core::TokenAlgo::SorensenDice,
        "overlap" => core::TokenAlgo::Overlap,
        "tversky" => core::TokenAlgo::Tversky,
        "bag" => core::TokenAlgo::Bag,
        "roberts" => core::TokenAlgo::Roberts,
        other => return Err(err(format!("unknown token algo: {other}"))),
    };
    Ok(core::token_similarity(a.to_string(), b.to_string(), algo))
}

/// Dates are ISO `YYYY-MM-DD`. `algo` is exact, day_difference or year_month;
/// day_difference scores 1.0 on the same day and 0.0 once `max_days` apart.
#[pyfunction]
#[pyo3(signature = (a, b, algo, max_days=None))]
fn date_similarity(a: &str, b: &str, algo: &str, max_days: Option<u32>) -> PyResult<f64> {
    let parse = |value: &str| {
        NaiveDate::parse_from_str(value, "%Y-%m-%d")
            .map_err(|e| err(format!("{value:?} is not an ISO date: {e}")))
    };
    let algo = match algo {
        "exact" => core::DateAlgo::Exact,
        "day_difference" => core::DateAlgo::DayDifference {
            max_days: max_days.ok_or_else(|| err("day_difference needs max_days"))?,
        },
        "year_month" => core::DateAlgo::YearMonth,
        other => return Err(err(format!("unknown date algo: {other}"))),
    };
    Ok(core::date_similarity(&parse(a)?, &parse(b)?, algo).similarity.score)
}

/// `algo` is exact, username, domain or combined.
#[pyfunction]
fn email_similarity(a: &str, b: &str, algo: &str) -> PyResult<f64> {
    let algo = match algo {
        "exact" => core::EmailAlgo::Exact,
        "username" => core::EmailAlgo::Username,
        "domain" => core::EmailAlgo::Domain,
        "combined" => core::EmailAlgo::Combined,
        other => return Err(err(format!("unknown email algo: {other}"))),
    };
    core::email_similarity(a.to_string(), b.to_string(), algo)
        .map(|result| result.similarity.score)
        .map_err(|e| err(e.to_string()))
}

/// `algo` is absolute, relative or normalized; normalized needs both `min` and
/// `max` bounds.
#[pyfunction]
#[pyo3(signature = (a, b, algo, min=None, max=None))]
fn numeric_similarity(a: f64, b: f64, algo: &str, min: Option<f64>, max: Option<f64>) -> PyResult<f64> {
    let algo = match algo {
        "absolute" => core::NumericAlgo::AbsoluteDifference,
        "relative" => core::NumericAlgo::RelativeDifference,
        "normalized" => core::NumericAlgo::NormalizedDifference {
            min: min.ok_or_else(|| err("normalized needs min"))?,
            max: max.ok_or_else(|| err("normalized needs max"))?,
        },
        other => return Err(err(format!("unknown numeric algo: {other}"))),
    };
    core::numeric_similarity(a, b, algo)
        .map(|result| result.similarity.score)
        .map_err(|e| err(e.to_string()))
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    let er = PyModule::new(m.py(), "er")?;
    er.add_function(wrap_pyfunction!(identify_source, &er)?)?;
    er.add_function(wrap_pyfunction!(normalize, &er)?)?;
    er.add_function(wrap_pyfunction!(exact_similarity, &er)?)?;
    er.add_function(wrap_pyfunction!(jaro_similarity, &er)?)?;
    er.add_function(wrap_pyfunction!(jaro_winkler_similarity, &er)?)?;
    er.add_function(wrap_pyfunction!(levenshtein_similarity, &er)?)?;
    er.add_function(wrap_pyfunction!(damerau_levenshtein_similarity, &er)?)?;
    er.add_function(wrap_pyfunction!(token_similarity, &er)?)?;
    er.add_function(wrap_pyfunction!(date_similarity, &er)?)?;
    er.add_function(wrap_pyfunction!(email_similarity, &er)?)?;
    er.add_function(wrap_pyfunction!(numeric_similarity, &er)?)?;
    er.add("HermesErError", m.py().get_type::<HermesErError>())?;
    m.add_submodule(&er)?;
    Ok(())
}