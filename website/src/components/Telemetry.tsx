"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";

// A fixed rotation of the shipped connectors. Static content, so the server
// render and the first client render agree; only the rotation is state.
const LOG = [
  { src: "world_bank", rows: "1,204", schema: "economic.v3", ms: "412" },
  { src: "sec.edgar", rows: "318", schema: "document.v2", ms: "286" },
  { src: "fred", rows: "9,551", schema: "economic.v3", ms: "198" },
  { src: "gdelt", rows: "24,910", schema: "geopolitical.v1", ms: "671" },
  { src: "binance", rows: "86,400", schema: "market.v4", ms: "94" },
  { src: "opensanctions", rows: "4,772", schema: "entity.v2", ms: "355" },
  { src: "imf", rows: "612", schema: "economic.v3", ms: "503" },
  { src: "finnhub", rows: "2,940", schema: "financial.v2", ms: "167" },
];

const VISIBLE = 5;

export function Telemetry() {
  const [head, setHead] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setHead((h) => (h + 1) % LOG.length), 1500);
    return () => clearInterval(id);
  }, []);

  // Keys are stable per line, so advancing the window slides the surviving rows
  // up via `layout` and animates only the one entering line.
  const rows = Array.from({ length: VISIBLE }, (_, i) => LOG[(head + i) % LOG.length]);

  return (
    <div className="panel brackets flex h-full flex-col overflow-hidden">
      <div className="flex items-center justify-between border-b border-hairline px-4 py-2.5">
        <span className="label text-gray-bright">Live pipeline</span>
        <span className="label flex items-center gap-2 text-teal-bright">
          <span className="pulse-dot" aria-hidden="true" />
          streaming
        </span>
      </div>

      <div className="h-[110px] overflow-hidden px-4 py-2.5">
        {rows.map((row, i) => (
          <motion.div
            key={row.src}
            layout
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1 - i * 0.15, y: 0 }}
            transition={{ duration: 0.35, ease: "easeOut" }}
            className="label flex items-center gap-3 py-[3px]"
          >
            <span className="w-2 shrink-0 text-teal-bright" aria-hidden="true">
              ›
            </span>
            <span className="w-24 shrink-0 truncate text-gray-bright">{row.src}</span>
            <span className="tabular w-14 shrink-0 text-right text-offwhite">{row.rows}</span>
            <span className="hidden w-24 shrink-0 truncate text-teal-bright sm:block">
              {row.schema}
            </span>
            <span className="tabular ml-auto shrink-0 text-gray">{row.ms}ms</span>
          </motion.div>
        ))}
      </div>

      <div className="flex items-center justify-between border-t border-hairline px-4 py-2.5">
        <span className="label text-gray">10 / 10 connectors healthy</span>
        <span className="label tabular text-gray">p95 412ms</span>
      </div>
    </div>
  );
}
