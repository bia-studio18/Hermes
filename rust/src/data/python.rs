//! Thin PyO3 wrapper around the Hermes Dataset IR.
//!
//! Exposes `hermes._rust.data.HermesDataset`. Python holds this handle and calls
//! into the representation through it; Arrow and Polars never cross the
//! boundary.

use pyo3::prelude::*;
use pyo3::types::PyModule;

use crate::data::{HermesDataset, RepresentationKind};

/// Python view of [`HermesDataset`]. Holds the Rust value, not a copy of it.
#[pyclass(name = "HermesDataset")]
pub struct PyHermesDataset {
    inner: HermesDataset,
}

#[pymethods]
impl PyHermesDataset {
    /// Empty in-memory dataset. Placeholder until ingestion exists.
    #[new]
    fn new() -> Self {
        Self {
            inner: HermesDataset::in_memory(Vec::new()),
        }
    }

    /// Name of the backing representation: `InMemory`, `Streaming`, `Lazy`,
    /// `MemoryMapped` or `Remote`.
    fn kind(&self) -> &'static str {
        match self.inner.kind() {
            RepresentationKind::InMemory => "InMemory",
            RepresentationKind::Streaming => "Streaming",
            RepresentationKind::Lazy => "Lazy",
            RepresentationKind::MemoryMapped => "MemoryMapped",
            RepresentationKind::Remote => "Remote",
        }
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    let data = PyModule::new(m.py(), "data")?;
    data.add_class::<PyHermesDataset>()?;
    m.add_submodule(&data)?;
    Ok(())
}