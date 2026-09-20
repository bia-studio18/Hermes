//! TF-IDF / vector operations over string corpora.

use pyo3::prelude::*;

#[pymodule]
pub fn tfidf(_py: Python<'_>, _module: &Bound<'_, PyModule>) -> PyResult<()> {
    Ok(())
}