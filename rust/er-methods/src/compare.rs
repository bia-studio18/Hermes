//! Large-scale / bulk pairwise comparisons across record sets.

use pyo3::prelude::*;

#[pymodule]
pub fn compare(_py: Python<'_>, _module: &Bound<'_, PyModule>) -> PyResult<()> {
    Ok(())
}