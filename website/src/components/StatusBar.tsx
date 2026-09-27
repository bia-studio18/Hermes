"use client";

import { useEffect, useState } from "react";

/**
 * Thin instrument strip above the header. Reads like the status bar of an
 * internal tool rather than a marketing band.
 *
 * The clock only starts after mount, so the server-rendered markup and the
 * first client render agree.
 */
export function StatusBar() {
  const [clock, setClock] = useState("--:--:--");

  useEffect(() => {
    const tick = () => setClock(new Date().toISOString().slice(11, 19));
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="border-b border-hairline bg-midnight">
      <div className="shell flex h-8 items-center justify-between gap-4">
        <div className="flex items-center gap-2.5">
          <span className="pulse-dot" aria-hidden="true" />
          <span className="label text-gray-bright">All systems operational</span>
        </div>

        <div className="label hidden items-center gap-6 text-gray md:flex">
          <span>Rust core</span>
          <span className="text-gray/50" aria-hidden="true">
            /
          </span>
          <span>Python 3.11</span>
          <span className="text-gray/50" aria-hidden="true">
            /
          </span>
          <span className="text-gray">v0.1.0</span>
        </div>

        <div className="label tabular flex items-center gap-2 text-gray">
          <span className="hidden sm:inline">UTC</span>
          <span className="text-gray-bright">{clock}</span>
        </div>
      </div>
    </div>
  );
}
