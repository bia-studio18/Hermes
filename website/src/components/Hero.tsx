"use client";

import { useEffect, useRef } from "react";
import { ArrowRight } from "lucide-react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { MapTexture } from "@/components/MapTexture";
import { PipelineStrip } from "@/components/PipelineStrip";
import { Telemetry } from "@/components/Telemetry";
import { DOCS_URL, GITHUB_URL } from "@/lib/constants";

gsap.registerPlugin(ScrollTrigger);

export function Hero() {
  const root = useRef<HTMLElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      const mm = gsap.matchMedia();

      mm.add("(prefers-reduced-motion: no-preference)", () => {
        // Entrance. `from` tween states, so the markup itself stays visible and
        // a reduced-motion visitor gets the hero already settled.
        gsap
          .timeline({ defaults: { ease: "power3.out" } })
          .from("[data-hero='eyebrow']", { opacity: 0, y: 12, duration: 0.5 })
          .from("[data-hero='title']", { opacity: 0, y: 26, duration: 0.75 }, "-=0.28")
          .from("[data-hero='lede']", { opacity: 0, y: 16, duration: 0.6 }, "-=0.5")
          .from(
            "[data-hero='actions'] > *",
            { opacity: 0, y: 12, duration: 0.45, stagger: 0.08 },
            "-=0.4",
          )
          .from("[data-hero='panel']", { opacity: 0, y: 20, duration: 0.6 }, "-=0.45");

        // Parallax: the texture and grid drift slower than the page scrolls.
        gsap.to("[data-hero='texture']", {
          yPercent: 16,
          ease: "none",
          scrollTrigger: {
            trigger: root.current,
            start: "top top",
            end: "bottom top",
            scrub: true,
          },
        });
        gsap.to("[data-hero='grid']", {
          yPercent: 8,
          opacity: 0.15,
          ease: "none",
          scrollTrigger: {
            trigger: root.current,
            start: "top top",
            end: "bottom top",
            scrub: true,
          },
        });
      });
    }, root);

    return () => ctx.revert();
  }, []);

  return (
    <section ref={root} className="relative overflow-hidden">
      <div className="absolute inset-0" aria-hidden="true">
        <div data-hero="grid" className="grid-field absolute inset-0" />
        <div data-hero="texture" className="absolute -inset-y-16 inset-x-0 opacity-45">
          <MapTexture />
        </div>
        <div className="absolute inset-0 bg-gradient-to-b from-midnight/40 via-midnight/70 to-midnight" />
      </div>

      <div className="shell relative grid grid-cols-1 items-center gap-14 pb-28 pt-24 lg:grid-cols-[1.15fr_1fr] lg:gap-16 lg:pb-36 lg:pt-32">
        <div>
          <div data-hero="eyebrow" className="flex items-center gap-3">
            <span className="h-1.5 w-1.5 rotate-45 bg-teal-bright" aria-hidden="true" />
            <span className="label text-gray">Data infrastructure</span>
          </div>

          <h1
            data-hero="title"
            className="mt-6 font-sans text-5xl font-bold leading-[0.95] tracking-[-0.03em] text-offwhite sm:text-6xl lg:text-[5.25rem]"
          >
            Every source.
            <br />
            <span className="text-gray-bright">One contract.</span>
          </h1>

          <p
            data-hero="lede"
            className="mt-7 max-w-xl text-base leading-relaxed text-gray-bright sm:text-lg"
          >
            Hermes acquires, normalizes, validates and serves structured and unstructured
            data through one interface — financial feeds, government portals and files, all
            speaking the same canonical schema.
          </p>

          <div data-hero="actions" className="mt-10 flex flex-col gap-3 sm:flex-row">
            <a href={DOCS_URL} className="btn btn-primary">
              Read the docs
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </a>
            <a href={GITHUB_URL} className="btn btn-ghost">
              View source
            </a>
          </div>

          <div className="mt-12 border-t border-hairline pt-6">
            <PipelineStrip />
          </div>
        </div>

        <div data-hero="panel" className="lg:pl-4">
          <Telemetry />
        </div>
      </div>
    </section>
  );
}
