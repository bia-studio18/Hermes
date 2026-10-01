use std::{
    fs::File,
    error::Error,
};
use csv::StringRecord;

pub struct CsvReader {
    headers: StringRecord,
    rows: csv::StringRecordsIntoIter<File>,
}

impl CsvReader {
    pub fn from_path(path: &str) -> Result<Self, Box<dyn Error>> {
        let mut reader = csv::Reader::from_path(path)?;

        let headers = reader.headers()?.clone();
        let rows = reader.into_records();

        Ok(Self { headers, rows })
    }

    pub fn headers(&self) -> &StringRecord {
        &self.headers
    }

    pub fn next(&mut self) -> Option<Result<StringRecord, csv::Error>> {
        self.rows.next()
    }
}

