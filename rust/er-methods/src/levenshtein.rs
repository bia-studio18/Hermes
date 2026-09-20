//! Levenshtein and normalized Levenshtein edit distance.

use pyo3::prelude::*;

#[pymodule]
pub fn levenshtein(_py: Python<'_>, _module: &Bound<'_, PyModule>) -> PyResult<()> {
    Ok(())
}