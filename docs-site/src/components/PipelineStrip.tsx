import { ChevronRight } from "lucide-react";

const STEPS = ["ACQUIRE", "PARSE", "NORMALIZE", "VALIDATE", "STORE", "SERVE"];

export function PipelineStrip() {
  return (
    <div className="flex flex-wrap items-center justify-center gap-3 font-mono text-xs font-medium uppercase tracking-widest text-gray-bright">
      {STEPS.map((step, i) => (
        <span key={step} className="flex items-center gap-3">
          <span className="whitespace-nowrap">{step}</span>
          {i < STEPS.length - 1 && (
            <ChevronRight className="h-3.5 w-3.5 text-teal" aria-hidden="true" />
          )}
        </span>
      ))}
    </div>
  );
}