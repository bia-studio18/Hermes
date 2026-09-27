"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { Menu, X } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { LogoLockup } from "@/components/Logo";
import { SocialLinks } from "@/components/SocialLinks";
import { EXTERNAL_LINKS, SECTIONS } from "@/lib/constants";

gsap.registerPlugin(ScrollTrigger);

export function Header() {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [active, setActive] = useState<string | null>(null);
  const bar = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Progress rule across the header, plus a scroll-spy over the page sections.
  useEffect(() => {
    const ctx = gsap.context(() => {
      if (bar.current) {
        gsap.fromTo(
          bar.current,
          { scaleX: 0 },
          {
            scaleX: 1,
            ease: "none",
            scrollTrigger: {
              trigger: document.documentElement,
              start: "top top",
              end: "bottom bottom",
              scrub: 0.25,
            },
          },
        );
      }

      SECTIONS.forEach(({ id }) => {
        const el = document.getElementById(id);
        if (!el) return;
        ScrollTrigger.create({
          trigger: el,
          start: "top 45%",
          end: "bottom 45%",
          onToggle: (self) => {
            if (self.isActive) setActive(id);
          },
        });
      });
    });

    return () => ctx.revert();
  }, []);

  // The menu is a scroll trap on mobile — close it if the viewport grows back.
  useEffect(() => {
    if (!open) return;
    const mq = window.matchMedia("(min-width: 768px)");
    const close = () => setOpen(false);
    mq.addEventListener("change", close);
    return () => mq.removeEventListener("change", close);
  }, [open]);

  return (
    <header
      className={`sticky top-0 z-50 border-b transition-colors duration-200 ${
        scrolled ? "border-hairline bg-midnight/85 backdrop-blur-md" : "border-transparent bg-midnight"
      }`}
    >
      <div className="shell flex h-16 items-center justify-between gap-6">
        <Link href="/" aria-label="Hermes home" className="inline-flex shrink-0">
          <LogoLockup />
        </Link>

        <nav className="hidden items-center gap-7 md:flex" aria-label="Sections">
          {SECTIONS.map((s) => (
            <a
              key={s.id}
              href={`#${s.id}`}
              aria-current={active === s.id ? "true" : undefined}
              className={`label flex items-center gap-1.5 transition-colors duration-150 ${
                active === s.id ? "text-teal-bright" : "text-gray hover:text-gray-bright"
              }`}
            >
              <span className="tabular text-[10px] opacity-60">{s.index}</span>
              {s.label}
            </a>
          ))}
        </nav>

        <div className="hidden shrink-0 items-center gap-6 lg:flex">
          <div className="h-4 w-px bg-hairline-strong" aria-hidden="true" />
          {EXTERNAL_LINKS.map((l) => (
            <a
              key={l.label}
              href={l.href}
              target="_blank"
              rel="noopener noreferrer"
              className="label text-gray transition-colors duration-150 hover:text-offwhite"
            >
              {l.label}
            </a>
          ))}
          <SocialLinks />
        </div>

        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          className="btn btn-ghost h-10 w-10 shrink-0 p-0 md:hidden"
          aria-expanded={open}
          aria-label={open ? "Close menu" : "Open menu"}
        >
          {open ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
        </button>
      </div>

      {/* Scroll progress — 1px rule pinned to the header's lower edge */}
      <span
        ref={bar}
        aria-hidden="true"
        className="absolute inset-x-0 bottom-0 h-px origin-left scale-x-0 bg-teal-bright"
      />

      <AnimatePresence>
        {open ? (
          <motion.nav
            key="mobile"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.22, ease: "easeOut" }}
            className="overflow-hidden border-t border-hairline bg-midnight md:hidden"
            aria-label="Mobile"
          >
            <div className="shell flex flex-col py-4">
              {SECTIONS.map((s) => (
                <a
                  key={s.id}
                  href={`#${s.id}`}
                  onClick={() => setOpen(false)}
                  className="flex items-center gap-3 border-b border-hairline py-3.5 last:border-b-0"
                >
                  <span className="label tabular text-teal-bright">{s.index}</span>
                  <span className="font-sans text-sm font-medium text-offwhite">{s.label}</span>
                </a>
              ))}
              <div className="mt-5 flex items-center justify-between gap-4">
                <div className="flex gap-5">
                  {EXTERNAL_LINKS.map((l) => (
                    <a
                      key={l.label}
                      href={l.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={() => setOpen(false)}
                      className="label text-gray transition-colors hover:text-offwhite"
                    >
                      {l.label}
                    </a>
                  ))}
                </div>
                <SocialLinks />
              </div>
            </div>
          </motion.nav>
        ) : null}
      </AnimatePresence>
    </header>
  );
}
