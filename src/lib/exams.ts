// Exam-code helpers, shared by the build (homepage exam cards) and the client
// (browse-by-exam page, per-exam progress rings).

export const EXAM_NAMES: Record<string, string> = {
  SS24: "SoSe 2024",
  SS25: "SoSe 2025",
  WS26: "WiSe 2025/26",
};

const EXAM_CODE = /^(SS\d\d|WS\d\d)\b/;

/** Exam code from a source string ("WS26 P6.1" -> "WS26"), or null. */
export function examOf(source: string): string | null {
  const m = source.match(EXAM_CODE);
  return m ? m[1] : null;
}

/** The problem label without the exam code ("WS26 P6.1" -> "P6.1"). */
export function labelOf(source: string): string {
  return source.replace(/^(SS\d\d|WS\d\d)\s*/, "");
}
