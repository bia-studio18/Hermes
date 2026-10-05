//! The decision layer.

mod decision;
mod resolver;
mod result;

pub use decision::{NoMatchReason, ResolutionDecision, Thresholds};
pub use resolver::{action_for, resolve, Resolver};
pub use result::{EntityAction, ResolutionReport, ResolutionResult};