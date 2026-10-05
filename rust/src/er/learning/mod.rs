//! Feedback in, a versioned model out.

mod feedback;
mod model;

pub use feedback::{Feedback, FeedbackType};
pub use model::{FeedbackWeights, Learning, LearningModel, ModelKind, NoLearning};