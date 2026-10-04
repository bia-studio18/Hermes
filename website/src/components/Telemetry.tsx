"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";

const LOG = [
  { src: "world_bank", rows: "1,204", schema: "economic.v3" },
  { src: "sec.edgar", rows: "318", schema: "document.v2" },
  { src: "fred", rows: "9,551", schema: "economic.v3" },
  { src: "gdelt", rows: "24,910", schema: "geopolitical.v1" },
  { src: "binance", rows: "86,400", schema: "market.v4" },
  { src: "opensanctions", rows: "4,772", schema: "entity.v2" },
  { src: "imf", rows: "612", schema: "economic.v3" },
  { src: "finnhub", rows: "2,940", schema: "financial.v2" },
];

const VISIBLE = 5;

export function Telemetry() {
  const [head, setHead] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setHead((h) => (h + 1) % LOG.length), 1500);
    return () => clearInterval(id);
  }, []);

  const rows = Array.from({ length: VISIBLE }, (_, i) => LOG[(head + i) % LOG.length]);

  return (
    <div className="panel brackets flex h-full flex-col overflow-hidden">
      <div className="flex items-center justify-between border-b border-hairline px-4 py-2.5">
        <span className="label text-gray-bright">One run, nine sources</span>
        <span className="label text-gray">illustrative</span>
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
            <span className="w-24 shrink-0 truncate text-gray-bright">{row.src}</span>
            <span className="tabular w-14 shrink-0 text-right text-offwhite">{row.rows}</span>
            <span className="hidden w-24 shrink-0 truncate text-teal-bright sm:block">
              {row.schema}
            </span>
          </motion.div>
        ))}
      </div>

      <div className="border-t border-hairline px-4 py-2.5">
        <span className="label text-gray">rows acquired, then normalized to schema</span>
      </div>
    </div>
  );
}
