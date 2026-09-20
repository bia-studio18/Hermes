//! Blocking / indexing: cheap keys that reduce the candidate set.

use pyo3::prelude::*;

#[pymodule]
pub fn blocking(_py: Python<'_>, _module: &Bound<'_, PyModule>) -> PyResult<()> {
    Ok(())
}