"use client";

import { useState } from "react";

const NODES = [
  { label: "Country", x: 30, y: 30 },
  { label: "Organization", x: 110, y: 14 },
  { label: "Person", x: 178, y: 30 },
  { label: "Location", x: 178, y: 92 },
  { label: "Event", x: 110, y: 108 },
  { label: "Document", x: 30, y: 92 },
];

const HUB = { x: 104, y: 61 };

const EDGE = "transition-[stroke-opacity] duration-200";
const FILL = "transition-[fill] duration-200";
const FADE = "transition-opacity duration-200";

export function EntityGraph() {
  const [hover, setHover] = useState<string | null>(null);
  const dim = hover !== null;
  const lit = (label: string) => hover === label;

  return (
    <svg
      viewBox="0 0 208 122"
      className="h-full w-full"
      fill="none"
      role="img"
      aria-label="Entity relationship graph: Country, Organization, Person, Location, Event and Document, each connected to a central hub"
    >
      {NODES.map((n) => (
        <line
          key={`edge-${n.label}`}
          x1={HUB.x}
          y1={HUB.y}
          x2={n.x}
          y2={n.y}
          stroke="var(--color-teal)"
          strokeWidth="0.75"
          style={{ strokeOpacity: dim ? (lit(n.label) ? 1 : 0.12) : 0.45 }}
          className={EDGE}
        />
      ))}

      <circle
        cx={HUB.x}
        cy={HUB.y}
        r="4"
        fill="var(--color-teal)"
        style={{ fillOpacity: dim ? 1 : 0.85 }}
        className={FADE}
      />
      <circle cx={HUB.x} cy={HUB.y} r="7" fill="var(--color-teal)" fillOpacity="0.15" />

      {NODES.map((n) => (
        <text
          key={`label-${n.label}`}
          x={n.x}
          y={n.y}
          dominantBaseline="middle"
          textAnchor={n.x > HUB.x ? "start" : "end"}
          dx={n.x > HUB.x ? "6" : "-6"}
          fontSize="8"
          fontFamily="var(--font-jetbrains-mono), monospace"
          letterSpacing="1"
          style={{
            fill: dim && !lit(n.label) ? "var(--color-gray)" : "var(--color-offwhite)",
          }}
          className={FILL}
        >
          {n.label.toUpperCase()}
        </text>
      ))}

      {NODES.map((n) => (
        <g
          key={`hit-${n.label}`}
          tabIndex={0}
          role="button"
          aria-label={`Isolate ${n.label}`}
          onMouseEnter={() => setHover(n.label)}
          onMouseLeave={() => setHover(null)}
          onFocus={() => setHover(n.label)}
          onBlur={() => setHover(null)}
          className="cursor-pointer outline-none"
        >
          <circle cx={n.x} cy={n.y} r="10" fill="transparent" />
          <circle
            cx={n.x}
            cy={n.y}
            r="2.6"
            fill="var(--color-offwhite)"
            style={{ opacity: dim && !lit(n.label) ? 0.28 : 1 }}
            className={`origin-center transition duration-200 [transform-box:fill-box] ${
              lit(n.label) ? "scale-125" : "scale-100"
            }`}
          />
        </g>
      ))}
    </svg>
  );
}
