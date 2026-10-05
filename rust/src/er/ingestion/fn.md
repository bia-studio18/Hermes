## Hermes Rust Ingestion Layer Functions

> Superseded by the implemented layout in `ingestion/mod.rs`. There is no
> `record.rs`/`RawRecord`: readers emit `data::RecordBatch`, the Hermes batch
> type, so ingestion adds no record model of its own. Everything below is the
> original plan.

```rust
// Entry point
ingest(source) -> Result<IngestedDataset>

// Source detection
detect_source_type(input) -> SourceType

// Readers
read_csv(...)
read_json(...)
read_jsonl(...)
read_parquet(...)
read_database(...)
read_stream(...)

// Normalization at ingestion level
coerce_value(value, target_type) -> Value
handle_null(value) -> Option<Value>

// Streaming/batching
read_batch(source, batch_size) -> Result<RecordBatch>
```

### Build order

1. **Core Hermes representation**
2. **Source abstraction**
3. **Reader abstraction**
4. **CSV reader**
5. **JSON reader**
6. **JSONL reader**
7. **Parquet reader**
8. **Database/API/stream readers**
9. **Unified `ingest()` entry point**

### `ingestion/`

```text
ingestion/
├── mod.rs
├── source.rs
├── reader.rs
├── record.rs
├── csv.rs
├── json.rs
├── jsonl.rs
├── parquet.rs
├── database.rs
├── api.rs
└── stream.rs
```

### What each file contains

| File          | Responsibility              | Main things                             |
| ------------- | --------------------------- | --------------------------------------- |
| `mod.rs`      | Public ingestion API        | `ingest()`, module exports              |
| `source.rs`   | Describe external sources   | `Source` enum, `SourceMetadata`         |
| `reader.rs`   | Common reader interface     | `Reader` trait                          |
| `record.rs`   | Hermes input representation | `RawRecord`, `RawValue`, `RecordStream` |
| `csv.rs`      | Read CSV                    | `CsvReader`                             |
| `json.rs`     | Read JSON                   | `JsonReader`                            |
| `jsonl.rs`    | Read JSON Lines             | `JsonlReader`                           |
| `parquet.rs`  | Read Parquet                | `ParquetReader`                         |
| `database.rs` | Read database records       | `DatabaseReader`                        |
| `api.rs`      | Read API responses          | `ApiReader`                             |
| `stream.rs`   | Read streaming sources      | `StreamReader`                          |

### Core pieces

`source.rs`

```rust
enum Source {
    File(...),
    Database(...),
    Api(...),
    Stream(...),
}
```

`reader.rs`

```rust
trait Reader {
    fn next(&mut self) -> Result<Option<RawRecord>>;
}
```

`record.rs`

```rust
struct RawRecord {
    fields: ...
}

enum RawValue {
    Null,
    String(...),
    Number(...),
    Boolean(...),
    Array(...),
    Object(...),
}
```

`mod.rs`

```rust
fn ingest(source: Source) -> Result<...>
```

That's the initial ingestion scope. **Build `record.rs → source.rs → reader.rs → csv.rs → json.rs → jsonl.rs`, then add the remaining readers.**
