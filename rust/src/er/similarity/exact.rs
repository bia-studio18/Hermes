use crate::er::similarity::normalize::normalize;

/// Normalized equality: 1.0 when the two values are the same once normalized,
/// 0.0 otherwise. A miss is not an error.
pub fn exact_similarity(a: String, b: String) -> f64 {
    if normalize(&a) == normalize(&b) {
        1.0
    } else {
        0.0
    }
}