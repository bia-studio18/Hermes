//! General string similarity / distance measures (exact, n-gram, hamming, ...).

use pyo3::prelude::*;

#[pymodule]
pub fn similarity(_py: Python<'_>, _module: &Bound<'_, PyModule>) -> PyResult<()> {
    Ok(())
}