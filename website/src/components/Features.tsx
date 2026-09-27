"use client";

import { motion } from "framer-motion";
import { Database, FileStack, Network, ServerCog, type LucideIcon } from "lucide-react";
import { SectionHead } from "@/components/SectionHead";
import { fadeUp } from "@/lib/constants";

const FEATURES: {
  icon: LucideIcon;
  title: string;
  description: string;
  facts: string[];
}[] = [
  {
    icon: Database,
    title: "Multi-source acquisition",
    description:
      "Ten connectors for financial APIs, government portals and local files, all sharing one caching and retry layer.",
    facts: ["SEC · FRED · IMF · World Bank", "GDELT · Binance · Finnhub", "Parquet-backed cache"],
  },
  {
    icon: FileStack,
    title: "Schema normalization",
    description:
      "Inconsistent source formats are normalized onto versioned canonical schemas, so every dataset speaks the same language.",
    facts: ["7 schema domains", "Composable rule chain", "Per-record diff report"],
  },
  {
    icon: Network,
    title: "Entity resolution",
    description:
      "Resolve companies, countries and securities across every identifier form they appear under — tickers, CIKs, ISINs, LEIs and names.",
    facts: ["Canonical HRM identifiers", "Alias registry", "Cross-source matching"],
  },
  {
    icon: ServerCog,
    title: "Scalable storage",
    description:
      "Parquet-backed caching, Dataset save and export, and clean interchange with the dataframe stack you already run.",
    facts: ["Stable on-disk format", "Polars · Arrow · Pandas", "Rust core"],
  },
];

export function Features() {
  return (
    <section id="capabilities" className="border-t border-hairline">
      <div className="shell py-24">
        <SectionHead
          index="02"
          kicker="Capabilities"
          title="Built for scale. Designed for reliability."
          lede="Four capabilities, each a module you can adopt on its own. Nothing here is a wrapper around someone else's product."
        />

        <div className="grid grid-cols-1 gap-px border border-hairline bg-hairline md:grid-cols-2">
          {FEATURES.map((f, i) => (
            <motion.div
              key={f.title}
              {...fadeUp}
              transition={{ duration: 0.5, delay: (i % 2) * 0.08, ease: "easeOut" }}
              className="cell group relative bg-midnight p-7"
            >
              <div className="flex items-start justify-between">
                <f.icon className="h-6 w-6 text-teal-bright" aria-hidden="true" />
                <span className="label tabular text-gray/60">
                  {String(i + 1).padStart(2, "0")}
                </span>
              </div>

              <h3 className="mt-6 font-sans text-lg font-semibold tracking-tight text-offwhite">
                {f.title}
              </h3>
              <p className="mt-3 text-sm leading-relaxed text-gray-bright">
                {f.description}
              </p>

              <ul className="mt-6 space-y-1.5 border-t border-hairline pt-5">
                {f.facts.map((fact) => (
                  <li key={fact} className="label flex items-center gap-2.5 text-gray">
                    <span
                      className="h-1 w-1 rotate-45 bg-teal transition-colors duration-200 group-hover:bg-teal-bright"
                      aria-hidden="true"
                    />
                    {fact}
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
