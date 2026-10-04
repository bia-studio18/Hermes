"use client";

import { motion } from "framer-motion";
import { ArrowRight, Database, FileStack, Network, ServerCog } from "lucide-react";
import { SectionHead } from "@/components/SectionHead";
import { DOCS_URL, GITHUB_URL, fadeUp } from "@/lib/constants";

const DOCS_NAV = [
  { label: "Introduction" },
  { label: "Quickstart" },
  { label: "Installation" },
  { header: "CORE" },
  { label: "Acquisition" },
  { label: "Parsing" },
  { label: "Normalization" },
  { label: "Validation" },
  { label: "Metadata" },
  { label: "Entities" },
  { header: "DATA" },
  { label: "Datasets" },
  { label: "Schemas" },
  { label: "Storage" },
  { label: "Querying" },
  { label: "Export" },
  { header: "REFERENCE" },
  { label: "Python API" },
  { label: "CLI" },
  { label: "Configuration" },
];

const FEATURE_BADGES = [
  { icon: Database, label: "Multi-source acquisition" },
  { icon: FileStack, label: "Schema normalization" },
  { icon: Network, label: "Entity resolution" },
  { icon: ServerCog, label: "Scalable storage" },
];

export function DocsPreview() {
  return (
    <section id="reference" className="border-t border-hairline">
      <div className="shell py-24">
        <SectionHead
          index="04"
          kicker="Reference"
          title="Documented end to end."
          lede="Ten connector guides, seven schema domains, the full Python API and every CLI command, with runnable examples."
        />

        <motion.div {...fadeUp} className="panel brackets overflow-hidden">
          <div className="flex items-center justify-between border-b border-hairline px-4 py-2.5">
            <span className="label text-gray-bright">docs.hermes-plt.xyz</span>
          </div>

          <div className="flex">
            <aside
              className="hidden w-64 shrink-0 border-r border-hairline p-5 sm:block"
              aria-hidden="true"
            >
              <nav className="space-y-0.5 font-sans">
                {DOCS_NAV.map((item, i) =>
                  item.header ? (
                    <p
                      key={`${item.header}-${i}`}
                      className="label px-2 pb-1 pt-4 text-teal-bright"
                    >
                      {item.header}
                    </p>
                  ) : (
                    <p
                      key={item.label}
                      className={`cursor-default rounded-sm px-2 py-1.5 text-sm ${
                        item.label === "Introduction"
                          ? "bg-teal/10 font-medium text-teal-bright"
                          : "text-gray-bright"
                      }`}
                    >
                      {item.label}
                    </p>
                  ),
                )}
              </nav>
            </aside>

            <div className="min-w-0 flex-1 p-6 sm:p-8">
              <p className="label text-teal-bright">Introduction</p>
              <h3 className="mt-3 font-sans text-2xl font-bold tracking-tight text-offwhite">
                Introduction
              </h3>
              <p className="mt-3 max-w-lg text-sm leading-relaxed text-gray-bright">
                Hermes provides a unified interface for acquiring, processing and serving
                data, from financial feeds to geopolitical sources, with built-in
                validation, normalization and provenance tracking.
              </p>

              <div className="panel mt-6 flex items-center gap-3 overflow-x-auto rounded-none px-4 py-3">
                <span className="label text-teal-bright" aria-hidden="true">
                  $
                </span>
                <code className="whitespace-nowrap font-mono text-sm text-gray-bright">
                  pip install hermes-plt
                </code>
              </div>

              <div className="mt-6 flex flex-wrap gap-2">
                {FEATURE_BADGES.map((b) => (
                  <span
                    key={b.label}
                    className="inline-flex items-center gap-1.5 border border-teal/30 px-2.5 py-1 text-xs text-gray-bright"
                  >
                    <b.icon className="h-3.5 w-3.5 text-teal-bright" aria-hidden="true" />
                    {b.label}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div
          {...fadeUp}
          className="mx-auto mt-20 max-w-2xl text-center"
        >
          <span className="label inline-flex items-center gap-3">
            <span className="h-px w-8 bg-hairline-strong" aria-hidden="true" />
            <span className="text-teal-bright">Get started</span>
            <span className="h-px w-8 bg-hairline-strong" aria-hidden="true" />
          </span>
          <h2 className="mt-6 font-sans text-3xl font-bold tracking-tight text-offwhite sm:text-4xl">
            Data infrastructure for the modern world.
          </h2>
          <p className="mt-4 text-base leading-relaxed text-gray-bright">
            Install it, point it at a source, and get a validated dataset. That is the
            whole onboarding.
          </p>
          <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
            <a href={DOCS_URL} className="btn btn-primary">
              Get started
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </a>
            <a href={GITHUB_URL} className="btn btn-ghost">
              View on GitHub
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
