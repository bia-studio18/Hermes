use std::io::{Error, ErrorKind};

#[derive(Debug, Clone, PartialEq)]
pub struct SimilarityScore {
    pub score: f64, 
    pub method: String,
}

impl SimilarityScore {
    pub fn check(score: f64, method: String) -> Result<Self, Error> {
        if (0.0..=1.0).contains(&score) {
            return Ok(Self { score, method });
        }

        Err(Error::new(
            ErrorKind::InvalidInput,
            "The Score should be between 0.0 and 1.0",
        ))
    }

}
