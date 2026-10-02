use serde_json::Value;
use std::{
    collections::HashMap,
    io::BufReader,
    fs::File,
    error::Error
};

pub type Record = HashMap<String, Value>;
type Item = Result<Record, serde_json::Error>;
type JsonStream = serde_json::StreamDeserializer<'static, serde_json::de::IoRead<BufReader<File>>, Record>;

pub struct JsonReader {
    stream: JsonStream,
}

impl JsonReader {
    pub fn from_path(path: &str) -> Result<Self, Box<dyn Error>> {
        let file = File::open(path)?;
        let reader = BufReader::new(file);
        
        let stream = serde_json::Deserializer::from_reader(reader).into_iter::<Record>();
        
        Ok(Self { stream })
    }

    pub fn next(&mut self) -> Option<Item> {
        self.stream.next()
    }
}
