"use client";

import { useState } from "react";
import { motion } from "framer-motion";

// Entity-relationship diagram: six labelled entity types radiating from a
// central hub. Thin teal lines, low-opacity dots. Inline SVG.
//
// Hovering (or tab-focusing) a node isolates its edge and label, which is the
// whole interaction — a state change, so framer owns it.

const NODES = [
  { label: "Country", x: 30, y: 30 },
  { label: "Organization", x: 110, y: 14 },
  { label: "Person", x: 178, y: 30 },
  { label: "Location", x: 178, y: 92 },
  { label: "Event", x: 110, y: 108 },
  { label: "Document", x: 30, y: 92 },
];

const HUB = { x: 104, y: 61 };

export function EntityGraph() {
  const [hover, setHover] = useState<string | null>(null);
  const dim = hover !== null;

  return (
    <svg
      viewBox="0 0 208 122"
      className="h-full w-full"
      fill="none"
      role="img"
      aria-label="Entity relationship graph: Country, Organization, Person, Location, Event and Document, each connected to a central hub"
    >
      {NODES.map((n) => (
        <motion.line
          key={`edge-${n.label}`}
          x1={HUB.x}
          y1={HUB.y}
          x2={n.x}
          y2={n.y}
          stroke="var(--color-teal)"
          strokeWidth="0.75"
          animate={{ strokeOpacity: dim ? (hover === n.label ? 1 : 0.12) : 0.45 }}
          transition={{ duration: 0.2 }}
        />
      ))}

      <motion.circle
        cx={HUB.x}
        cy={HUB.y}
        r="4"
        fill="var(--color-teal)"
        animate={{ fillOpacity: dim ? 1 : 0.85 }}
        transition={{ duration: 0.2 }}
      />
      <circle cx={HUB.x} cy={HUB.y} r="7" fill="var(--color-teal)" fillOpacity="0.15" />

      {NODES.map((n) => (
        <motion.text
          key={`label-${n.label}`}
          x={n.x}
          y={n.y}
          dominantBaseline="middle"
          textAnchor={n.x > HUB.x ? "start" : "end"}
          dx={n.x > HUB.x ? "6" : "-6"}
          fontSize="8"
          fontFamily="var(--font-jetbrains-mono), monospace"
          letterSpacing="1"
          animate={{
            fill: dim && hover !== n.label ? "var(--color-gray)" : "var(--color-offwhite)",
          }}
          transition={{ duration: 0.2 }}
        >
          {n.label.toUpperCase()}
        </motion.text>
      ))}

      {/* Hit targets last so they sit above the artwork, and focusable so the
          same isolation is reachable from the keyboard. */}
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
          <motion.circle
            cx={n.x}
            cy={n.y}
            r="2.6"
            fill="var(--color-offwhite)"
            animate={{ r: hover === n.label ? 3.6 : 2.6 }}
            transition={{ duration: 0.2 }}
          />
          <circle cx={n.x} cy={n.y} r="10" fill="transparent" />
        </g>
      ))}
    </svg>
  );
}
