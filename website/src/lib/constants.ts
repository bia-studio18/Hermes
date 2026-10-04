export const GITHUB_URL = "https://github.com/ryomenhaider/Hermes";
export const DISCORD_URL = "https://discord.gg/UeJuEz4YdS";
export const LINKEDIN_URL = "https://www.linkedin.com/company/hermes-plt";
export const DOCS_URL = "https://docs.hermes-plt.xyz";

export const SECTIONS = [
  { id: "platform", index: "01", label: "Platform" },
  { id: "capabilities", index: "02", label: "Capabilities" },
  { id: "interface", index: "03", label: "Interface" },
  { id: "reference", index: "04", label: "Reference" },
] as const;

export const EXTERNAL_LINKS = [
  { label: "Docs", href: DOCS_URL },
  { label: "GitHub", href: GITHUB_URL },
] as const;

// Counts, not traffic metrics: 10 connector packages, 7 schema domains,
// 3 interchange formats, 1 shared cache/retry layer.
export const STATS = [
  {
    value: 10,
    label: "Built-in connectors",
    note: "SEC, FRED, IMF, World Bank, GDELT, market data, sanctions",
  },
  {
    value: 7,
    label: "Canonical schema domains",
    note: "economic, market, financial, geopolitical, entity, document, security",
  },
  {
    value: 3,
    label: "Dataframe ecosystems",
    note: "Polars, Arrow and Pandas over one columnar core",
  },
  {
    value: 1,
    label: "Shared cache and retry layer",
    note: "Inherited by every connector from a single base class",
  },
] as const;

export const TICKER = [
  "SEC EDGAR",
  "FRED",
  "IMF",
  "WORLD BANK",
  "GDELT",
  "BINANCE",
  "FINNHUB",
  "YAHOO FINANCE",
  "OPENSANCTIONS",
] as const;

export const PIPELINE = [
  {
    id: "source",
    label: "Source",
    icon: "database",
    code: "hermes/connectors/base.py",
    headline: "Declare the source once",
    body: "Every connector subclasses a single base and inherits caching, retry and provenance. No source gets bespoke plumbing.",
    signal: ["cache", "parquet-backed", "shared across all 10 connectors"],
  },
  {
    id: "acquire",
    label: "Acquire",
    icon: "share",
    code: "hermes/api/acquire.py",
    headline: "One call, any source",
    body: "hr.fetch() routes to the right connector, retries transient failures and returns a Dataset. fetch_raw() bypasses the pipeline when you need the payload untouched.",
    signal: ["retry with backoff", "raw passthrough available", "Dataset return type"],
  },
  {
    id: "parse",
    label: "Parse",
    icon: "file",
    code: "hermes/parsing",
    headline: "Structures arrive consistent",
    body: "JSON, CSV, XML and tabular payloads land in a Polars frame with inferred types and the source's own metadata retained.",
    signal: ["json, csv, xml", "polars frame out", "source metadata kept"],
  },
  {
    id: "normalize",
    label: "Normalize",
    icon: "settings",
    code: "hermes/normalization/engine.py",
    headline: "Rules, not rewrites",
    body: "A composable rule chain maps inconsistent source fields onto versioned canonical schemas. Ask for a report and you get every change it made, per record.",
    signal: ["rule chain", "per-record diff report", "streams or batches"],
  },
  {
    id: "validate",
    label: "Validate",
    icon: "check",
    code: "hermes/validation",
    headline: "Fail loudly, early",
    body: "Schemas are registered and versioned. Validation runs against the registry, so a broken contract surfaces at the boundary instead of three layers downstream.",
    signal: ["versioned registry", "typed errors", "runs pre-serve"],
  },
  {
    id: "store",
    label: "Store",
    icon: "layers",
    code: "hermes/storage",
    headline: "Columnar by default",
    body: "Datasets save to Parquet with a stable on-disk format, so a dataset written today loads identically in every later version.",
    signal: ["parquet", "arrow interchange", "stable format"],
  },
  {
    id: "serve",
    label: "Serve",
    icon: "zap",
    code: "hermes/export",
    headline: "Hand it to your stack",
    body: "Clean conversion to Polars, Arrow or Pandas, plus export for the formats your warehouse already reads. No wrapper objects in the way.",
    signal: ["polars, arrow, pandas", "warehouse export", "no lock-in"],
  },
] as const;

export const DATA_ROWS = [
  ["USA", "NY.GDP.MKTP.CD", "27438.6", "2024-01-01"],
  ["DEU", "NY.GDP.MKTP.CD", "4523.9", "2024-01-01"],
  ["JPN", "NY.GDP.MKTP.CD", "4226.8", "2024-01-01"],
  ["GBR", "NY.GDP.MKTP.CD", "3340.0", "2024-01-01"],
] as const;

// Real entry points from hermes/__init__.py and hermes/cli/__main__.py.
export const CODE_TABS = [
  {
    id: "acquire",
    label: "Acquire",
    caption: "hermes/api/acquire.py",
    code: `import hermes as hr

# cached, parsed and schema-validated in one call
gdp = hr.fetch("world_bank", indicator="NY.GDP.MKTP.CD")

report = hr.profile(gdp)                # types, nulls, ranges
clean = hr.normalize(gdp, report=True)  # canonical economic schema`,
  },
  {
    id: "resolve",
    label: "Resolve",
    caption: "hermes/api/entities.py",
    code: `import hermes as hr

# any identifier form: ticker, CIK, LEI, ISIN or plain name
hit = hr.resolve_company("AAPL")

hit.status     # "success"
hit.data       # canonical company record
hit.metadata   # which identifier matched, and where`,
  },
  {
    id: "cli",
    label: "CLI",
    caption: "hermes/cli",
    code: `hermes fetch world_bank --indicator NY.GDP.MKTP.CD
hermes profile gdp.parquet
hermes validate --schema economic
hermes entity resolve AAPL`,
  },
] as const;

export const fadeUp = {
  initial: { opacity: 0, y: 20 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-80px" },
  transition: { duration: 0.6, ease: "easeOut" as const },
};
