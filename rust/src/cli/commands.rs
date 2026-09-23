use super::Command;

/// Dispatch a parsed subcommand to its handler.
///
/// Handlers that have no Hermes functionality behind them yet return a clear
/// "not implemented" error instead of pretending to succeed.
pub fn exec(command: Command) -> i32 {
    match command {
        Command::Fetch => not_implemented("fetch"),
        Command::Inspect => not_implemented("inspect"),
        Command::Dataset => not_implemented("dataset"),
        Command::Entity => not_implemented("entity"),
    }
}

fn not_implemented(name: &str) -> i32 {
    eprintln!("hermes: '{name}' is not implemented yet");
    1
}
