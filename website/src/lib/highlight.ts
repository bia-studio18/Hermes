const KEYWORDS = new Set([
  "import",
  "as",
  "from",
  "def",
  "class",
  "return",
  "with",
  "for",
  "in",
  "not",
  "and",
  "or",
  "if",
  "else",
  "elif",
  "while",
  "try",
  "except",
  "raise",
  "pass",
  "is",
  "del",
  "assert",
  "None",
  "True",
  "False",
  "async",
  "await",
  "lambda",
  "yield",
]);

// Leading (?<=) keeps paths like hermes/api/entities.py out of the comment branch.
const TOKEN =
  /(?<=^|[\s(])(?:\/\/[^\n]*|#[^\n]*)|"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|\b\d+(?:\.\d+)?\b|\b[A-Za-z_]\w*\b/g;

export type Token = { text: string; following: string };

export function tokenize(src: string): Token[] {
  const out: Token[] = [];
  let last = 0;
  for (const match of src.matchAll(TOKEN)) {
    const start = match.index ?? 0;
    if (start > last) out.push({ text: src.slice(last, start), following: "" });
    const end = start + match[0].length;
    out.push({ text: match[0], following: src[end] ?? "" });
    last = end;
  }
  if (last < src.length) out.push({ text: src.slice(last), following: "" });
  return out;
}

export function classify(text: string, following: string): string {
  if (text.startsWith("//") || text.startsWith("#")) return "text-gray italic";
  if (text.startsWith('"') || text.startsWith("'")) return "text-[#b3a1e6]";
  if (/^\d/.test(text)) return "text-orange-300";
  if (KEYWORDS.has(text)) return "text-teal-bright";
  // an identifier immediately called is a function
  if (following === "(") return "text-offwhite";
  return "text-gray-bright";
}
