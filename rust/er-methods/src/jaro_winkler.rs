//! Jaro and Jaro-Winkler string similarity.

use pyo3::prelude::*;

#[pymodule]
pub fn jaro_winkler(_py: Python<'_>, _module: &Bound<'_, PyModule>) -> PyResult<()> {
    Ok(())
}