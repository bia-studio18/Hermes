// Small entity-relationship node diagram: 6 labeled entity types radiating
// from a central hub. Thin teal lines, low-opacity dots. Inline SVG.

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
  return (
    <svg
      viewBox="0 0 208 122"
      className="h-full w-full"
      fill="none"
      role="img"
      aria-label="Entity relationship graph: Country, Organization, Person, Location, Event, Document connected to a central hub"
    >
      {/* Connecting lines from central hub */}
      {NODES.map((n) => (
        <line
          key={`edge-${n.label}`}
          x1={HUB.x}
          y1={HUB.y}
          x2={n.x}
          y2={n.y}
          stroke="var(--color-teal)"
          strokeOpacity="0.5"
          strokeWidth="0.75"
        />
      ))}
      {/* Central hub */}
      <circle cx={HUB.x} cy={HUB.y} r="4" fill="var(--color-teal)" />
      <circle cx={HUB.x} cy={HUB.y} r="7" fill="var(--color-teal)" fillOpacity="0.15" />
      {/* Nodes */}
      {NODES.map((n) => (
        <circle key={`node-${n.label}`} cx={n.x} cy={n.y} r="2.6" fill="var(--color-offwhite)" />
      ))}
      {/* Labels */}
      {NODES.map((n) => (
        <text
          key={`label-${n.label}`}
          x={n.x}
          y={n.y}
          dominantBaseline="middle"
          textAnchor={n.x > HUB.x ? "start" : "end"}
          dx={n.x > HUB.x ? "6" : "-6"}
          fill="var(--color-gray-bright)"
          fontSize="8"
          fontFamily="var(--font-jetbrains-mono), monospace"
          letterSpacing="1"
        >
          {n.label.toUpperCase()}
        </text>
      ))}
    </svg>
  );
}