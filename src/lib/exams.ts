// Exam-code helpers, shared by the build (homepage exam cards) and the client
// (browse-by-exam page, per-exam progress rings).

export const EXAM_NAMES: Record<string, string> = {
  SS20: "SoSe 2020",
  SS21: "SoSe 2021",
  SS22: "SoSe 2022",
  SS23: "SoSe 2023",
  SS24: "SoSe 2024",
  SS25: "SoSe 2025",
  WS21: "WiSe 2021/22",
  WS22: "WiSe 2022/23",
  WS23: "WiSe 2023/24",
  WS24: "WiSe 2024/25",
  WS26: "WiSe 2025/26",
  Mock: "Mock exam",
};

const EXAM_CODE = /^(SS\d\d|WS\d\d|Mock)\b/;

/** Exam code from a source string ("SS23 6.1" -> "SS23"), or null. */
export function examOf(source: string): string | null {
  const m = source.match(EXAM_CODE);
  return m ? m[1] : null;
}

/** The problem label without the exam code ("SS23 6.1" -> "6.1"). */
export function labelOf(source: string): string {
  return source.replace(/^(SS\d\d|WS\d\d|Mock)\s*/, "");
}
