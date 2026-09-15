// Decorative world-map / node-grid texture for the hero background.
// Sparse teal dots and thin connecting lines at low opacity — suggesting
// global data acquisition. Built as inline SVG, no external images.

type TextureNode = {
  x: number;
  y: number;
};

const NODES: TextureNode[] = [
  { x: 8, y: 22 },
  { x: 22, y: 16 },
  { x: 34, y: 30 },
  { x: 52, y: 14 },
  { x: 66, y: 26 },
  { x: 84, y: 18 },
  { x: 93, y: 34 },
  { x: 14, y: 58 },
  { x: 31, y: 52 },
  { x: 46, y: 66 },
  { x: 62, y: 54 },
  { x: 78, y: 70 },
  { x: 90, y: 58 },
  { x: 48, y: 84 },
  { x: 72, y: 88 },
  { x: 26, y: 82 },
];

// Pairs of connected nodes → thin lines
const LINES: [number, number][] = [
  [0, 1],
  [1, 2],
  [2, 4],
  [3, 4],
  [4, 5],
  [5, 6],
  [7, 8],
  [8, 10],
  [9, 10],
  [10, 12],
  [11, 12],
  [11, 14],
  [2, 9],
  [4, 10],
];

export function MapTexture() {
  return (
    <svg
      viewBox="0 0 100 100"
      className="pointer-events-none h-full w-full opacity-40"
      preserveAspectRatio="xMidYMid slice"
      aria-hidden="true"
    >
      {LINES.map(([a, b], i) => (
        <line
          key={`line-${i}`}
          x1={NODES[a].x}
          y1={NODES[a].y}
          x2={NODES[b].x}
          y2={NODES[b].y}
          stroke="var(--color-teal)"
          strokeWidth="0.25"
          strokeOpacity="0.35"
        />
      ))}
      {NODES.map((n, i) => (
        <circle
          key={`node-${i}`}
          cx={n.x}
          cy={n.y}
          r="0.7"
          fill="var(--color-teal)"
          fillOpacity="0.5"
        />
      ))}
      {/* Sparse extra accent squares */}
      <rect x="6" y="40" width="1.2" height="1.2" fill="var(--color-teal)" fillOpacity="0.4" />
      <rect x="74" y="44" width="1.2" height="1.2" fill="var(--color-teal)" fillOpacity="0.4" />
      <rect x="40" y="8" width="1.2" height="1.2" fill="var(--color-teal)" fillOpacity="0.4" />
      <rect x="58" y="78" width="1.2" height="1.2" fill="var(--color-teal)" fillOpacity="0.4" />
    </svg>
  );
}