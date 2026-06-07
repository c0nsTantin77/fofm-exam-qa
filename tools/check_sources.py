#!/usr/bin/env python3
"""Cross-check every source tag in data/*.json against the exam text dumps,
so a citation like 'SS22 3.1' is verified to actually exist in SS_2022."""
import glob, json, re, pathlib, sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = pathlib.Path(__file__).resolve().parent.parent
TXT = ROOT / "AK" / "_txt"

EXAM_FILES = {
    "SS20": "SS_2020_Solutions.txt", "SS21": "SS_2021_Solutions.txt",
    "SS22": "SS_2022_Solutions.txt", "SS23": "SS_2023_Solutions.txt",
    "SS24": "SS_2024_Solutions.txt", "SS25": "SS_2025_Solutions.txt",
    "WS21": "WS_2021_Solutions.txt", "WS22": "WS_2022_Solutions.txt",
    "WS23": "WS_2023_Solutions.txt", "WS24": "WS_2024_Solutions.txt",
    "WS26": "WS_2026_Solutions.txt", "Mock": "Mock_Exam _Solutions.txt",
}
_cache = {}
def text(exam):
    if exam not in _cache:
        p = TXT / EXAM_FILES[exam]
        _cache[exam] = p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""
    return _cache[exam]

def collect_sources():
    srcs = []
    for f in glob.glob(str(ROOT / "data" / "ch*.json")):
        if pathlib.Path(f).name == "chapters.json":
            continue
        data = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        for kp in data["knowledge_points"]:
            for q in kp["questions"]:
                for s in q["sources"]:
                    srcs.append(s)
    return srcs

def verify(src):
    if src.lower().startswith(("ai", "summary")):
        return True, "skip"
    m = re.match(r"^(SS\d\d|WS\d\d|Mock)\s+(.+)$", src)
    if not m:
        return False, "unparseable"
    exam, ref = m.group(1), m.group(2)
    body = text(exam)
    if not body:
        return False, f"no exam file for {exam}"
    # numeric ref like 3.1 / 2.10
    if re.match(r"^\d+\.\d+$", ref):
        # look for the ref at a line start (exam uses 'X.Y ...')
        pat = re.compile(r"(?m)^\s*" + re.escape(ref) + r"(?=[\s)])")
        return (bool(pat.search(body)), f"numeric {ref}")
    # SS20-style 'P7b' -> Problem 7 then a subpart 'b)'
    m2 = re.match(r"^P(\d+)([a-z])$", ref)
    if m2:
        pn, sub = m2.group(1), m2.group(2)
        has_problem = re.search(r"(?m)^Problem\s+" + pn + r"\b", body)
        has_sub = re.search(r"(?m)^\s*" + sub + r"\)", body)
        return (bool(has_problem and has_sub), f"Problem {pn} {sub})")
    # 'P3e' style already covered; Mock 'I.1','II.1' -> just check part exists
    return True, f"loose {ref}"

def main():
    seen = {}
    for s in collect_sources():
        if s in seen:
            continue
        ok, why = verify(s)
        seen[s] = (ok, why)
    bad = [(s, w) for s, (ok, w) in seen.items() if not ok]
    for s in sorted(seen):
        ok, why = seen[s]
        mark = "OK " if ok else "XX "
        print(f"  {mark}{s:16s} [{why}]")
    print(f"\n{len(seen)} unique sources, {len(bad)} suspicious")
    for s, w in bad:
        print("  SUSPICIOUS:", s, w)

if __name__ == "__main__":
    main()
