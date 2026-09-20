//! Token-based similarity (Jaccard, token-set/ratio, ...).

use pyo3::prelude::*;

#[pymodule]
pub fn token_similarity(_py: Python<'_>, _module: &Bound<'_, PyModule>) -> PyResult<()> {
    Ok(())
}