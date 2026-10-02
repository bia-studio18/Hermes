mod csv;
mod json;
mod parquet;

pub fn ingest() {

}

pub fn read(source: &str){
    let ext = std::path::Path::new(source)
        .extension()
        .and_then(|ext| ext.to_str())
        .unwrap_or("");
    
    match ext {
        "json" => {

        },
        "csv" => {
                let mut reader = csv::CsvReader::from_path(source).unwrap();
                println!("Headers: {:?}", reader.headers());

                while let Some(row) = reader.next() {
                    for (header, value) in reader.headers().iter().zip(row.iter()) {
                        println!("{}: {:?}", header, value);
                    }
                }
        },
        "parquet" => {

        },
        _ => println!("Error")
    };
}

pub fn infer_schema(){

}

pub fn infer_field_type(){

}

pub fn infer_field_semantics(){

}

pub fn create_record(){

}

pub fn validate_record(){

}

pub fn attach_provenance(){

}