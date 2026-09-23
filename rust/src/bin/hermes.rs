//! Native `hermes` CLI entry point.

use std::process::ExitCode;

fn main() -> ExitCode {
    ExitCode::from(_rust::cli::run() as u8)
}
