"use client";

import { useEffect, useState } from "react";

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
        <span className="label text-gray">Data infrastructure for the modern world</span>

        <div className="label hidden items-center gap-6 text-gray md:flex">
          <span>Rust core</span>
          <span className="text-gray/50" aria-hidden="true">
            /
          </span>
          <span>Python 3.11</span>
          <span className="text-gray/50" aria-hidden="true">
            /
          </span>
          <span>v0.1.0</span>
        </div>

        <div className="label tabular flex items-center gap-2 text-gray">
          <span className="hidden sm:inline">UTC</span>
          <span className="text-gray-bright">{clock}</span>
        </div>
      </div>
    </div>
  );
}
