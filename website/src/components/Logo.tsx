type LogoMarkProps = {
  className?: string;
};

export function LogoMark({ className }: LogoMarkProps) {
  return (
    <svg
      viewBox="0 0 64 44"
      fill="none"
      role="img"
      aria-hidden="true"
      className={className}
    >
      <path
        d="M8 6 H20 V18 H44 V26 H20 V38 H12 Z"
        fill="var(--color-offwhite)"
      />
      <path
        d="M48 6 H56 V38 H44 V26 H20 V18 H44 Z"
        fill="var(--color-teal)"
      />
    </svg>
  );
}

export function LogoLockup({ className }: LogoMarkProps) {
  return (
    <span className={`inline-flex items-center gap-2.5 ${className ?? ""}`}>
      <LogoMark className="h-6 w-9 shrink-0" />
      <span className="font-sans text-sm font-bold uppercase leading-none tracking-[0.28em] text-offwhite">
        Hermes
      </span>
    </span>
  );
}

export function LogoIcon({
  className,
  variant = "dark",
}: LogoMarkProps & { variant?: "dark" | "light" }) {
  const dark = variant === "dark";
  return (
    <svg
      viewBox="0 0 64 44"
      fill="none"
      role="img"
      aria-hidden="true"
      className={className}
    >
      <rect
        x="0.5"
        y="-6.5"
        width="63"
        height="57"
        rx="7"
        fill={dark ? "var(--color-midnight)" : "var(--color-offwhite)"}
        stroke={dark ? "rgba(245,245,242,0.15)" : "rgba(11,13,15,0.12)"}
        strokeWidth="1"
      />
      <g transform="translate(12 4)">
        <path
          d="M8 6 H20 V18 H44 V26 H20 V38 H12 Z"
          fill={dark ? "var(--color-offwhite)" : "var(--color-teal)"}
        />
        <path
          d="M48 6 H56 V38 H44 V26 H20 V18 H44 Z"
          fill={dark ? "var(--color-teal)" : "var(--color-offwhite)"}
        />
      </g>
    </svg>
  );
}