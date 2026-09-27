"use client";

import { motion } from "framer-motion";
import { fadeUp } from "@/lib/constants";

/**
 * The section header used down the page: a numbered index, a rule, a mono
 * kicker, then the title. One component so the numbering and spacing stay
 * consistent across every section.
 */
export function SectionHead({
  index,
  kicker,
  title,
  lede,
  align = "left",
}: {
  index: string;
  kicker: string;
  title: string;
  lede?: string;
  align?: "left" | "center";
}) {
  return (
    <motion.div
      {...fadeUp}
      className={`mb-14 ${align === "center" ? "mx-auto max-w-3xl text-center" : "max-w-3xl"}`}
    >
      <div className={`flex items-center gap-3 ${align === "center" ? "justify-center" : ""}`}>
        <span className="label tabular text-teal-bright">{index}</span>
        <span className="h-px w-8 bg-hairline-strong" aria-hidden="true" />
        <span className="label text-gray">{kicker}</span>
      </div>
      <h2 className="mt-5 font-sans text-3xl font-bold tracking-tight text-offwhite sm:text-4xl">
        {title}
      </h2>
      {lede ? (
        <p className="mt-4 text-base leading-relaxed text-gray-bright">{lede}</p>
      ) : null}
    </motion.div>
  );
}
