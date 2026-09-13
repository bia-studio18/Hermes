# Hermes

> **One document for architecture, engineering, roadmap, and strategy.**
> This file replaces the previous `docs/**` markdown files (consolidated here) and is the single
> source of truth for the repository. `res/` holds personal scratch docs and is gitignored.

**Status:** Alpha. Source-available under Elastic License 2.0 (ELv2) — see [Part G](#part-g--positioning-licensing--credibility).
Every checkbox in [Part D](#part-d--subsystem-engineering-spec) is tracked here and in the code.

---

## Part A — What Hermes Is

### Elevator

Hermes is a Python-native **data engine** that turns messy external and existing data into clean,
profiled, well-understood, provenance-tracked datasets — and then **serves those datasets for
finance and defense**, resolved by real-world entity.

### The three layers

| Layer | What it is | Customer-visible artifact |
|---|---|---|
| **1. General data engine** | A domain-agnostic data lifecycle: `fetch/ingest → parse → normalize → validate → canonical Dataset`, with metadata, provenance, and lineage attached | `Dataset`, the `hr.*` engine API |
| **2. Special datasets builder** | Curated, versioned canonical datasets (finance & defense) built on the engine | Canonical `Dataset`s in the catalog (`list / search / get`) |
| **3. Data provider** | Entity-centric data access: resolve an entity, then pull its datasets on demand | `hr.resolve_company("AAPL").financials` etc. |

Each layer depends only on the one above it. **Core never knows about finance or defense**;
the entity registry and the provider layer are the only places that know entity types.

### Entity-centric API (the product's face)

```python
import hermes as hr

apple = hr.resolve_company("AAPL")

apple.financials        # SEC/Finnhub financials
apple.market_data       # OHLCV/history via market connectors
apple.fillings          # SEC filings
apple.xxxxx             # extensible per-domain datasets
```

### Entity scope (v1)

- **~100,000 entities**: **companies, countries, and persons** — for **finance and defense**.
- Resolvable by any practical identifier or alias: ticker, CIK, ISIN, LEI, name, ISO-2/ISO-3,
  numeric country code, alias.
- The entity registry is an anchor asset: it turns the engine's outputs into a data product and is
  a competitor-hard moat (see [Part G](#part-g--positioning-licensing--credibility)).

### Product direction

```
1. GENERAL DATA ENGINE   — domain-agnostic lifecycle for ANY source
2. SPECIAL DATASETS       — curated canonical datasets for finance & defense
3. DATA PROVIDER         — entity-centric access to those datasets
```

Other domains (healthcare, trade, energy, climate, geopolitics) are **potentially later**, built the
same way on top of Core. Nothing domain-specific goes into Core.

> **De-scoped from the v1 product identity:** the heavy standalone feature engines (financial
> TA/fundamentals, country-risk pipelines) and the old domain scaffolding were removed. Feature work
> is only considered again after the engine + provider layers are real.

---

## Part B — Data Lifecycle

### The lifecycle

Data must go from **fetching to serving with minimal user effort**, with the complexity kept inside
Hermes:

```text
External Source / File / API
    ↓  fetch() / ingest()
Raw data
    ↓  parse                     → raw becomes easy-to-understand structured records
    ↓  normalize                 → parsed data becomes the Hermes representation
    ↓  validate                  → checked for missing values, outliers, schema conformance
    ↓  metadata + provenance + lineage
Canonical Dataset
    ↓  store → query → version → export
```

### Dataset — the central abstraction

A `Dataset` is a **representation and reference** of data, not a copy of the entire payload:

- It holds a **reference to where the data lives** (e.g. a parquet path / storage location), so data is
  loaded **on demand** rather than held fully in memory from the start.
- It carries the data's complete story: **lineage, provenance, metadata, schema, name, UUID, and
  version**.

By construction, a Hermes dataset is never "just a file" — it is a file plus the story of how it was
produced and what it contains.

### Convergence requirement

API-sourced data and file-sourced data must converge into the **same internal representation**, so all
downstream stages (normalize, validate, profile, query, export) behave identically regardless of origin.
Parsing produces the source-agnostic intermediate record representation; normalization maps it onto the
canonical Hermes representation.

---

## Part C — Architecture

### Package layout (current)

```text
hermes/
├── __init__.py            # Public facade
├── acquisition/           # cache · client · retry · rate_limit · pagination · sync
├── api/                   # acquire · data · datasets · entities · schemas · storage
├── cli/                   # hermes commands
├── connectors/            # binance · finnhub · fred · gdelt · imf · opensanctions ·
│                          # public_data · sec · world_bank · yfinance
├── constants.py
├── core/                  # dataset · errors · lineage · metadata · provenance · result · versioning · config
├── datasets/              # catalog · models · registry
├── entities/              # aliases · companies · countries · models · registry · resolver
├── export/                # csv · json · parquet · arrow
├── features/              # (de-scoped) financial · country_risk · decorator · registry
├── metadata/              # extractor · models · registry
├── normalization/         # engine · mapping · rules · errors
├── parsing/               # engine · records · csv_parser · json_parser · parquet_parser · xml_parser · errors
├── query/                 # engine · filters · expressions
├── schemas/               # base · registry · entity · document · economic · financial · market · geopolitical · security
├── storage/               # base · filesystem · parquet · duckdb
└── validation/            # engine · checks · contracts · reports · errors

data/datasets/             # bundled static datasets
tests/                     # unit · connectors · features · integration
```

### Responsibilities by subsystem

| Subsystem | Owns | Not owned here |
|---|---|---|
| `__init__.py` | Public `hr.*` facade | feature logic |
| `api/` | Thin translation of user ops → internal ops | business logic |
| `acquisition/` | HTTP client, caching, retry, rate limiting, pagination, sync | per-source fetches |
| `connectors/` | Per-source acquisition + parse/normalize/map/schema | generic infrastructure |
| `core/` | Dataset, errors, metadata, provenance, lineage, versioning | domain logic |
| `schemas/` | Canonical schema registry, versions, migration | acquisition |
| `parsing/` | Format → structured records | semantic normalization |
| `normalization/` | Source → canonical normalization | acquisition logic |
| `validation/` | Checks, contracts, reports; errors vs warnings | source knowledge |
| `metadata/` | Descriptive metadata extraction | data modification |
| `entities/` | Entity registry, aliases, resolution | data acquisition |
| `datasets/` | Dataset catalog & registry | persistence engine |
| `storage/` | Where datasets persist | query execution |
| `query/` | Filtering/projection/aggregation/joins/SQL | storage layout |
| `export/` | To external formats/tools | caching |
| `features/` | (de-scoped) derived analytics | connector I/O |

### Canonical schemas

A canonical schema is the contract between sources and the rest of Hermes:

```text
Source A ─→ Mapping ─→ Canonical Hermes Schema ←─ Mapping ←─ Source B
```

The v1 canonical schemas are: **Entity · Economic observation · Financial observation · Market
observation · Geopolitical event · Security event · Document**. Each defines field names, types,
required/optional fields, primary keys, entity references, units, temporal semantics, allowed values,
constraints, and a **schema version**. Canonical schemas are domain-specific — never one giant
universal schema.

### Connector package convention

Each connector ships source-specific modules only, with generic behavior living in the shared
subsystems:

```text
source/
├── __init__.py
├── connector.py     # source integration: endpoints, params, acquisition orchestration
├── parser.py        # raw response → structured records
├── normalizer.py    # source → canonical mapping
└── mappings.py      # endpoint tables, field/identifier/unit mappings
```

A connector should (1) acquire, (2) preserve raw data, (3) parse, (4) map fields to Hermes concepts,
(5) normalize values, (6) declare the canonical schema, (7) validate output, (8) provide metadata and
provenance. A connector must NOT implement generic retry/caching/validation, business logic, or feature
engineering.

### Architectural boundaries

```text
Connector      knows source API/format/concepts            · no generic retry/cache/storage
Acquisition    knows how to reliably retrieve data         · does not know what GDP/revenue means
Parser         knows how to interpret the source format    · does not define canonical meaning
Normalizer     knows how to make data consistent           · generic rules global, source mapping in connector
Schema         defines what canonical data looks like
Validation     determines whether data satisfies requirements
Metadata       describes what the dataset contains
Provenance     describes where the dataset came from
Lineage        describes what happened to the dataset
Storage        where the dataset is persisted
Query          how stored datasets are accessed
Export         how data transfers to external tools
```

**Dependency rule:** Core must not depend on any domain package; domain packages may depend on Core.
Generic behavior → Hermes subsystem; source-specific behavior → connector; canonical meaning → schema;
derived analytical behavior → features.

### Data flow

```text
External Source
      ↓
Connector
      ↓
Acquisition → Raw response → Parser → Structured records → Source mapping → Normalization
      ↓
Canonical Hermes Schema → Validation → Metadata → Provenance → Lineage
      ↓
Hermes Dataset
      ↓
┌──────────┬──────────┬──────────┐
Storage    Query      Export     Features (de-scoped)
```

---

## Part D — Subsystem Engineering Spec

**How to read this:** every unchecked box is an engineering task. Assignments follow the team/ownership
map in [Part E](#part-e--engineering-team). DoD = Definition of Done.

### D0. Project direction

**Objective:** evolve Hermes into a reusable data platform that can *acquire, preserve raw data, parse,
normalize to canonical schemas, validate, profile, attach metadata, track provenance + lineage, resolve
entities, register/version datasets & schemas, store/query, export, and synchronize incremental
updates* — and serve finance/defense datasets through an entity-centric provider API.

Core principle:

```text
External Source → Connector → Raw Data → Parse → Normalize → Validate
→ Metadata + Provenance + Lineage → Hermes Dataset → Storage / Query / Export
```

### D1. Core Dataset System

- [x] Create `Dataset` abstraction
- [x] Define dataset identity
- [x] Define dataset name
- [x] Define dataset ID
- [ ] Define dataset schema reference
- [x] Define dataset version
- [ ] Define dataset metadata reference
- [ ] Define provenance reference
- [ ] Define lineage reference
- [ ] Create standardized operation/result objects
- [ ] Create standardized error handling
- [ ] Ensure datasets are independent of specific storage engines

Dataset requirements: contains schema info, metadata, provenance, lineage, version; supports
lazy/eager execution where appropriate; integrates with Arrow, Polars, Pandas, DuckDB; operations
`parse normalize validate profile inspect transform resolve query save export metadata schema lineage`
return consistent `Dataset`/result types.

### D2. Acquisition Engine

- [ ] Define `Source`: configuration, credentials, capabilities, metadata, lifecycle
- [ ] Implement `fetch()`, `ingest()`, `source()`, `connect()`, `read()`, `stream()`
- [ ] API sources, file sources, local sources supported
- [ ] Streaming sources have a defined interface
- [ ] Failures produce structured errors
- [ ] Source information is recorded in provenance
- [ ] Common HTTP client with headers/timeouts/response handling
- [ ] Cache: keys, expiration, invalidation (move current cache implementation)
- [ ] Retry: timeouts, temporary server errors, connection failures, rate-limit responses
- [ ] Pagination: pages/offsets/cursors/next-URL/date-range/tokens
- [ ] Rate limiting: tracking, waiting, response handling
- [ ] Synchronization: sync state, last-successful-sync, cursors, timestamps
- [ ] Resumable acquisition; request timeout handling
- [ ] Implement `fetch_raw()`, `sync()`; preserve existing `_fetch()` acquisition abstraction

### D3. Parsing Engine

- [ ] Define `Parser` contract: input contract, output contract, registration, selection
- [ ] Implement `parse()`, `detect_format()`, `read_raw()`, `decode()`
- [ ] Formats: CSV, JSON, JSONL, XML, Parquet, Arrow, compressed files
- [ ] Nested JSON and lists-of-records support
- [ ] Intermediate record representation (`records.py`)
- [ ] Preserve source fields and raw values
- [ ] Handle malformed records; define parser errors and warnings
- [ ] Allow connector-specific parsers; keep source-specific logic inside connectors
- [ ] Prevent generic parser from containing SEC/GDELT business logic
- [ ] Parser does not perform semantic normalization, entity resolution, or contain domain mappings

### D4. Schema / Data Contract Engine

- [ ] Define schema model: fields, types, nullable, required, constraints
- [ ] Schema versioning and serialization
- [ ] Implement `schema()`, `register_schema()`, `infer_schema()`, `validate_schema()`,
      `compare_schema()`, `migrate_schema()`, `metadata()`, `set_metadata()`
- [ ] Schema registry, compatibility checking, evolution, version tracking, migration
- [ ] Initial canonical schemas registered: entity, economic, financial, market, geopolitical,
      security, document

### D5. Normalization Engine

- [ ] Define normalization interface; source→canonical mapping
- [ ] Type, unit, temporal, geographic, identifier normalization
- [ ] Implement `normalize()`, `map()`, `cast()`, `standardize()`, `convert_units()`, `align_time()`,
      `clean()`
- [ ] ISO date/time conventions; consistent timezone handling
- [ ] Standard country codes; consistent numeric types; unit conversion framework
- [ ] Currency normalization; missing-value conventions; duplicate handling
- [ ] Source-specific mappings remain outside generic Core
- [ ] Normalization is deterministic; steps recorded in lineage
- [ ] Normalization rules reusable (`rules.py`: date, numeric, string cleanup, null, unit, identifier)

### D6. Quality Engine

- [ ] Define quality-check and validation-rule interfaces
- [ ] Define quality report, score/model, severity levels, warning vs error behavior
- [ ] Implement `validate()`, `check()`, `check_quality()`, `check_completeness()`,
      `check_freshness()`, `check_integrity()`
- [ ] Checks: null, type, range, required-field, constraint, schema, primary-key, foreign-key,
      referential-integrity, unit, date, duplicates
- [ ] Create `ValidationReport`; separate errors from warnings
- [ ] Profiling: row count, column count, types, null %, unique, duplicates, min/max, basic stats,
      distributions, temporal coverage, frequency detection, gap detection
- [ ] Implement `profile()`
- [ ] Deduplication: exact, configurable keys, resolution strategy, preserve duplicates when required
- [ ] Anomaly detection: extensible interface, not coupled to ML implementations
- [ ] Quality results recorded in metadata/provenance; machine- and human-readable reports

### D7. Metadata System

- [ ] Dataset-level and column-level metadata models
- [ ] Type, row/column counts, null stats, unique stats, date range, frequency detection,
      entity coverage, source information, retrieval timestamp, last-observation timestamp,
      expected update frequency, quality information
- [ ] Implement `get_metadata()`, `inspect()`, `profile()`
- [ ] Metadata does not modify the dataset

### D8. Provenance

- [ ] Define provenance model
- [ ] Record source, URL/API endpoint, retrieval timestamp, connector, connector version,
      raw-data checksum, parser version, normalizer version, schema version, validation result,
      transformation information
- [ ] Implement `get_provenance()`
- [ ] Provenance immutable once recorded where appropriate

### D9. Lineage

- [ ] Define lineage model
- [ ] Track input/output dataset, operations, transformations, timestamps, versions, parameters
- [ ] Build dataset lineage graph; implement `get_lineage()`; make lineage queryable
- [ ] Start with ordered lineage records; design so a DAG can be added later; do not build a DAG initially

### D10. Entity System *(first-class pillar)*

- [ ] Define `Entity` and `EntityMatch` models; canonical entity representation
- [ ] Define `Resolver` interface: `resolve()`, `identify()`, `match()`, `link()`, `entity()`
- [ ] Registry: `register()`, `get()`, `resolve()`, `list_types()`
- [ ] Aliases: `add_alias()`, `resolve_alias()`, `list_aliases()`
- [ ] Countries: canonical IDs, ISO-2/ISO-3/name/numeric-code resolution, aliases,
      historical/source-specific identifiers, `resolve_country()`
- [ ] Companies: canonical IDs, name, ticker, CIK, LEI, ISIN, source-specific IDs, aliases,
      `resolve_company()`
- [ ] Persons: canonical IDs, name/identifier resolution, aliases (defense/persons scope)
- [ ] Implement `resolve_entity()`
- [ ] Connect entities to canonical schemas
- [ ] **Entity registry populated to ~100k entities: companies, countries, and persons for finance & defense**
- [ ] **Entity-centric provider API:** `hr.resolve_company("AAPL")` → `.financials`, `.market_data`,
      `.fillings`, extensible per-domain datasets

Core provides the resolver interface; domain-specific entity knowledge stays outside Core.
Corporate/financial/defense/healthcare identifiers can be added independently.

### D11. Dataset Catalog

- [ ] Define dataset registry and identifier
- [ ] Fields: description, owner/source, schema, versions, coverage, frequency, quality, freshness,
      provenance
- [ ] Implement `datasets.list()`, `datasets.get()`, `datasets.search()`
- [ ] Register each bundled static dataset with schema, metadata, validation, provenance, version

### D12. Storage

- [ ] Define storage abstraction; pluggable backends
- [ ] Filesystem backend; Parquet backend (partitioning, compression, manifests); DuckDB integration
- [ ] Dataset layout: partition strategy, compression, manifests
- [ ] Persist metadata, schema, version, provenance with data
- [ ] Implement `save()`, `load()`, `delete()`, existence checks
- [ ] Atomic writes; corruption protection; storage tests

### D13. Query Engine

- [ ] Define query interface and execution model; query result abstraction
- [ ] Implement `query()` and `sql()`
- [ ] Filtering, projections, joins, aggregations, ordering, limits, entity/date/range filtering
- [ ] DuckDB execution; Polars/Arrow/Pandas integration
- [ ] Query separated from storage; query tests

### D14. Materialization

- [ ] Define materialization abstraction
- [ ] Materialize to Polars, Pandas, Arrow, DuckDB relation
- [ ] Implement `materialize()`; never mutate canonical data

### D15. Export

- [ ] Define exporter interface and configuration; export metadata
- [ ] Implement `export()`, `to_arrow()`, `to_polars()`, `to_pandas()`, `to_duckdb()`
- [ ] Formats: Parquet, CSV, JSON, JSONL, Arrow
- [ ] Preserve metadata/schema/provenance where supported

### D16. Dataset Versioning

- [ ] Version model: dataset, schema, pipeline, version identifiers, version metadata
- [ ] Implement `version()`, `snapshot()`, `diff()`
- [ ] Content hashing, schema hashing, transformation versions, deterministic version IDs
- [ ] Immutable snapshots with snapshot metadata/provenance/lineage
- [ ] Detect added/removed/changed rows and schema changes
- [ ] Versioning tests

### D17. Schema Migration

- [ ] Migration model, registry, direction, compatibility rules
- [ ] Detect breaking schema changes; forward migrations
- [ ] Implement `migrate()`; record migration provenance; test reproducibility

### D18. Registry System

- [ ] Component, dataset, schema, connector, parser, validator, transformer, resolver, storage
      registries
- [ ] Implement `register()`, component lookup/discovery/versioning/metadata

### D19. Execution Engine

- [ ] Execution context, pipeline abstraction, state, results, error handling, retry behavior
- [ ] Deterministic stage order; pass `Dataset` between stages
- [ ] Capture lineage, execution metadata, errors automatically
- [ ] Reusable and configurable pipelines

### D20. Inspection / Developer Experience

- [ ] Implement `inspect()`: dimensions, schema, metadata, sample records, quality, lineage,
      provenance, version
- [ ] CLI: dataset inspection, schema inspection, profile, validation, lineage, dataset catalog
- [ ] TUI where practical

### D21. Error System

- [ ] Hermes exception hierarchy
- [ ] Acquisition, parsing, schema, normalization, validation, transformation, resolution, storage,
      query, configuration errors
- [ ] Useful error context; preserve original source errors where appropriate

### D22. Extension Architecture

- [ ] Connector interface/config/metadata/lifecycle
- [ ] Plugin interfaces: connector, parser, schema, mapper, normalizer, validator, profiler,
      transformer, resolver, storage backend, exporter
- [ ] Connectors depend on Core, never the reverse

### D23. Python Ecosystem Integration

- [ ] Arrow-native internal interoperability; Arrow/pandas/polars conversions and schema mapping
- [ ] Dataset ↔ Polars, Pandas, DuckDB (SQL execution, parquet querying), NumPy where appropriate

### D24. Public API

```python
hr.fetch()            hr.ingest()           hr.read()             hr.sync()
hr.parse()            hr.normalize()        hr.transform()        hr.validate()
hr.profile()          hr.inspect()          hr.get_metadata()     hr.check_quality()
hr.check_completeness() hr.check_freshness() hr.check_integrity()
hr.resolve_entity()   hr.resolve_country()  hr.resolve_company()
hr.datasets.list()    hr.datasets.get()     hr.datasets.search()
hr.save()             hr.load()             hr.query()            hr.materialize()
hr.get_provenance()   hr.get_lineage()      hr.version()          hr.snapshot()      hr.diff()
hr.get_schema()       hr.register_schema()  hr.compare_schema()   hr.migrate()
```

- [ ] Keep the public API thin; route to internal engines; no business logic in wrappers
- [ ] Consistent return types and error behavior
- [ ] Document the public API; add public API tests

`Dataset` methods mirror the `hr.*` ops: `parse normalize validate profile inspect transform resolve
query save export schema metadata lineage`.

### D25. Testing

- [ ] Unit: acquisition, parsing, schema, normalization, validation, profiling, transformation,
      resolution, storage, query, export, versioning, provenance, lineage, registry
- [ ] Integration: API→Parser→Dataset, File→Parser→Dataset, Dataset→Normalize→Validate,
      Dataset→Profile→Quality, Dataset→Store→Load, Dataset→Query→Export, Dataset→Snapshot→Diff,
      full connector pipeline
- [ ] Contract tests: connector, parser, validator, transformer, resolver, storage interfaces
- [ ] Test suite organized as `unit / connectors / features / integration`
- [ ] Regression and failure/recovery tests; schema compatibility tests

### D26. Production Hardening

- [ ] Structured logging; standardized error taxonomy
- [ ] Retry policies, rate-limit handling, request timeouts
- [ ] Memory limits; streaming ingestion; large-file handling
- [ ] Checkpointing; resumable ingestion
- [ ] Atomic dataset writes; corruption detection
- [ ] Deterministic pipelines; reproducibility checks
- [ ] Performance and memory benchmarks; connector reliability tests

### D27. Static Data

- [ ] Move bundled datasets into `data/datasets/`
- [ ] Register each: metadata, schema, validation, provenance, version; catalog access

### D28. v1 Acceptance Criteria

**Acquisition:** reliable connector framework, raw acquisition, cache, retry, pagination, rate limiting,
incremental sync.

**Understanding:** metadata extraction, inspection, profiling.

**Transformation:** parsing, canonical normalization, explicit transformations.

**Trust:** schema validation, quality validation, completeness, freshness, integrity.

**Identity:** country resolution, company resolution, person resolution, general entity resolution,
canonical entity registry (~100k entities).

**Data management:** catalog, registry, storage, querying, materialization, export.

**Reproducibility:** metadata, provenance, lineage, dataset versioning, snapshots, diff, schema
versioning, migration.

**Developer experience:** stable `hr.*` API, connector contract, documented canonical schemas, reference
connector, complete test suite, architecture documentation, connector development documentation.

**Core success tests (both must be CI-green):**

```text
CSV / JSON / API / XML
        ↓
      Hermes
        ↓
Parse → Normalize → Validate
        ↓
Metadata + Provenance + Lineage
        ↓
Canonical Dataset
        ↓
Store → Query → Version → Export
```

```python
import hermes as hr
apple = hr.resolve_company("AAPL")
apple.financials      # CI-verified provider demo
apple.market_data
apple.fillings
```

**The first real milestone is ONE complete vertical slice** (a single source: raw → parse → normalize →
canonical schema → validate → metadata → provenance → stored Dataset), then the rest of Hermes becomes
repeating and generalizing the architecture rather than inventing it per source.

> **Decision on appetite:** "implement everything" is not the milestone. The engine milestone is the
> vertical slice above; the provider milestone is the `resolve_company` demo above.

---

## Part E — Engineering & Team

### Team roles

| Person | Role | Owns |
|---|---|---|
| **Haider** | Founder — architect & core engineer | `core/`, `api/` (design), `schemas/`, `datasets/`, `storage/`+`query/` (design), canonical schemas, connector contract, entity architecture, final review, integration |
| **Abdulrehman** | Core engineer | `connectors/` (rebase), `parsing/`, `export/`, `storage/`+`query/` (implement), source mappings |
| **Abdullah** | Security & core engineer | `acquisition/`, security hardening, storage/query integrity; security review gate on every subsystem |
| **Tasbiha** | Frontend & core engineer | `docs-site/`, public docs, API reference, `inspect()`/CLI display, export helpers |
| **Faik** | Frontend & core engineer | CLI, examples, parser/unit tests, docs-site; grows into core alongside |
| **Ifra** | Core engineer — data quality | `normalization/`, `validation/`, `metadata/`, `entities/` (implementation); schema inference + migration |

### Repository ownership

```text
hermes/
├── api/             → Haider + Abdulrehman
├── acquisition/     → Abdullah
├── connectors/      → Abdulrehman (security review: Abdullah)
├── core/            → Haider
├── schemas/         → Haider (Ifra: inference/migration)
├── parsing/         → Abdulrehman (Faik co-implements CSV/JSON)
├── normalization/   → Ifra
├── validation/      → Ifra
├── metadata/        → Ifra
├── entities/        → Ifra (Haider: design/review)
├── datasets/        → Haider (Tasbiha/Faik: catalog UI + docs)
├── storage/         → Haider + Abdulrehman (Abdullah: integrity)
├── query/           → Haider + Abdulrehman
├── export/          → Abdulrehman + Tasbiha
├── cli/             → Faik (Haider: design)
└── features/        → Shared (de-scoped; keep out of v1-core)
```

Ownership means one person is responsible for understanding, maintaining, testing, and improving a
subsystem — not that others cannot touch it.

### Task rules

Every engineering task must have: **Task ID · Title · Owner · Goal · Background · Input · Expected
output · Files/subsystem · Requirements · Edge cases · Tests · Definition of done.**

Assign `META-001 Implement column metadata extraction` — never "Build metadata."

### Difficulty levels

- **Beginner:** small functions, tests, documentation, simple metadata/validation, small utilities
- **Easy:** small modules, simple connector components, basic parsing, basic mappings
- **Medium:** complete connectors, complex validation, storage, query
- **Hard:** SEC/GDELT normalization, logical entity resolution, schema migrations, lineage, versioning,
  performance
- **Architecture:** only after the engineer understands the subsystem

### Git workflow

Never work directly on `main`. `Issue → Branch → Implementation → Tests → Pull Request → Review →
Merge`. Branch examples: `feature/meta-column-profile`, `feature/worldbank-normalizer`,
`fix/validation-null-check`, `test/sec-normalizer`, `docs/connector-guide`.

### Pull requests

Every PR: *what changed, why, files affected, tests added, tests run, known limitations.* Before
opening: code works, tests added, existing tests pass, no unrelated changes, type hints where
appropriate, docs updated if API changed, no secrets committed.

### Review rules

Author owns correctness. Reviewer checks: correctness, tests, architecture, maintainability, naming,
error handling, API compatibility, performance. The lead reviews: architecture changes, public API
changes, canonical schemas, cross-subsystem changes, entity resolution, storage architecture, major
normalization decisions.

### Coding rules

Prefer: small functions, clear names, type hints, explicit behavior, tests, documentation,
deterministic transformations. Avoid: huge functions, hidden global state, magic behavior, duplicated
infrastructure, source-specific logic in core, untested transformations, unnecessary abstractions.

### The #1 architectural rule

Do not solve the same infrastructure problem separately inside every connector.

```text
Bad:   World Bank → own retry · FRED → own retry · IMF → own retry · SEC → own retry
Good:  Hermes Acquisition {retry, cache, pagination, rate-limit} ← World Bank/FRED/IMF/SEC/...
```

The connector provides source-specific behavior; Hermes provides reusable infrastructure.

### Learning while building

`Python → Git → pytest → Polars → Metadata → Profiling → Validation → Simple parser → Simple connector
→ Normalization → Complete connector`. Every step produces a real PR.

### Communication rules

When blocked, state: *what I am trying to do / what I expected / what actually happened / what I tried /
relevant error / relevant files.*

### Definition of Done (component)

Design understood · implementation exists · interface defined · tests exist · edge cases handled ·
errors handled · documentation exists · metadata/provenance implications considered · code reviewed ·
CI passes.

---

## Part F — Roadmap & Strategy

### v1 scope

v1 = the checkboxes in [Part D](#part-d--subsystem-engineering-spec). Strategy: **core-first** —
build the general data engine so anyone can process their own data (CSV/JSON/XML/Parquet) and so the
finance/defense datasets and data-provider can be built on real infrastructure.

### Quick wins (~half a day)

1. **Truth pass** — README shows "Implemented / Planned"; remove/convert broken root `main.py`
   (`benchmarks/profile_run.py`).  *README largely done.*
2. **License — DONE (2026-09): Elastic License 2.0** (source-available) in `LICENSE.md` +
   `pyproject.toml`; README/docs-site repositioned; commercial path = Hermes Enterprise.
3. **CI gates PRs** — `tests.yml` on `pull_request`, caching, rising coverage threshold; rename
   workflows (`tests` = CI, `publish` = release).
4. **Split-stub demo locked** — local-file core loop as a CI-smoke-tested vertical slice (Phases 1–4
   compressed).

### Phases

**Phase 1 — Core Foundation** *[Blocking] · Haider* (Checklist D1/D7/D21)
`Dataset` lifecycle with conversions, metadata/provenance/lineage/version models, error system,
component ABCs (Parser, Normalizer, Validator, Resolver, StorageBackend).

**Phase 2 — Data In** *[Abdullah day one] · Abdullah + Abdulrehman + Faik* (D2/D3)
Real acquisition (Client/RetryPolicy/RateLimiter/Paginator/SyncState + RawCache), parsing engine
(detect_format + csv/json/parquet/xml parsers → `pl.DataFrame`). Done: `hr.read("file.csv")` returns a
`Dataset`.

**Phase 3 — Data Contract** *[Blocking after Phase 2] · Haider + Ifra* (D4/D5)
Schema registry + 7 canonical schemas + `infer_schema`, normalization engine + reusable rules.
Done: `hr.normalize(df, schema="economic.v1")` → canonical `Dataset`.

**Phase 4 — Data Quality** *· Ifra* (D6/D7)
Validation contracts/checks/reports; profiling + metadata extraction wired into `Dataset.profile()`.

**Phase 5 — Identity & Entity Resolution** *· Ifra, Haider design* (D10)
`Resolver` interface + registry + aliases; countries (ISO2/3/name/numeric) and companies
(ticker/CIK/ISIN) resolvers; `hr.resolve_country("PK")`, `hr.resolve_company("AAPL")` real.

**Phase 6 — Storage / Query / Export / Materialization** *· Haider + Abdulrehman, integrity Abdullah*
(D11/D12/D13/D14/D15)
Filesystem+parquet storage with atomic writes + sidecars; DuckDB backend; exporters; query engine;
dataset catalog.

**Phase 7 — Dataset Lifecycle** *· Haider* (D8/D9/D16/D17/D27)
Automatic provenance + lineage capture; versioning/snapshots/diff; schema migration; bundled static
datasets registered.

**Phase 8 — Public API, CLI, DX** *· Haider + Faik + Tasbiha* (D20/D24)
Thin `hr.*` wrappers with consistent types; CLI commands (`inspect`, `profile`, `validate`, `schema`,
`datasets list`, `lineage`, `sync`); pretty inspect; examples; notebook snippets.

**Phase 9 — Connectors on the Engine** *· Abdulrehman lead, Haider arch, Abdullah security* (D9/S)
`BaseConnector` + registry; World Bank as the reference vertical slice on the `economic` schema; rollout
FRED → IMF → YFinance → Finnhub → Binance → SEC → GDELT → OpenSanctions; STRIDE review per connector.

**Phase 10 — Data Provider (Entity-first serving layer)** *· Ifra + Haider* (D10)
Entity registry scaled to ~100k companies/countries/persons (finance & defense); `resolve_entity` →
entity object; `.financials / .market_data / .fillings` backed by canonical datasets, provenance-bound;
provider CI demo green.

**Phase 11 — Hardening, Testing, Docs** *· All hands* (D25/D26/D28)
Structured logging, error taxonomy wired everywhere, streaming/resumable sync, benchmarks; test-suite
split + integration e2e + CI coverage gate; security redaction/tamper tests; per-subsystem docs;
v1 acceptance (both core-success tests).

### Sequencing rules

- Phases 1–4 are the critical path; 1 and 3 are strictly blocking.
- Abdullah (security/acquisition) and Tasbiha (docs-site) run from day one in parallel.
- Ifra owns the quality stack (normalization → validation → metadata → entities) once schemas land
  (Phase 3+).
- Every task: an ID, one owner, a DoD, a PR.

### Definitions of done — v1 acceptance (summary)

See **D28**. The two non-negotiable green demos: (1) the core lifecycle on a local file with
provenance/lineage; (2) `resolve_company("AAPL").financials` returning a provenance-bound Dataset.

### Status legend

| Area | Checklist | Status |
|---|---|---|
| Core Dataset | D1 | ~35% (Dataset + load/inspect/profile/conversions real; save/export + tests pending) |
| Acquisition | D2 | ~20% (cache done; client/retry/rate/pagination/sync pending) |
| Parsing | D3 | ~15% (module skeleton + parsers exist; engine dispatch pending) |
| Schemas / Contracts | D4 | ~10% (field/schema models; registry + engines pending) |
| Normalization | D5 | ~10% |
| Quality | D6 | ~10% (profile real in `api/data.py`; validation pending) |
| Metadata | D7 | ~15% (InspectReport/MetaData real; extractor pending) |
| Provenance / Lineage | D8/D9 | ~10% (models exist; capture pending) |
| Entities | D10 | ~15% (countries/companies helpers real; registry/resolver/aliases pending) |
| Dataset Catalog | D11 | ~10% |
| Storage / Query / Export | D12–15 | ~10% (export/utils real; storage/query pending) |
| Versioning / Migration | D16/D17 | ~10% (models exist) |
| Public API + CLI | D20/D24 | ~5% (facade wired, bodies pending; CLI profile_data works) |
| Connectors on engine | Phase 9 | ~30% (connectors work standalone; contract pending) |
| Provider layer | Phase 10 | ~5% (entities skeleton) |
| Hardening / Testing / Docs | D25/D26/D28 | ~20% (tests pass; platform + docs pending) |

---

## Part G — Positioning, Licensing & Credibility

### License — Elastic License 2.0 (decided)

Hermes is **source-available**, not OSI "open source", under **Elastic License 2.0 (ELv2)** — the same
family used by Elastic/Couchbase. Reasons:

- **Credibility:** a lawyer-drafted license instead of a hand-written one; terms are precise and
  defensible.
- **Honesty:** no false "open source" claims anywhere.
- **Protecting the cloud business:** ELv2 forbids offering the software to third parties as a hosted /
  managed service — only Hermes (via a commercial license) may host a "cloud Hermes".
- **Adoption-friendly:** individual/research/internal-commercial use, modification, and redistribution
  are free and unconditional (no employee/revenue counting).

**Monetization:** **Hermes Enterprise** — commercial license for support, SLAs, enterprise features,
and managed-hosting rights. Big organizations adopt the free engine; revenue comes from the Enterprise
edition and the cloud, not from the core license.

### Where Hermes competes

The vertical slice nobody owns: **trustworthy canonical datasets, with provenance, for finance &
defense, served through an entity-centric API** — resolve a company/country/person → on-demand canonical
datasets, gated by a ~100k-entity registry.

Integrate (never wrap): Polars, pandas, DuckDB, Arrow, PyArrow. Complement: dlt/Airbyte/Singer (use
their output). Integrate adapters later: Great Expectations, pandera, Splink/Dedupe (behind `Resolver`),
OpenLineage (export lineage to them), DVC/lakeFS (storage-level versioning).

Deliberately NOT building: BI dashboards, an ML framework, a generic ETL/DAG/orchestration system, HTML
report generation, a general tap ecosystem, a columnar database.

### The moat

| Candidate | Moat? | Why |
|---|---|---|
| Entity registry (finance/defense: companies/countries/persons) | **Strong** | a maintained, deduplicated ~100k-entity registry + aliases is a data asset competitors won't rebuild |
| Entity-centric data provider | **Strong once live** | the product's face; harder to switch, stronger lock-in |
| Canonical schemas (7 domains) | Strong, if maintained | few operate public versioned canonical schemas for finance/defense |
| Provenance + traceable normalization | Strong | auditable end-to-end normalization is what finance/defense buyers need |
| Connector breadth | Not a moat | dlt/airbyte out-source us 100:1 |
| Dataset-as-only-currency | Becoming moat | once Dataset is the only currency, datasets/resolvers/exports compose on it |

### Credibility strategy

The largest credibility risk was the gap between claims and code. That gap is being closed by: truthful
README, ELv2 license, CI on PRs, and the two CI-green success demos (engine vertical slice +
`resolve_company` provider demo). Reputation is measured by *external PRs merged, installs-to-works
time, reproduction hashes, time-to-first-useful-dataset* — not stars.

### Top 10 highest-leverage improvements

1. README/document truth pass + license repositioning **(in progress / mostly done)**
2. Local-file lifecycle real (parse→normalize→validate→Dataset→save→query→export)
3. CI-verified Dataset-first pipeline demo
4. Connector contract (`BaseConnector` + registry + shared acquisition)
5. Provenance/lineage recorded + persisted
6. Schema registry + validation over the 7 canonical schemas
7. CI gates PRs + coverage threshold
8. Live quickstart + honest roadmap on docs-site
9. Provider demo green (`resolve_company("AAPL").financials`)
10. ~100k-entity registry seeded (companies/countries/persons)

### NOW / NEXT / LATER / DON'T BUILD

**NOW (this month):** local-file lifecycle end-to-end + CI smoke test; provenance/lineage recorded at
ingest; CI gates PRs; connector retry/cache centralized in acquisition; README truth pass complete.

**NEXT (months 2–3):** BaseConnector + registry (World Bank reference wedge); schema registry + 7
canonical schemas + validation + contracts; storage backends + `Dataset.save/load/query`; entity
resolution real (Ifra); provider demo; feature layer removed or consolidated; changelog + semver.

**LATER (6–12 months):** DuckDB query engine; versioning/diff/snapshot; schema migration; `resolve`
provider layer live with ~100k entities (companies/countries/persons) and finance/defense datasets;
contributor surfaces; 2–3 case studies with reproducible hashes; OpenLineage/GX/pandera/Splink adapters.

**DON'T BUILD:** Hermes Cloud (waits for a real product); Healthcare/Trade/Energy/Climate domains until
finance/defense are proven; a tap-for-everything connector ecosystem (integrate dlt/Airbyte); BI /
dashboards / ML framework / orchestration / HTML report generators; a second (DAG) lineage architecture;
a giant universal schema; standalone feature engines on top of the current scope.

### First 5 actions (roadmap-linked)

1. **License — DONE (2026-09): ELv2** in `LICENSE.md`/`pyproject.toml`/README/docs-site; Enterprise =
   commercial path.
2. **Truth-fix README + root artifact** — README rewritten to "Implemented / Planned" (done); convert
   root `main.py` to a benchmark script (pending).
3. **Land the local-file core loop** as a CI-smoke-tested vertical slice (Phases 1–4).
4. **Wire provenance + lineage as recorded facts at ingest**, persisted with the Dataset,
   exposed via `provenance_info/lineage_info`.
5. **Make CI gate PRs** — `tests.yml` on `pull_request`, coverage threshold, honest workflow names,
   docs-site version synced to the package version.

---

*Everything else depends on the engine lifecycle and the entity-centric provider demo being real first.*