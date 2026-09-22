use pyo3::prelude::*;

#[pyfunction]
fn version() -> &'static str {
    "0.1.0"
}

#[pymodule]
fn _rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(version, m)?)?;
    Ok(())
}