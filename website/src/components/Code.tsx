import { classify, tokenize } from "@/lib/highlight";

/**
 * Renders a source string with generic token colouring.
 *
 * Exists so code samples live as plain strings in one place (lib/constants.ts)
 * instead of as ~50 lines of hand-coloured spans per sample.
 */
export function Code({ children, className = "" }: { children: string; className?: string }) {
  return (
    <code className={`font-mono text-[13px] leading-relaxed ${className}`}>
      {tokenize(children).map((token, i) => (
        <span key={i} className={classify(token.text, token.following)}>
          {token.text}
        </span>
      ))}
    </code>
  );
}
