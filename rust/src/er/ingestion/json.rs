use serde_json::Value;
use std::{
    collections::HashMap,
    // io::BufReader,
    // fs::File,
    // error::Error
};

pub type Record = HashMap<String, Value>;

struct JsonReader {
    records: std::vec::IntoIter<Record>,
}

impl JsonReader{
    pub fn from_path(_path: &str) {
        

    }
}