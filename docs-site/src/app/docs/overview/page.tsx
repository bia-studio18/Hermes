import type { Metadata } from "next";
import {
  DocTitle,
  Lead,
  H2,
  P,
  List,
  Callout,
  DocLink,
  PrevNext,
  Table,
} from "@/components/Doc";
import { CodeBlock } from "@/components/CodeBlock";
import { Plant } from "@/components/Doodle";

export const metadata: Metadata = {
  title: "Overview",
  description:
    "Hermes is a foundational intelligence data platform. Technical overview, architecture, pipeline and package layout.",
};

export default function OverviewPage() {
  return (
    <article className="relative">
      <div className="pointer-events-none absolute -right-8 top-24 hidden opacity-40 sm:block">
        <Plant className="h-28 w-24" color="#ff4328" />
      </div>
      <DocTitle kicker="Getting Started">Overview</DocTitle>
      <Lead>
        Hermes (<code>hermes-plt</code>, v0.2.16) is a foundational intelligence data platform for
        acquiring, validating, normalizing, storing and serving intelligence datasets. One
        consistent pipeline for APIs, CSVs, JSON, databases and public datasets.
      </Lead>

      <Callout title="Package" tone="cedar">
        <strong>hermes-plt</strong> · Python <code>&gt;=3.11</code> (3.11/3.12/3.13) · build backend{" "}
        <code>hatchling</code> · Development Status <code>3 - Alpha</code> · authored by Haider Ali ·
        under the Elastic License 2.0 (source-available; not open source).
      </Callout>

      <H2 id="why">Why Hermes</H2>
      <Lead>
        Every time a data team adds a new source, they rebuild the same plumbing: authentication,
        pagination, retries, schema mapping, unit conversion and validation. Hermes turns that
        repeated work into a single, reusable infrastructure layer. Here is what it tackles —{" "}
        <DocLink href="#pipeline">skip ahead to the pipeline</DocLink> if you want the data flow.
      </Lead>
      <Table
        head={["Problem", "How Hermes solves it"]}
        rows={[
          ["Different APIs & auth schemes", "Every connector behind one async fetch() contract"],
          ["Inconsistent formats", "A shared parse / normalize layer with one canonical schema"],
          ["Messy identifiers & units", "Entity helpers and canonical codes (ISO-3, ticker→CIK)"],
          ["Missing or duplicated records", "Validation rules + deduplicate()"],
          ["Repetitive fetch boilerplate", "RawCache with per-source TTLs and hit/miss stats"],
          ["Untracked data provenance", "Lineage and provenance recorded on every dataset"],
        ]}
      />
      <P>
        Modern data work repeats the same engineering for every new source: dealing with
        different APIs, authentication, formats, schemas, naming conventions, missing values,
        types, timestamps, units, identifiers, duplicates and validation rules. Hermes turns that
        repeated work into reusable infrastructure:
      </P>
      <CodeBlock
        title="python"
        code={`import hermes as hr

data = hr.fetch("world_bank", dataset="gdp")

data = data.parse()
data = data.normalize()
data = data.validate()

print(data.profile())

df = data.to_polars()`}
      />
      <P>
        Hermes does not replace pandas, polars, duckdb or arrow — it is a{" "}
        <strong>pipeline layer</strong> that makes them easier to use together.
      </P>

      <H2 id="pipeline">The data lifecycle</H2>
      <P>
        Every dataset travels through a single, repeatable pipeline. The same shape applies
        whether you&apos;re pulling GDP from the World Bank or filings from the SEC:
      </P>
      <CodeBlock
        title="pipeline"
        code={`External Source
    │  Connector (fetch / ingest)
    ▼
Raw Data
    │  parse / normalize / validate / profile
    ▼
Hermes Dataset
    │  transform / resolve / query / save / export
    ▼
Applications — ML, analytics, dashboards`}
      />
      <Table
        head={["Function", "Purpose"]}
        rows={[
          ["fetch()", "Retrieve data from an external source via a connector"],
          ["ingest()", "Bring an existing dataset (csv, json, parquet) into Hermes"],
          ["parse()", "Convert raw data into structured records"],
          ["normalize()", "Convert data into a consistent representation"],
          ["validate()", "Verify data satisfies defined rules"],
          ["profile() / inspect()", "Analyze structure, quality and metadata"],
          ["transform()", "Apply transformations to data"],
          ["resolve()", "Connect records to canonical entities"],
          ["deduplicate()", "Detect and handle duplicate records"],
          ["query(), save(), load(), export()", "Query, persist and ship datasets"],
          ["snapshot(), diff()", "Immutable versioning and comparison"],
          ["lineage(), provenance()", "Show how and where data was produced"],
        ]}
      />

      <H2 id="pillars">Design pillars</H2>
      <Lead>
        Five principles shape every API decision in Hermes. They keep the platform small,
        predictable and easy to reason about.
      </Lead>
      <Table
        head={["Principle", "What it means in practice"]}
        rows={[
          ["Composable", "Datasets from different sources work together in one pipeline"],
          ["Inspectable", "profile() / inspect() before you build on data"],
          ["Reproducible", "The same pipeline repeats predictably, cache-aware"],
          ["Traceable", "lineage() and provenance() on every dataset"],
          ["Interoperable", "pandas, polars, arrow, duckdb, numpy and parquet out of the box"],
        ]}
      />

      <H2 id="where-it-fits">Where Hermes fits</H2>
      <P>
        Hermes does <strong>not</strong> replace your DataFrame library or your database. It is the{" "}
        <strong>glue layer</strong> between live sources and your analysis stack:
      </P>
      <CodeBlock
        title="stack"
        code={`Live APIs & public datasets
        │  Hermes (acquire → validate → normalize)
        ▼
Canonical datasets (parquet-backed, cacheable)
        │  query / transform / export
        ▼
pandas · polars · arrow · duckdb · numpy
        │  features / ML / dashboards / apps
        ▼
Your applications`}
      />
      <P>
        Because everything upstream shares one shape, the tools you already know keep working —
        Hermes just makes the messy part reliable.
      </P>

      <H2 id="implemented">What is implemented today (v0.2.14)</H2>
      <P>
        Rather than a complete-from-day-one platform, Hermes ships a fully working foundation and
        builds the rest out over time. Today the working, tested core is:
      </P>
      <List
        items={[
          "The Hermes facade — wires up every connector, feature group and cache.",
          "10 source connectors (World Bank, IMF, FRED, GDELT, Binance, Finnhub, yfinance, SEC EDGAR, OpenSanctions, bundled public datasets).",
          "The feature engine — a tiered, dependency-aware registry with lineage tracking.",
          "Country-risk features (economic, environmental, geopolitical, security, social).",
          "Financial features (technical, fundamental, crypto history, company filings).",
          "RawCache — per-source parquet-backed caching with TTLs and hit/miss stats.",
          "A cron/interval asyncio scheduler.",
          "Entity helpers — 249 ISO-3 countries and ticker→CIK company mapping.",
        ]}
      />
      <Callout title="Planned subsystems" tone="gold">
        The core lifecycle modules (<code>parsing</code>, <code>normalization</code>,{" "}
        <code>validation</code>, <code>schemas</code>, <code>metadata</code>,{" "}
        <code>query</code>, <code>storage</code>, <code>api</code>) exist as scaffolded packages
        and are built out progressively. The long-form public API (composable{" "}
        <code>hr.fetch().parse().normalize()</code>) is the target architecture; see the{" "}
        <DocLink href="/docs/roadmap">roadmap</DocLink>.
      </Callout>

      <H2 id="ecosystem">The Hermes ecosystem</H2>
      <P>
        Hermes Core stays small and general. Specialized capability ships as separate packages
        (Finance, Defense, Healthcare, Trade, Energy, Climate, Geopolitics, Corporate, Entity,
        Features, Connectors) so a finance developer never installs defense infrastructure:
      </P>
      <CodeBlock
        title="ecosystem"
        code={`Hermes Core
  ├── Hermes Finance
  ├── Hermes Defense
  ├── Hermes Healthcare
  ├── Hermes Trade
  ├── Hermes Energy
  ├── Hermes Climate
  ├── Hermes Geopolitics
  ├── Hermes Corporate
  ├── Hermes Entity
  ├── Hermes Features
  └── Hermes Connectors`}
      />
      <P>
        The dependency rule is strict: <strong>Core must not depend on any domain package</strong>.
        Domain knowledge (resolvers, canonical schemas, features) is layered on top.
      </P>

      <H2 id="package-layout">Package layout</H2>
      <CodeBlock
        title="tree"
        code={`hermes/
├── __init__.py            # Hermes facade
├── constants.py           # SYMBOLS, TICKERS, CANONICAL_FREQS, interval maps
├── acquisition/           # RawCache, Client
├── connectors/            # binance, finnhub, fred, gdelt, imf,
│                          #   opensanctions, public_data, sec, world_bank, yfinance
├── core/                  # Dataset, scheduler, lineage/provenance/metadata stubs
├── entities/              # countries, companies
├── features/
│   ├── country_risk_features/   # economic, environmental, geopolitical, security, social
│   └── financial/               # technical, fundamental (crpto), filling, stocks
├── api|datasets|metadata|normalization|parsing|query|
│   schemas|storage|validation   # (scaffolded, being built out)
└── export/                # export helpers`}
      />

      <H2 id="works-with">Works with your data stack</H2>
      <Table
        head={["Tool", "Hermes integration"]}
        rows={[
          ["Pandas", "DataFrame conversion"],
          ["Polars", "DataFrame conversion"],
          ["PyArrow", "Arrow data interchange"],
          ["DuckDB", "Analytical querying"],
          ["NumPy", "Numerical processing"],
          ["Parquet", "Dataset storage"],
          ["SQL databases", "Ingestion and export"],
          ["ML frameworks", "ML-ready datasets"],
        ]}
      />

      <H2 id="philosophy">Philosophy</H2>
      <List
        items={[
          "Data should be composable — datasets from different sources work together.",
          "Data should be inspectable — know what you received before building on it.",
          "Data should be reproducible — the same pipeline repeats predictably.",
          "Data should be traceable — every dataset has a clear origin.",
          "Data should be interoperable — work with the ecosystem, not lock you in.",
          "Data infrastructure should be reusable — across domains.",
        ]}
      />

      <H2 id="get-started">Next: install and run</H2>
      <CodeBlock code="pip install hermes-plt" title="terminal" />
      <P>
        Follow the <DocLink href="/docs/quickstart">Quickstart</DocLink> for a full walkthrough of
        the facade, fetching and computing features.
      </P>

      <PrevNext next={{ title: "Quickstart", href: "/docs/quickstart" }} />
    </article>
  );
}
