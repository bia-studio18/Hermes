"use client";

import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Check, Copy } from "lucide-react";
import { CODE_TABS } from "@/lib/constants";
import { Code } from "@/components/Code";
import { SectionHead } from "@/components/SectionHead";

export function CodeTabs() {
  const [active, setActive] = useState(0);
  const [copied, setCopied] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const tab = CODE_TABS[active];

  useEffect(() => () => clearTimeout(timer.current), []);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(tab.code);
      setCopied(true);
      clearTimeout(timer.current);
      timer.current = setTimeout(() => setCopied(false), 1600);
    } catch {
      // clipboard blocked on an insecure origin
    }
  };

  return (
    <section id="interface" className="border-t border-hairline bg-panel">
      <div className="shell py-24">
        <SectionHead
          index="03"
          kicker="Interface"
          title="One library, one CLI, one contract."
          lede="The same pipeline from Python or from a shell. Nothing to learn twice, and no wrapper object between you and the data."
        />

        <div className="panel brackets overflow-hidden">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-hairline">
            <div className="flex" role="tablist" aria-label="Interface examples">
              {CODE_TABS.map((t, i) => (
                <button
                  key={t.id}
                  type="button"
                  role="tab"
                  aria-selected={i === active}
                  aria-controls="code-panel"
                  onClick={() => setActive(i)}
                  className={`label relative px-5 py-3.5 transition-colors duration-150 ${
                    i === active ? "text-offwhite" : "text-gray hover:text-gray-bright"
                  }`}
                >
                  {t.label}
                  {i === active ? (
                    <motion.span
                      layoutId="code-tab-rule"
                      className="absolute inset-x-0 -bottom-px h-px bg-teal-bright"
                      transition={{ duration: 0.25, ease: "easeOut" }}
                    />
                  ) : null}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-3 pr-4">
              <span className="label hidden text-gray sm:inline">{tab.caption}</span>
              <button
                type="button"
                onClick={copy}
                aria-label={copied ? "Copied" : "Copy code"}
                className="label flex items-center gap-1.5 text-gray transition-colors duration-150 hover:text-teal-bright"
              >
                {copied ? (
                  <Check className="h-3.5 w-3.5" aria-hidden="true" />
                ) : (
                  <Copy className="h-3.5 w-3.5" aria-hidden="true" />
                )}
                <span className="hidden sm:inline">{copied ? "Copied" : "Copy"}</span>
              </button>
            </div>
          </div>

          <div className="relative">
            <AnimatePresence mode="wait" initial={false}>
              <motion.div
                key={tab.id}
                id="code-panel"
                role="tabpanel"
                aria-label={`${tab.label} example`}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.2, ease: "easeOut" }}
                className="overflow-x-auto px-5 py-6"
              >
                <Code>{tab.code}</Code>
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </div>
    </section>
  );
}
