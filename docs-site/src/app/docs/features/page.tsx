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
  title: "Features",
  description:
    "The Hermes feature engine: @feature decorator, LineageGraph, TieredPlan, and the full country-risk and financial feature inventories.",
};

export default function FeaturesPage() {
  return (
    <article className="relative">
      <div className="pointer-events-none absolute -right-8 top-24 hidden opacity-40 sm:block">
        <Plant className="h-28 w-24" color="#ff4328" />
      </div>
      <DocTitle kicker="Core Concepts">Features</DocTitle>
      <Lead>
        Hermes turns raw datasets into derived intelligence through a tiered, dependency-aware
        feature engine that records lineage. ~57 features ship across five country-risk groups
        plus technical, fundamental, crypto-history and filing feature sets.
      </Lead>

      <H2 id="at-a-glance">Feature groups at a glance</H2>
      <Table
        head={["Group", "Count", "Source(s)", "Status"]}
        rows={[
          ["Economic", "18", "World Bank + IMF", "Working"],
          ["Environmental", "6", "ND-GAIN + World Bank", "Partial (2 placeholders)"],
          ["Security", "7", "SIPRI / NATO datasets", "Partial (4 placeholders)"],
          ["Social", "6", "World Bank + HRS / FSI / HDI", "Partial (1 placeholder)"],
          ["Geopolitical", "21", "GDELT / WGI", "Stubbed"],
          ["Technical (crypto)", "~50 per snapshot", "Binance", "Working"],
          ["Fundamental", "CompanyFundamental", "SEC + Finnhub + FRED + yfinance", "Working"],
          ["Filing (crypto fam)", "—", "SEC facts", "Working"],
        ]}
      />
      <P>
        Country-risk features are the bread-and-butter: five groups covering the dimensions that
        matter when assessing a sovereign. Financial features layer market and company intelligence
        on top.
      </P>

      <H2 id="engine">The feature engine</H2>
      <P>
        The core abstraction lives in <code>hermes/features/</code>. The <code>features</code>{" "}
        registry (constructed with <code>features(os_api)</code>) exposes five country-risk groups
        and <code>list_features()</code> returns every registered callable.
      </P>
      <CodeBlock
        title="registry"
        code={`class features:
    def __init__(self, os_api: str):
        self.eco = economic_features()
        self.env = enviromental_features()
        self.geo = geopolitical_features(os_api=os_api)
        self.sec = security_features()
        self.soc = social_features()

    def list_features(self) -> list[Callable]`}
      />

      <H2 id="decorator">@feature, LineageGraph & TieredPlan</H2>
      <P>
        Features register themselves through a <code>@feature</code> decorator that records their
        name, group, dependencies and compute expression into a module-level singleton{" "}
        <code>lineagegraph = LineageGraph()</code>:
      </P>
      <CodeBlock
        title="python"
        code={`from hermes.features import feature

@feature(
    name="gdp_growth_5y",
    group="economic",
    deps=["economic:gdp_growth_yoy"],
    compute="rolling(5).mean()",
)
async def compute_growth(df, config):
    return df["gdp_growth"].rolling(5).mean()`}
      />
      <P>
        <code>LineageGraph.register_feature(name, group, deps, compute, fn)</code> stores the
        record and appends the name to <code>groups[group]</code>.{" "}
        <code>resolve_group(group)</code> performs a <strong>topological layering</strong>: it
        repeatedly emits a tier of features whose cross-feature dependencies are already satisfied,
        producing a <code>TieredPlan(tiers, all_features)</code>. The graph and tiers persist to
        JSON via <code>save(path)</code> / <code>load(path)</code> (functions are dropped on load).
      </P>

      <H2 id="country-risk">Country-risk features</H2>
      <P>
        Every country-risk feature shares the signature{" "}
        <code>async &lt;feature&gt;(country_code, mode=&quot;F&quot;)</code>.{" "}
        <code>mode=&quot;F&quot;</code> returns the latest scalar; <code>mode=&quot;ML&quot;</code> returns a{" "}
        <code>pd.Series</code> indexed by year (2000–2025, forward-filled). Helper{" "}
        <code>adjust_year_range(df, year_col, start, end, fill_method, fill_value)</code> merges
        onto the full year range with <code>value</code>/<code>ffill</code>/<code>bfill</code>/
        <code>linear</code> fills.
      </P>

      <H3Section title="Economic (18)" note="World Bank + IMF">
        <CodeBlock
          title="economic"
          code={`gdp_growth_yoy            NY.GDP.MKTP.KD.ZG        GDP growth YoY (%)
gdp_growth_qoq            NY.GDP.MKTP.KD          GDP growth QoQ
industrial_production_yoy NV.IND.MANF.KD.ZG       industrial production YoY
inflation_cpi_yoy         FP.CPI.TOTL.ZG          CPI inflation YoY
inflation_volatility_12m  FP.CPI.TOTL             CPI YoY rolled 12-period std
ppi_yoy                   IMF ...PPI.IX.A         producer price index YoY
inflation_yoy             IMF ...CPI._T.IX.M     inflation YoY (monthly)
unemployment_rate         SL.UEM.TOTL.ZS
youth_unemployment        SL.UEM.1524.ZS
labor_force_participation SL.TLF.CACT.ZS
current_account_gdp_ratio BN.CAB.XOKA.GD.ZS
fx_reserves_months_import FI.RES.TOTL.MO
external_debt_gdp_ratio   DT.DOD.DECT.GN.ZS
fiscal_deficit_gdp        IMF WEO GGXCNL_NGDP
government_debt_gdp       IMF WEO GGXWDG_NGDP
reer_misalignment         IMF ...EREER_IX.M
banking_sector_health     FB.AST.NPLN.ZS
gdp_per_capita_ppp        NY.GDP.PCAP.PP.CD`}
        />
      </H3Section>

      <H3Section title="Environmental (6)" note="ND-GAIN + World Bank">
        <List
          items={[
            "climate_vulnerability_score — NDGAIN CVS dataset score (implemented)",
            "climate_readiness_score — NDGAIN CRS dataset score (implemented)",
            "energy_dependence_ratio — WB EG.IMP.CONS.ZS (implemented)",
            "water_stress_index — WB ER.H2O.FWTL.ZS (implemented)",
            "natural_disaster_risk — placeholder",
            "food_price_index_change_yoy — placeholder",
          ]}
        />
      </H3Section>

      <H3Section title="Security (7)" note="SIPRI / NATO datasets">
        <List
          items={[
            "military_spending_gdp — SIPRI military expenditure % of GDP (implemented)",
            "military_spending_growth_yoy — SIPRI pct_change(1)*100 (implemented)",
            "nato_member — NATO membership bool, deps=['nato:membership'] (implemented)",
            "alliance_strength_score, arms_imports_12m, arms_exports_12m, peacekeeping_troops — placeholders",
          ]}
        />
      </H3Section>

      <H3Section title="Social (6)" note="World Bank + HRS / FSI / HDI datasets">
        <List
          items={[
            "human_rights_score — HRS dataset human_right_score",
            "fragile_state_index — FSI dataset Total (0–120)",
            "human_development_index — HDI dataset score",
            "gini_coefficient — WB SI.POV.GINI",
            "poverty_headcount_ratio — WB SI.POV.DDAY",
            "social_stability_index — placeholder",
          ]}
        />
      </H3Section>

      <H3Section title="Geopolitical (21)" note="stubbed — NotImplementedError pending GDELT/WGI rebuild">
        <P>
          The public API surface is preserved: <code>conflict_event_count_30d/90d</code>,{" "}
          <code>conflict_trend</code>, <code>goldstein_scale_avg_30d</code>,{" "}
          <code>goldstein_scale_trend</code>, <code>battle_deaths_30d/90d</code>,{" "}
          <code>protest_event_count_30d</code>, <code>protest_violence_level</code>,{" "}
          <code>diplomatic_event_count_30d</code>, <code>diplomatic_intensity_avg</code>,{" "}
          <code>sanctions_count_active</code>, <code>sanctions_new_30d</code>,{" "}
          <code>sanctions_sector_coverage</code>, <code>governance_wgi_composite</code>,{" "}
          <code>corruption_perception_index</code>, <code>rule_of_law_score</code>,{" "}
          <code>regulatory_quality</code>, <code>democracy_index</code>,{" "}
          <code>regime_type</code>{" "}
          <code>(democracy | hybrid | autocracy)</code>, <code>press_freedom_score</code>.
        </P>
      </H3Section>

      <H2 id="pipeline-class">The country-risk pipeline</H2>
      <P>
        The <code>pipeline</code> class coordinates the groups.{" "}
        <code>get_country_risk_features(country)</code> validates the ISO3 code, runs all features
        concurrently with <code>asyncio.gather</code> (a <code>_safe_call</code> swallows
        exceptions into <code>None</code>), and returns:
      </P>
      <CodeBlock
        title="python"
        code={`{
  "country": "USA",
  "economic": {...},     # feature -> value
  "geopolitical": {...},
  "security": {...},
  "social": {...},
  "environmental": {...},
  "metadata": {
    "last_updated": ...,
    "features_version": "1.0.0",
  },
}`}
      />
      <P>
        <code>build_training_panel(fns, countries)</code> calls each function with{" "}
        <code>mode=&quot;ML&quot;</code> across countries and stacks them into a{" "}
        <code>pd.DataFrame</code> with a MultiIndex of <code>(country_iso3, date)</code> — ready
        for supervised modeling.
      </P>

      <H2 id="financial">Financial features</H2>

      <H3Section title="Technical analysis — TAfeatures (crypto, via Binance)">
        <P>
          Helpers: <code>_sma</code>, <code>_ema</code> (pandas <code>ewm</code>,{" "}
          <code>adjust=False</code>), <code>_zscore</code> (sample std, ddof=1),{" "}
          <code>_returns</code> (log returns). Methods each return a <code>dict</code> of
          features:
        </P>
        <Table
          head={["Method", "Features computed"]}
          rows={[
            [
              "calculate_price_features(candles)",
              "open, high, low, close, volume, quote_volume, ret_1b/5b/10b/60b, ret_open_to_close, hl_range, body_range, dist_sma_20/50/200, ema_diff_9_21, ema_diff_21_50, vol_20, vol_60, atr_14_norm, volume_rel_20, taker_buy_vol_ratio",
            ],
            [
              "trade_features(symbol, limit=1000)",
              "trades_count, trade_window_*, trade_buy_vol_ratio, avg_trade_size, median_trade_size, large_trade_vol_ratio (95th pct)",
            ],
            [
              "orderbook_features(symbol, limit=20)",
              "bid/ask price & qty, spread_abs, spread_bps, top_book_imbalance, depth_bid_total, depth_ask_total, depth_imbalance",
            ],
            [
              "day_features(symbol)",
              "high/low/last_24h, range_24h, pct_change_24h, pos_in_24h_range, volume_24h, quote_volume_24h",
            ],
            [
              "funding_features(symbol, limit=30)",
              "funding_rate, funding_rate_lag_3, funding_rate_change, funding_rate_zscore",
            ],
            [
              "oi_features(symbol)",
              "open_interest, oi_change_1h, oi_change_24h",
            ],
            [
              "positioning_features(symbol, period='1h', limit=30)",
              "trend_score, mean_reversion_score, liquidity_score, order_flow_score, sentiment_score",
            ],
          ]}
        />
        <P>
          <code>build_snapshot(symbol)</code> (→ <code>TechnicalSnapshot</code> dataclass, ~50
          fields) adds <code>oi_to_volume_24h</code>; <code>get_technical(symbol)</code> returns
          snapshots.
        </P>
      </H3Section>

      <H3Section title="Crypto history — CryptoHistory">
        <P>
          <code>get_history(symbol, interval=&apos;1d&apos;, market=&apos;future&apos;, years=2)</code> fetches
          Binance history and computes a vectorized rolling feature set ({" "}
          <code>TechnicalHistoryRow</code>, ~90 fields) including: log returns{" "}
          <code>ret_1b/3b/5b/10b/20b/60b</code>, <code>rsi_14</code> (Wilder),{" "}
          <code>macd/macd_signal/macd_hist</code>, Bollinger{" "}
          <code>bb_upper/lower/width/pct</code>, <code>obv</code>,{" "}
          <code>returns_skew_20</code>/<code>returns_kurt_20</code>, <code>drawdown</code>,{" "}
          <code>amihud_illiquidity</code>, plus extended volume/z-score/trend/ratio features.
        </P>
      </H3Section>

      <H3Section title="Fundamental analysis — FAfeatures">
        <P>
          Combines SEC facts + filing metadata + Finnhub metrics + FRED macro + yfinance estimates
          into a <code>CompanyFundamental</code> row via{" "}
          <code>get_fundamentels(symbol)</code>. Notable helpers:
        </P>
        <List
          items={[
            "extract_funds_sec(data) — maps SEC us-gaap facts through SEC_TAG_MAP to most-recent values",
            "extract_filing_meta(data) — filing_date, fiscal_year, fiscal_period, filing_type",
            "macro() — FRED GDP, CPI, FEDFUNDS, UNRATE, GFDEBTN, exchange rates",
            "Computes revenue_surprise = (revenue − revenue_estimate) / revenue_estimate",
            "Ratio metadata aliases: P/E, P/S, P/B, EV/EBITDA, ROE, ROA, Debt/Equity",
          ]}
        />
      </H3Section>

      <H3Section title="Company filings — CompanyFiling">
        <P>
          <code>get_history(quarters=8, symbols=None)</code> fetches SEC facts for each ticker and
          computes filing-derived fundamentals with true YoY matching by fiscal period. Feature
          families: growth, margins, liquidity, leverage, cash-flow quality, efficiency,
          balance-sheet growth, shareholder (share_count/buyback/dividend change), and coverage
          (<code>interest_coverage</code>). <code>get_candle_history</code> pulls candles via
          Finnhub with automatic yfinance fallback when fewer than 100 rows.
        </P>
      </H3Section>

      <H2 id="compute">Compute through the facade</H2>
      <CodeBlock
        title="python"
        code={`from hermes import Hermes
hermes = Hermes(opensanction_api="x", new_data_api="x",
                sec_username="x", sec_email="x")

# Full country-risk scan
scan = await hermes.country_features.get_country_risk_features("USA")

# Single economic feature, ML-mode series
series = await hermes.lf.eco.gdp_growth_yoy("USA", mode="ML")

# Technical snapshot for a crypto symbol
snap = hermes.ta_feature.get_technical("BTCUSDT")`}
      />

      <Callout title="Feature catalog" tone="cedar">
        The feature engine (<code>hermes/features/</code>) is currently de-scoped from the v1 core;
        the product focus is the data engine and the finance/defense data-provider layer. See
        <code>docs/hermes.md</code> for the current scope.
      </Callout>
      <Sparkle className="mt-8 h-10 w-10 opacity-50" color="#ff4328" strokeWidth={4} />

      <PrevNext
        prev={{ title: "Connectors", href: "/docs/connectors" }}
        next={{ title: "API Reference", href: "/docs/api-reference" }}
      />
    </article>
  );
}

function H3Section({ title, note, children }: { title: string; note?: string; children: React.ReactNode }) {
  return (
    <section className="my-8">
      <div className="mb-2 flex flex-wrap items-baseline gap-3">
        <h3 className="font-heading text-xl font-extrabold text-ink">{title}</h3>
        {note && <span className="font-mono text-[12px] text-ink">{note}</span>}
      </div>
      {children}
    </section>
  );
}
