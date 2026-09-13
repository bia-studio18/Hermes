import type { Metadata } from "next";
import {
  DocTitle,
  Lead,
  H2,
  P,
  List,
  Callout,
  PrevNext,
  Table,
} from "@/components/Doc";
import { CodeBlock } from "@/components/CodeBlock";
import { Plant, Sparkle } from "@/components/Doodle";

export const metadata: Metadata = {
  title: "Roadmap",
  description:
    "Hermes roadmap and architecture phases: connectors & features today; the core lifecycle subsystems built out over time.",
};

export default function RoadmapPage() {
  return (
    <article className="relative">
      <div className="pointer-events-none absolute -right-8 top-24 hidden opacity-40 sm:block">
        <Plant className="h-28 w-24" color="#ff4328" />
      </div>
      <DocTitle kicker="Project">Roadmap</DocTitle>
      <Lead>
        Hermes ships a working foundation and builds the general-purpose core out progressively.
        The single architecture &amp; roadmap document is <code>docs/hermes.md</code>.
      </Lead>

      <H2 id="summary">The journey at a glance</H2>
      <Table
        head={["Phase", "Focus", "ETA-ish"]}
        rows={[
          ["Phase 1 — Core foundation", "parse, normalize, validate, Dataset, metadata/provenance/lineage", "Now → next"],
          ["Phase 2 — Data in", "acquisition, parsers; hr.read(file) → Dataset", "In progress"],
          ["Phase 3 — Data contract & quality", "schema registry + 7 canonical schemas, normalization, validation", "Next"],
          ["Phase 4 — Identity & entities", "Resolver + registry + aliases; countries/companies/persons (~100k)", "Next"],
          ["Phase 5 — Storage/query/export", "parquet storage, DuckDB, exporters, dataset catalog", "Next"],
          ["Phase 6 — Lifecycle & connectors", "versioning/migration, connectors on the engine (World Bank first)", "Later"],
          ["Phase 7 — Data provider", "hr.resolve_company(\"AAPL\").financials — finance & defense datasets", "Later"],
        ]}
      />

      <H2 id="now">Today (v0.2.x)</H2>
      <Table
        head={["Area", "Status"]}
        rows={[
          ["Connectors (10)", "Working standalone; porting onto the engine contract"],
          ["Dataset + load/inspect/profile", "Working; save/export + tests pending"],
          ["Entities (countries, companies helpers)", "Working"],
          ["RawCache (parquet, TTLs, hit/miss)", "Working"],
          ["CLI (profile / inspect snippets)", "Partial"],
          [
            "Core lifecycle modules (parse/normalize/validate/schema/metadata/query/storage/api)",
            "Scaffolded — being built out",
          ],
          ["Data provider (entity-centric API)", "Specified — being built"],
          ["Provenance / lineage / versioning", "Models exist — capture pending"],
        ]}
      />

      <H2 id="core-spec">The core life-cycle specification</H2>
      <P>
        <code>hermes-core.md</code> describes the general-purpose data-lifecycle engine Hermes is
        building toward. Lifecycle subsystems:
      </P>
      <List
        items={[
          "Acquisition — fetch, ingest, source, connect, read, stream",
          "Parsing — parse, detect_format, read_raw, decode (CSV/JSON/JSONL/XML/Parquet/Arrow/compressed)",
          "Data Contract / Schema — schema, infer_schema, validate_schema, migrate_schema",
          "Normalization — normalize, map, cast, standardize, convert_units, align_time",
          "Quality — validate, check, profile, deduplicate, detect_anomalies (ML-extensible)",
          "Transformation — transform, pipe, select, filter, join, aggregate (Polars/Arrow/DuckDB)",
          "Identity / Resolution — resolve, identify, match, link, entity (extension point)",
          "Storage — save, load, delete (FS/Parquet/Arrow/DuckDB/PostgreSQL)",
          "Query — query, sql with filter/project/join/aggregate/order/limit",
          "Versioning — version, snapshot, diff (immutable snapshots)",
          "Provenance & Lineage — lineage, provenance, trace",
        ]}
      />
      <P>
        Cross-cutting design rules: a <strong>registry</strong> for every component, a defined{" "}
        <strong>error hierarchy</strong>, an <strong>extension architecture</strong>, and the{" "}
        <strong>dependency rule</strong> — Core never depends on a domain package. The public API
        target is <code>hr.fetch/ingest/parse/normalize/validate/profile/inspect/transform/query/
        save/load/export</code>.
      </P>

      <H2 id="phases">The phases</H2>
      <CodeBlock title="phases" code={`Phase 1 — Core foundation
  Dataset lifecycle, metadata/provenance/lineage/version models,
  error system, component contracts (Parser, Normalizer, Validator,
  Resolver, StorageBackend)

Phase 2 — Data in
  acquisition (retry, rate limiting, pagination, sync, cache),
  parser engine (CSV/JSON/XML/Parquet) — hr.read(file) → Dataset

Phase 3 — Data contract & quality
  schema registry + 7 canonical schemas, infer/validate schema,
  normalization engine, validation contracts, profiling/metadata

Phase 4 — Identity & entity resolution
  Resolver interface + registry + aliases; countries (ISO2/3),
  companies (ticker/CIK/ISIN), persons; hr.resolve_country("PK")

Phase 5 — Storage / query / export / materialization
  filesystem + parquet storage with atomic writes, DuckDB backend,
  exporters, query engine, dataset catalog

Phase 6 — Lifecycle & connectors
  provenance + lineage capture, versioning/snapshots/diff, schema
  migration, connectors on the engine (World Bank first, then
  FRED → IMF → YFinance → Finnhub → Binance → SEC → GDELT →
  OpenSanctions)

Phase 7 — Data provider (entity first)
  entity registry scaled to ~100k companies/countries/persons for
  finance & defense; hr.resolve_company("AAPL").financials/
  .market_data/.fillings backed by provenance-bound canonical
  datasets`} />
      <P>
        The guiding philosophy: make high-quality data infrastructure accessible through one
        consistent developer experience. One engine, one ecosystem, any data.
      </P>

      <Callout title="Get involved" tone="cedar">
        Hermes is source-available under Elastic License 2.0. The repository ships GitHub labels (type / area / difficulty) and
        a contributing guide (<code>docs/hermes.md</code>) that defines the
        vertical-slice build order (e.g. World Bank: acquire → parse → normalize → validate →
        metadata → provenance → Dataset).
      </Callout>
      <Sparkle className="mt-8 h-10 w-10 opacity-50" color="#ff4328" strokeWidth={4} />

      <PrevNext prev={{ title: "API Reference", href: "/docs/api-reference" }} />
    </article>
  );
}
