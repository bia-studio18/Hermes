# Hermes

**The data engine for intelligence pipelines.** Acquire, parse, normalize, validate, profile, store —
and know where every row came from.

Hermes is a **source-available** (not OSI "open source") Python data engine that turns messy
external and existing datasets into clean, profiled, well-understood `Dataset` objects that carry
their own provenance.

It is not a dataframe library. Hermes is the **pipeline layer** around your existing stack
(Polars, PyArrow, Parquet): it brings data in, understands it, cleans and validates it, and hands
you something you can trust.

> **Status: Alpha (v0.2.22).** Everything documented here runs. Features that are still stubs are
> called out explicitly in [Features](#features). Architecture, subsystem specs, ownership and the
> phased roadmap live in [`docs/hermes.md`](docs/hermes.md).

![PyPI downloads](https://img.shields.io/pypi/dm/hermes-plt)

---

## Table of Contents

- [Features](#features)
- [Demo](#demo)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Profiling](#profiling)
  - [The Dataset object](#the-dataset-object)
  - [Parsing, normalization, validation](#parsing-normalization-validation)
  - [Schemas and entities](#schemas-and-entities)
  - [Storage](#storage)
  - [Connectors](#connectors)
  - [Command line](#command-line)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Features

| Capability | What it does |
| --- | --- |
| `hr.profile()` | Full statistical profile: per-column dtype, nulls, uniques, min/max, mean, median, std, top values — plus completeness, duplicate and anomaly counts, date range, frequency |
| `hr.inspect()` | Fast glance without a full scan: row/column counts, column types, detected entity needs |
| `hr.get_freqs()` / `hr.date_ranges()` / `hr.anomaly_count()` | Frequency detection, temporal range detection, IQR-based anomaly counts |
| `hr.parse()` / `hr.read()` / `hr.ingest()` | Parse CSV, JSON, JSONL, Parquet and XML into a `Dataset` |
| `hr.normalize()` | 18 normalization rules: cast, unit/currency/date/country/name/boolean/null cleanup, string strip, round, rename, map value/concept, period parsing, literal |
| `hr.validate()` | 22 validation rules: not-null, unique, unique-combination, type, range, regex/pattern, enum, length, duplicate, null-rate, completeness, cardinality, constant, date range/order, freshness, row count, schema, column, foreign-key, referential |
| `hr.transform()` | Apply a function to a frame or `Dataset`; records a `transform` step in lineage when given a `Dataset` |
| `hr.get_schema()` / `compare_schema()` / `migrate()` | 7 versioned canonical schemas: `entity`, `economic.observation`, `financial.observation`, `market.observation`, `geopolitical.event`, `security.event`, `document` |
| `hr.resolve_entity()` and friends | Entity resolution over bundled country (249) and CIK/ticker (10,422) registries, with fuzzy matching and stable `HRM-` identifiers |
| `hr.save()` / `load()` / `exists()` / `delete()` / `list_datasets()` / `storage_info()` | Filesystem storage backend — Parquet or Arrow IPC, atomic metadata writes, load-time integrity checks |
| Credentials | `hr.set_cred()` / `get_cred()` / `has_cred()` / `list_creds()` / `delete_cred()` persisted to `~/.hermes-plt/credentials.json` |
| Connectors | Binance, Finnhub, FRED, IMF, SEC EDGAR, World Bank, YFinance, OpenSanctions — all on one `BaseConnector` contract with shared retry, rate-limit, auth, normalization, validation and provenance |
| `hr.fetch()` / `fetch_raw()` / `sync()` | Acquisition with retry, rate limiting, pagination, and a 24-hour raw-response cache |
| `Dataset.record()` | Every operation is recorded into lineage and bumps the dataset version |
| Error taxonomy | `HermesError` and 10 typed subclasses (`AcquisitionError`, `ParseError`, `SchemaError`, `NormalizationError`, `ValidationError`, `StorageError`, `QueryError`, `ConfigError`, `ConnectorNotFoundError`, `AuthenticationError`) |
| Rust core | PyO3/maturin extension for entity-resolution primitives and the HTTP client. **Not yet reachable from Python** — see [Limitations](#limitations) |
| Tests | 364 Python tests + 20 Rust tests, run in CI on Python 3.11 / 3.12 / 3.13 alongside `ruff` and `mypy` |

### Limitations

Alpha software, called out plainly:

- **`GDELT` is a stub.** The class exists with a `geopolitical.event` canonical schema but no
  implementation, and it is not registered with `hr.fetch`.
- **`PUBLIC_DATASET`** is a local CSV bundle (HDI, CPI, HRS, NATO, CRS, SIPRI), not a network
  connector. Reach it with `hr.read()` / `hr.ingest()`, not `hr.fetch("public_data")`.
- **Person entity resolution returns nothing.** The `person` entity type is registered with an
  empty registry. Countries resolve by name / ISO-2 / ISO-3; companies resolve by **ticker or CIK
  only** (no company-name index yet).
- **`hermes fetch` does not persist.** It ingests and prints a summary. Use `hr.save()`, or the
  Python API, to write a dataset into storage.
- **The Rust CLI is not implemented.** All four subcommands return exit code 1. The working CLI is
  the Python one; `maturin` builds both, and `[project.scripts]` wires `hermes` to the Python entry
  point.
- **Query engine and dataset catalog exist in the tree but are not exposed** through the top-level
  API or the CLI.

---

## Demo

A real terminal session — CSV in, profiled, stored, queried, and a country resolved to a stable ID:

```console
$ hermes cred init
Credentials initialized at /home/you/.hermes-plt/credentials.json

$ python -c "import hermes as hr; hr.save(hr.read('gdp.csv'), name='gdp')"
Fetched gdp (4 rows, 3 cols)

$ hermes dataset list
gdp

$ hermes dataset info gdp
dataset: gdp  rows: 4  cols: 3  size: 1,172 B  version: 0.0.1  format: parquet

$ hermes inspect gdp
Inspect: gdp  rows: 4  cols: 3  needs: [('country', 'country')]

$ hermes profile gdp
Profile: gdp
Rows: 4  Columns: 3  Duplicates: 0  Deep stats: yes

shape: (3, 10)
┌─────────┬─────────┬───────┬───────┬───┬──────┬─────────┬─────────┬─────────────────┐
│ column  ┆ dtype   ┆ nulls ┆ null% ┆ … ┆ max  ┆ mean    ┆ std     ┆ top 5           │
│ ---     ┆ ---     ┆ ---   ┆ ---   ┆   ┆ ---  ┆ ---     ┆ ---     ┆ ---             │
│ str     ┆ str     ┆ str   ┆ str   ┆   ┆ str  ┆ str     ┆ str     ┆ str             │
╞═════════╪═════════╪═══════╪═══════╪═══╪══════╪═════════╪═════════╪═════════════════╡
│ country ┆ String  ┆ 0     ┆ 0.00  ┆ … ┆ -    ┆ -       ┆ -       ┆ Kenyax2, Perux2 │
│ year    ┆ Int64   ┆ 0     ┆ 0.00  ┆ … ┆ 2024 ┆ 2023.5  ┆ 0.57735 ┆ -               │
│ gdp     ┆ Float64 ┆ 0     ┆ 0.00  ┆ … ┆ 280  ┆ 191.775 ┆ 94.8673 ┆ -               │
└─────────┴─────────┴───────┴───────┴───┴──────┴─────────┴─────────┴─────────────────┘

$ hermes entity resolve "Kenya" --type country
country: Kenya  (HRM-COUNTRY-01XGLAII0BFPBUGNAGHTTH)
  iso3: KEN
  iso2: KE
```

- **Docs** — <https://docs.hermes-plt.xyz>
- **Source** — <https://github.com/ryomenhaider/Hermes>
- **Community** — <https://discord.gg/UeJuEz4YdS>

---

## Installation

Requires **Python 3.11+**.

```bash
pip install hermes-plt
```

Installing from source requires a Rust toolchain, because the wheel is built with
[maturin](https://www.maturin.rs/) and bundles a PyO3 extension:

```bash
git clone https://github.com/ryomenhaider/Hermes.git
cd Hermes
uv sync --all-extras --dev
uv run pytest
```

Optional extras:

```bash
pip install "hermes-plt[yfinance]"   # YFinance connector
```

---

## Quick Start

```python
import hermes as hr
import polars as pl

df = pl.read_csv("gdp.csv")

# 1. Understand it before you trust it
report = hr.profile(df)
print("rows:", report.row_count, "· columns:", report.column_count)
print("duplicates:", report.quality.duplicate_count)
for col in report.columns[:3]:
    print(col.name, "|", col.dtype, "| nulls:", col.null_count, "| unique:", col.unique_count)

# 2. Wrap it, so the data travels with its story
ds = hr.Dataset(name="gdp", data_ref="gdp.csv", data=df)
ds.profile()
print(ds.provenance_info())  # where it came from
print(ds.lineage_info())  # what was done to it

# 3. Store it, with integrity checks on the way back in
hr.save(ds, name="gdp")
hr.list_datasets()  # ['gdp']
hr.storage_info("gdp")

# 4. Hand it to the stack you already use
ds.to_polars()  # polars.DataFrame
ds.to_arrow()  # pyarrow.Table
ds.to_pandas()  # pandas.DataFrame
ds.export("csv")  # raw bytes for your own storage
```

---

## Usage

### Profiling

```python
hr.profile(df)  # MetaData — full statistical profile
hr.profile(path="gdp.csv")  # profile straight from a file
hr.inspect(df)  # fast: counts and types, no deep scan

hr.get_freqs(df)  # detected frequency, e.g. ['yearly']
hr.date_ranges(df)  # per-date-column min/max
hr.anomaly_count(df)  # {'gdp': 2} — IQR-based outlier counts
```

### The Dataset object

`Dataset` is the center of Hermes. It holds your data *and* its metadata together, so a dataset is
never just a file — it is a file **plus its story**.

```python
ds = hr.Dataset(name="gdp", data_ref="gs://imports/gdp.csv", data=df)

ds.inspect()  # InspectReport
ds.profile()  # MetaData
ds.metadata_info()  # MetaData
ds.provenance_info()  # Provenance — where the data came from
ds.lineage_info()  # Lineage — what was done to it
ds.schema_info()  # str | None — raises if no Schema is attached

ds.record("normalized", input_ref="gdp.csv", params={"rules": 18})  # appends to lineage
ds.lineage_info().steps[-1].operation  # 'normalized'
ds.data_version.content_hash  # content hash of the current frame

ds.save("out", format="parquet")  # parquet / csv / json
ds.export("csv")  # raw bytes; "polars"/"arrow"/"pandas" return objects

ds.to_polars()
ds.to_arrow()
ds.to_pandas()
ds.to_lazy()
len(ds)
ds[0]
"gdp" in ds
list(ds)  # delegates to the underlying frame
```

### Parsing, normalization, validation

```python
ds = hr.parse("data.jsonl")  # format inferred from the suffix
ds = hr.read("data.parquet")  # same thing, reads straight to a Dataset
ds = hr.ingest("exports/gdp.csv")  # local path, or a connector name

hr.normalize(df, report=True)  # -> NormalizationResult when report=True
res = hr.validate(df)  # -> ValidationResult

# transform takes a frame (-> frame) or a Dataset (-> Dataset, with lineage recorded)
hr.transform(df, fn=lambda d: d.with_columns(pl.col("gdp") * 1e9))
hr.transform(ds, fn=lambda d: d.with_columns(pl.col("gdp") * 1e9))
```

`hr.transform` is the escape hatch for anything the normalizers do not cover. It requires a
callable, and anything you pass after it is forwarded to that callable.

`hr.parse` and `hr.read` accept a local path or raw bytes/strings — **not** a URL. To pull from a
URL, save it first, or write a connector. `hr.ingest` dispatches on the argument: if it resolves to
an existing path it reads the file, otherwise it treats the string as a connector name.

`hr.validate` returns a `ValidationResult` rather than raising. Inspect it:

```python
res = hr.validate(df, schema="economic.observation")

if not res.passed:  # bool(res) is the same check
    print(res.summary())  # per-rule PASSED/FAILED lines
    for rule in res.results:
        for v in rule.violations:
            print(rule.rule, v.field, v.row, v.message, v.expected)

print(res.success, res.passed, res.errors, res.warnings)
```

Pass `schema=` to validate against a canonical schema, or `rules=[...]` to supply your own.

### Schemas and entities

```python
schema = hr.get_schema("economic.observation")  # -> Result
schema.data.field_names()  # ['entity_id', 'date', 'indicator', 'value', 'unit', ...]
schema.data.primary_keys  # ['entity_id', 'date', 'indicator']
schema.data.validate_data(df)  # -> list[str] of problems
schema.data.compatibility(other)  # -> Compatibility
```
hr.register_schema(my_schema)                       # -> Result
hr.compare_schema("entity", "economic.observation")  # -> Result

result = hr.migrate(entities_df,
                    from_schema="entity",
                    to_schema="economic.observation",
                    rename={"name": "indicator"})
if not result.is_success():
    print(result.errors)   # required fields still missing after the rename

hr.resolve_entity("Kenya")            # Result
hr.resolve_country("KEN")              # by name, ISO-2 or ISO-3
hr.resolve_company("AAPL")             # by ticker or CIK
hr.resolve_security("AAPL"); hr.resolve_organization("AAPL")

hr.hrm_id("country")           # 'HRM-COUNTRY-01XGLAII0BFPBUGNAGHTTH'
```

### Storage

One backend today: `FilesystemStorage`, selected automatically. On disk:

```
<storage_root>/datasets/<name>/data.parquet     # or data.ipc
<storage_root>/datasets/<name>/metadata.json    # written atomically
```

```python
hr.save(ds, name="gdp", overwrite=True)  # format="parquet" (default) or "ipc"
hr.load("gdp")                           # -> Dataset
hr.exists("gdp")
hr.list_datasets()
hr.storage_info("gdp")                   # records, columns, created/modified
hr.delete("gdp")
```

Loads run integrity checks and raise `StorageCorruptionError` on a mismatch.

### Connectors

```python
# one API for every source; kwargs go straight to the connector
hr.fetch("world_bank", country_code="KEN", indicator_code="NY.GDP.MKTP.CD", frequency="annual")
hr.fetch("fred", series_id="NYGDP")
hr.fetch("binance", mode="spot", endpoint="ohlcv", symbol="BTCUSDT", interval="1d", limit=500)

hr.fetch_raw("world_bank", country_code="KEN", indicator_code="NY.GDP.MKTP.CD")  # no cache/Dataset
hr.sync("world_bank", country_code="KEN", indicator_code="NY.GDP.MKTP.CD")  # force=True
```

`Binance.fetch` is parameterised by `(mode, endpoint, symbol)`, where `mode` is `spot` or `future`
and `endpoint` is one of `ohlcv`, `trades`, `aggregated_trades`, `order_book`, `best_bid_ask`,
`24hr`, `exchangeInfo`, `fundingRate`, `openInterest`, `premiumIndex`, `openInterestHist`,
`longShortRatio`, and the top long/short ratio endpoints.

Registered: `binance`, `finnhub`, `fred`, `imf`, `opensanctions`, `sec`, `world_bank`, `yfinance`.
Each returns its canonical schema — `market.observation`, `economic.observation`,
`financial.observation`, or `entity` — already normalized and validated, with provenance attached.

Credentials are read from the credential store, not from arguments:

```python
hr.set_cred("fred", "your-api-key")
hr.set_cred("sec_email", "you@example.com")  # SEC also needs sec_username
hr.list_creds()
```

### Command line

```
hermes [--storage PATH] <command>
```

| Command | Purpose |
| --- | --- |
| `hermes fetch <source> [dataset]` | Fetch from a connector or local file |
| `hermes inspect <name>` | Row/column counts, types, detected entity needs |
| `hermes profile <name> [--json]` | Full column-stat table for a stored dataset |
| `hermes entity resolve <query> [--type]` | Resolve an entity to an `HRM-` identifier |
| `hermes dataset list \| info <name> \| delete <name>` | Manage stored datasets |
| `hermes cred init \| set <name> \| get <name> [--show] \| list \| delete <name>` | Manage the credential store |

```console
$ hermes --storage ./local-store profile gdp
```

Every command returns exit code `0` on success and `1` on failure, with the error on stderr.

---

## Configuration

Hermes has no config file and no daemon. Three things are configurable:

| Setting | How | Default |
| --- | --- | --- |
| Storage root | `hr.configure(storage_root=...)`, `HERMES_STORAGE_ROOT`, or `hermes --storage` | `~/.hermes-plt/storage` |
| Credentials | `hr.set_cred(...)` / `hermes cred set` | `~/.hermes-plt/credentials.json` |
| Raw fetch cache | automatic | `~/.hermes_cache/raw`, 24h TTL |

Precedence is **explicit setting → environment variable → default**.

```python
import hermes as hr

hr.configure(storage_root="/srv/hermes/datasets")
hr.get_config().storage_root  # PosixPath('/srv/hermes/datasets')
```

API keys for connectors are read from the credential store, not from environment variables. The
`.env.example` file in this repo is a convenience for local development only — Hermes itself reads
`HERMES_STORAGE_ROOT` and nothing else.

> **Credentials are stored as plain JSON** at `~/.hermes-plt/credentials.json` (mode `0600`). It is
> not encrypted. On shared machines, prefer a secret manager and inject at runtime.

---

## API Reference

`hermes` exports 52 names. Signatures as implemented:

**Acquisition** — `fetch(source, **kwargs)`, `fetch_raw(source, **kwargs)`,
`ingest(source, **kwargs) -> Dataset`, `read(path, format=None, **kwargs) -> Dataset`,
`sync(source, **kwargs) -> Dataset`

**Data** — `parse(data, format=None, **kwargs) -> Dataset`,
`normalize(data, rules=None, report=False, context=None)`,
`validate(data, rules=None, schema=None, context=None) -> ValidationResult`,
`transform(data, fn, **kwargs)`,
`profile(data=None, path=None, source=None) -> MetaData`, `inspect(data) -> InspectReport`,
`get_freqs(data)`, `date_ranges(data)`, `anomaly_count(data, threshold=1.5)`,
`resolve_data(data, keys=None)`

**Entities** — `resolve_entity(query, entity_type=None) -> Result`, `resolve_country(query)`,
`resolve_company(query)`, `resolve_security(query)`, `resolve_organization(query)`,
`resolve_person(query)`

**Schemas** — `get_schema(name, version=None) -> Result`, `register_schema(schema) -> Result`,
`compare_schema(a, b) -> Result`, `migrate(data, from_schema, to_schema, *, rename=None) -> Result`

**Storage** — `save(dataset, name=None, overwrite=False, format="parquet") -> Result`,
`load(name) -> Result`, `exists(name) -> Result`, `delete(name) -> Result`,
`list_datasets() -> Result`, `storage_info(name) -> Result`

**Credentials** — `set_cred(name, value)`, `get_cred(name)`, `has_cred(name)`,
`list_creds() -> list[str]`, `delete_cred(name)`

**Config** — `configure(**settings) -> HermesConfig`, `get_config() -> HermesConfig`

**Core** — `Dataset`, `Result`, `hrm_id(entity_type, *, timestamp_ms=None) -> str`

**Errors** — `HermesError`, `AcquisitionError`, `AuthenticationError`, `ConfigError`,
`ConnectorNotFoundError`, `NormalizationError`, `ParseError`, `QueryError`, `SchemaError`,
`StorageError`, `ValidationError`

Most fallible calls return a `Result` rather than raising. `Result` exposes `.is_success()`,
`.data`, `.metadata`, `.errors`, `.warnings` and `.statistics`.

**Not yet exported** — the query engine, dataset catalog, and scheduler are implemented in the tree
but not wired into the top-level API or the CLI.

Longer-form reference docs live in [`documentation/`](documentation/).

---

## Contributing

Hermes is source-available and built in the open. Good contributions: connectors, parsers,
normalizers, validators, profilers, storage backends, query integrations, documentation, tests, and
performance.

Before you start:

1. Read [`docs/hermes.md`](docs/hermes.md) — it is the single source of truth for architecture,
   subsystem ownership, and what is currently in flight.
2. Open an issue or a draft PR so the work does not collide with something already underway.

Run the full check suite before pushing — it is the same suite CI runs:

```bash
uv run ruff check . && uv run mypy hermes && uv run pytest
```

or all of it via `./cmd.sh`. Tests live in `tests/` (364 Python) and `rust/src/` (20 Rust); new
behavior needs a test.

Security issues: **do not** open a public issue. Follow [`SECURITY.md`](SECURITY.md).

---

## License

Hermes is **source-available** under the **Elastic License 2.0 (ELv2)**. This is **not** an
OSI-approved open source license; it is a deliberate choice.

**You may** read, use, modify, fork and redistribute Hermes freely, including for internal
commercial use.

**You may not** offer Hermes to third parties as a hosted or managed service, and **you may not**
strip the notices or use the trademarks. Embedding or hosting Hermes commercially requires a
**Hermes Enterprise** license (support, SLAs, managed-hosting rights) from the copyright holders.

Full terms: [`LICENSE.md`](LICENSE.md).

---

## Acknowledgments

- **[Polars](https://pola.rs/)** and **[PyArrow](https://arrow.apache.org/docs/python/)** — the
  dataframe and columnar formats underneath every `Dataset`.
- **[Maturin](https://www.maturin.rs/)** and **[PyO3](https://pyo3.rs/)** — the Python/Rust bridge
  that makes the Rust core a single `pip install` away.
- **[Apache Arrow](https://arrow.apache.org/)** — Parquet and IPC on-disk formats.
- The data providers Hermes connects to, for making this data public in the first place:
  **[Binance](https://www.binance.com/)**, **[Finnhub](https://finnhub.io/)**,
  **[FRED](https://fred.stlouisfed.org/)** (Federal Reserve Bank of St. Louis),
  **[IMF](https://www.imf.org/external/sdmx)**, **[SEC EDGAR](https://www.sec.gov/edgar)**,
  **[World Bank](https://data.worldbank.org/)**,
  **[OpenSanctions](https://www.opensanctions.org/)**, and **[GDELT](https://www.gdeltproject.org/)**.
- **[ISO 3166](https://www.iso.org/iso-3166-country-codes.html)** and
  **[ISO 4217](https://www.iso.org/iso-4217-currency-codes.html)** — the country and currency
  registries behind the normalizers.
- Everyone who has filed an issue, reviewed a PR, or tested a release.

Built and maintained by **Haider Ali & the Hermes Team** — <https://github.com/ryomenhaider/Hermes>

---

**Bring the data in. Make it usable. Know where it came from. Build on it.**
