//! Hermes entity-resolution engine: Rust implementation of the ER methods,
//! exposed to Python as `hermes.er.methods._native` (PyO3).

use pyo3::prelude::*;

pub mod blocking;
pub mod candidate;
pub mod compare;
pub mod jaro_winkler;
pub mod levenshtein;
pub mod similarity;
pub mod tfidf;
pub mod token_similarity;
pub mod vector;

/// Create a PyO3 child module, run `init`, attach it to the parent as a submodule,
/// and register it in `sys.modules` so Python can dot-import it.
fn register_submodule<'py>(
    py: Python<'py>,
    parent: &Bound<'py, PyModule>,
    name: &str,
    init: fn(Python<'py>, &Bound<'py, PyModule>) -> PyResult<()>,
) -> PyResult<()> {
    let full = format!("hermes.er.methods._native.{name}");
    let submodule = PyModule::new(py, &full)?;
    init(py, &submodule)?;
    parent.add_submodule(&submodule)?;
    PyModule::import(py, "sys")?
        .getattr("modules")?
        .set_item(&full, &submodule)?;
    Ok(())
}

#[pymodule]
fn _native(py: Python<'_>, module: &Bound<'_, PyModule>) -> PyResult<()> {
    register_submodule(py, module, "levenshtein", levenshtein::levenshtein)?;
    register_submodule(py, module, "jaro_winkler", jaro_winkler::jaro_winkler)?;
    register_submodule(py, module, "similarity", similarity::similarity)?;
    register_submodule(py, module, "token_similarity", token_similarity::token_similarity)?;
    register_submodule(py, module, "blocking", blocking::blocking)?;
    register_submodule(py, module, "candidate", candidate::candidate)?;
    register_submodule(py, module, "compare", compare::compare)?;
    register_submodule(py, module, "tfidf", tfidf::tfidf)?;
    // vector: reserved for embedding/vector operations; registered when implemented.
    Ok(())
}