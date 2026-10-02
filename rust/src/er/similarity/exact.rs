use std::io::{Error, ErrorKind};
use crate::er::similarity::normalize::normalize;


pub fn exact_similarity(a: String, b: String) -> Result<f64, Error> {
    let normalized_a = normalize(&a);
    let normalized_b = normalize(&b);

    if normalized_a == normalized_b {
        return Ok(1.0);
        
    }
    Err(Error::new(
        ErrorKind::InvalidData,
        "The Score should be between 0.0 and 1.0",
    ))
}