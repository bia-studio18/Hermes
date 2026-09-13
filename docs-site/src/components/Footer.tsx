import Link from "next/link";
import { Plant, WobbleCircle } from "./Doodle";
import { Logo } from "./Logo";

export function Footer() {
  const cols = [
    {
      title: "Docs",
      links: [
        { label: "Overview", href: "/docs/overview" },
        { label: "Quickstart", href: "/docs/quickstart" },
        { label: "Connectors", href: "/docs/connectors" },
        { label: "Features", href: "/docs/features" },
        { label: "API Reference", href: "/docs/api-reference" },
      ],
    },
    {
      title: "Project",
      links: [
        { label: "Roadmap", href: "/docs/roadmap" },
        { label: "GitHub", href: "https://github.com/ryomenhaider/Hermes" },
        { label: "PyPI", href: "https://pypi.org/project/hermes-plt/" },
        { label: "License", href: "/docs/overview#license" },
      ],
    },
    {
      title: "Community",
      links: [
        { label: "Join Discord", href: "https://discord.gg/KrxwaR3Uu" },
        { label: "GitHub Repo", href: "https://github.com/ryomenhaider/Hermes" },
        { label: "Report an issue", href: "https://github.com/ryomenhaider/Hermes/issues" },
      ],
    },
  ];

  return (
    <footer className="relative mt-auto overflow-hidden border-t border-line/70 bg-cream-soft">
      <div className="pointer-events-none absolute -right-10 -top-8 opacity-60">
        <Plant className="h-40 w-32" color="#ff4328" />
      </div>
      <div className="pointer-events-none absolute -left-6 top-10 opacity-40">
        <WobbleCircle className="h-28 w-28" color="#ff4328" />
      </div>

      <div className="relative mx-auto max-w-6xl px-4 py-12 sm:px-6 sm:py-14">
        <div className="grid grid-cols-2 gap-8 sm:gap-10 lg:grid-cols-[1.5fr_1fr_1fr_1fr] lg:gap-10">
          <div className="col-span-2 lg:col-span-1">
            <div className="mb-4">
              <Logo withWordmark={false} />
            </div>
            <p className="max-w-xs font-body text-sm leading-relaxed text-ink">Acquire, validate,
              normalize and serve intelligence datasets with provenance baked in.
            </p>
          </div>

          {cols.map((col) => (
            <div key={col.title}>
              <h3 className="font-heading text-base font-bold">{col.title}</h3>
              <ul className="mt-4 space-y-3">
                {col.links.map((l) => (
                  <li key={l.label}>
                    <Link
                      href={l.href}
                      target={l.href.startsWith("http") ? "_blank" : undefined}
                      rel={l.href.startsWith("http") ? "noopener noreferrer" : undefined}
                      className="font-body text-sm text-ink-soft transition-colors hover:text-accent"
                    >
                      {l.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 flex flex-col items-start justify-between gap-4 border-t border-line/70 pt-6 sm:flex-row sm:items-center">
          <p className="font-body text-xs text-ink-soft">
            Elastic License 2.0 (ELv2) · Built by Haider Ali
          </p>
          <div className="flex flex-wrap items-center gap-3">
            <a
              href="https://discord.gg/KrxwaR3Uu"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-full border border-line px-4 py-1.5 font-body text-xs font-semibold text-black transition-colors hover:border-accent hover:text-accent"
            >
              <DiscordIcon className="h-3.5 w-3.5" />
              Join Discord
            </a>
            <a
              href="https://github.com/ryomenhaider/Hermes"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-full border border-line px-4 py-1.5 font-body text-xs font-semibold text-black transition-colors hover:border-accent hover:text-accent"
            >
              <GithubIcon className="h-3.5 w-3.5" />
              GitHub
            </a>
            <a
              href="https://pypi.org/project/hermes-plt/"
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-full border border-line px-4 py-1.5 font-mono text-xs font-medium text-black transition-colors hover:border-accent hover:text-accent"
            >
              pip install hermes-plt
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}

function DiscordIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M20.317 4.37a19.79 19.79 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z" />
    </svg>
  );
}

function GithubIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12" />
    </svg>
  );
}
