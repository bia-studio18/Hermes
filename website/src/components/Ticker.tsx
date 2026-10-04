import { TICKER } from "@/lib/constants";

export function Ticker() {
  return (
    <div className="ticker border-y border-hairline bg-panel">
      <div className="ticker-track py-3.5">
        {[0, 1].map((copy) => (
          <div key={copy} className="flex shrink-0 items-center" aria-hidden={copy === 1}>
            {TICKER.map((name) => (
              <span key={name} className="label flex items-center gap-6 px-6 text-gray">
                <span className="text-gray-bright">{name}</span>
                <span className="h-1 w-1 rotate-45 bg-teal" aria-hidden="true" />
              </span>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
