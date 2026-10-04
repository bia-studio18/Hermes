use std::path::Path;

#[derive(Debug, PartialEq, Eq)]
pub enum Source {
    CSV,
    JSON,
    PARQUET,
    API,
    DATABASE,
    STREAMING,
    UNKNOWN,
}

pub fn identify_source(source: &str) -> Source {
    if let Some(ext) = Path::new(source).extension().and_then(|e| e.to_str()) {
        match ext.to_lowercase().as_str() {
            "csv" => return Source::CSV,
            "json" => return Source::JSON,
            "parquet" => return Source::PARQUET,
            _ => {}
        }
    }

    let source_lower = source.to_lowercase();
    
    if source_lower.starts_with("http://") || source_lower.starts_with("https://") {
        Source::API
    } else if source_lower.starts_with("postgres://") 
        || source_lower.starts_with("postgresql://") 
        || source_lower.starts_with("mysql://") 
        || source_lower.starts_with("sqlite://") 
        || source_lower.starts_with("mongodb://") 
    {
        Source::DATABASE
    } else if source_lower.starts_with("kafka://") 
        || source_lower.starts_with("amqp://") 
        || source_lower.starts_with("mqtt://") 
        || source_lower.starts_with("ws://") 
        || source_lower.starts_with("wss://") 
    {
        Source::STREAMING
    } else {
        Source::UNKNOWN
    }
}
