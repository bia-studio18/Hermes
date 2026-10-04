"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { STATS } from "@/lib/constants";

gsap.registerPlugin(ScrollTrigger);

export function Metrics() {
  const root = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      const mm = gsap.matchMedia();

      mm.add("(prefers-reduced-motion: no-preference)", () => {
        gsap.utils.toArray<HTMLElement>("[data-count]").forEach((el) => {
          const target = Number(el.dataset.count);
          const state = { value: 0 };
          gsap.to(state, {
            value: target,
            duration: 1.5,
            ease: "power3.out",
            scrollTrigger: { trigger: el, start: "top 88%", once: true },
            onUpdate: () => {
              el.textContent = String(Math.round(state.value));
            },
          });
        });
      });
    }, root);

    return () => ctx.revert();
  }, []);

  return (
    <div
      ref={root}
      className="grid grid-cols-1 border-t border-hairline sm:grid-cols-2 lg:grid-cols-4"
    >
      {STATS.map((stat, i) => (
        <div
          key={stat.label}
          className={`group relative px-5 py-10 sm:px-8 ${
            i > 0 ? "border-t border-hairline sm:border-t-0 sm:border-l" : ""
          } ${i === 2 ? "sm:border-t lg:border-t-0" : ""}`}
        >
          <p className="font-mono text-5xl font-medium leading-none tracking-tight text-offwhite tabular">
            <span data-count={stat.value}>{stat.value}</span>
          </p>
          <p className="mt-4 font-sans text-sm font-medium text-offwhite">{stat.label}</p>
          <p className="mt-2 font-mono text-[11px] leading-relaxed text-gray">{stat.note}</p>
          <span
            className="absolute inset-x-0 bottom-0 h-px origin-left scale-x-0 bg-teal-bright transition-transform duration-500 group-hover:scale-x-100"
            aria-hidden="true"
          />
        </div>
      ))}
    </div>
  );
}
