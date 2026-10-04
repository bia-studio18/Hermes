import { classify, tokenize } from "@/lib/highlight";

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
