import { LogoMark } from "@/components/Logo";
import { SocialLinks } from "@/components/SocialLinks";

export function Footer() {
  return (
    <footer className="border-t border-white/[0.06] bg-midnight">
      <div className="mx-auto max-w-6xl px-5 py-12 sm:px-8">
        <div className="flex flex-col items-start gap-6 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <LogoMark className="h-6 w-9 shrink-0" />
            <div>
              <p className="font-sans text-sm font-bold uppercase leading-none tracking-[0.28em] text-offwhite">
                Hermes
              </p>
              <p className="mt-1.5 font-mono text-[10px] uppercase tracking-[0.22em] text-gray">
                DATA INFRASTRUCTURE
              </p>
            </div>
          </div>

          <SocialLinks />
        </div>

        <div className="mt-10 border-t border-white/[0.06] pt-6">
          <p className="text-xs text-gray">
            &copy; {new Date().getFullYear()} Hermes. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}