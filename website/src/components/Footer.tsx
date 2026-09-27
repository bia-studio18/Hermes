import { LogoMark } from "@/components/Logo";
import { SocialLinks } from "@/components/SocialLinks";
import { EXTERNAL_LINKS, SECTIONS } from "@/lib/constants";

export function Footer() {
  return (
    <footer className="border-t border-hairline bg-midnight">
      <div className="shell py-14">
        <div className="grid grid-cols-2 gap-10 sm:grid-cols-4">
          <div className="col-span-2 sm:col-span-1">
            <div className="flex items-center gap-3">
              <LogoMark className="h-6 w-9 shrink-0" />
              <div>
                <p className="font-sans text-sm font-bold uppercase leading-none tracking-[0.28em] text-offwhite">
                  Hermes
                </p>
                <p className="label mt-2 text-gray">Data infrastructure</p>
              </div>
            </div>
            <p className="mt-5 max-w-xs text-sm leading-relaxed text-gray-bright">
              Acquire, normalize, validate and serve data through one interface.
            </p>
          </div>

          <nav aria-label="Sections">
            <p className="label text-gray">Sections</p>
            <ul className="mt-4 space-y-2.5">
              {SECTIONS.map((s) => (
                <li key={s.id}>
                  <a
                    href={`#${s.id}`}
                    className="text-sm text-gray-bright transition-colors duration-150 hover:text-teal-bright"
                  >
                    {s.label}
                  </a>
                </li>
              ))}
            </ul>
          </nav>

          <nav aria-label="Project">
            <p className="label text-gray">Project</p>
            <ul className="mt-4 space-y-2.5">
              {EXTERNAL_LINKS.map((l) => (
                <li key={l.label}>
                  <a
                    href={l.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-gray-bright transition-colors duration-150 hover:text-teal-bright"
                  >
                    {l.label}
                  </a>
                </li>
              ))}
              <li>
                <a
                  href="#main-content"
                  className="text-sm text-gray-bright transition-colors duration-150 hover:text-teal-bright"
                >
                  Back to top
                </a>
              </li>
            </ul>
          </nav>

          <div>
            <p className="label text-gray">Elsewhere</p>
            <div className="mt-4">
              <SocialLinks />
            </div>
          </div>
        </div>

        <div className="mt-12 flex flex-col gap-3 border-t border-hairline pt-6 sm:flex-row sm:items-center sm:justify-between">
          <p className="label text-gray">
            &copy; {new Date().getFullYear()} Hermes. All rights reserved.
          </p>
          <p className="label flex items-center gap-2 text-gray">
            <span className="pulse-dot" aria-hidden="true" />
            All systems operational
          </p>
        </div>
      </div>
    </footer>
  );
}
