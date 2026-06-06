# I2DL Exam Q&A — TUM IN2346

A static, closed-book revision deck for **Introduction to Deep Learning (IN2346)** at TUM.
Every problem from the past exams + the official course summary is extracted, classified by
**chapter → knowledge point**, sorted by **exam frequency**, and answered with the **official
sample solutions** (scoring points merged for variant phrasings). Formulas render with KaTeX.

🔗 **Live site:** https://c0nsTantin77.github.io/i2dl-exam-qa/

## Status
**All 7 chapters complete** — 188 questions across 43 knowledge points (every knowledge point includes AI practice), extracted from 12 past exams + the course summary. Every source citation is auto-verified against the original exam text (`tools/check_sources.py`); `tools/coverage_report.py` writes a per-exam coverage table to [COVERAGE.md](COVERAGE.md).

| Ch | Topic | Questions |
|----|-------|-----------|
| I | Machine Learning Basics | 42 |
| II | Neural Networks | 34 |
| III | Convolutions | 22 |
| IV | Optimization | 38 |
| V | Popular Architectures | 26 |
| VI | RNNs & Transformers | 16 |
| VII | Appendix: Matrix Calculus | 10 |

## Features
- **Index hub → per-chapter pages** with a **site-wide search** across all questions (deep-links straight to the answer).
- **Frequency-first ordering** (enforced at render time) with 🔥 badges; **source tags** like `SS22 3.1` (= SoSe 2022, problem 3.1).
- **Interactive multiple-choice**: pick options → check → reveal ✅/❌ marks, an explicit "Correct: A, C" line, the answer, and analysis.
- **AI-generated** practice questions on **every** knowledge point, clearly labelled.
- **KaTeX** LaTeX rendering (auto-verified); per-chapter **search** and **MC/Open/AI** filters; collapsible answers.
- **Mobile-optimized**: collapsible TOC, large tap targets, back-to-top, no horizontal scroll.

## Sources
| Tag | Exam |
|-----|------|
| SS20 … SS25 | Sommersemester endterms 2020–2025 |
| WS21 … WS26 | Wintersemester endterms 2021–2026 |
| Mock | Mock exam (SoSe 2020) |
| Summary I.3 | Per-chapter questions from *Summary of the lecture I2DL* |

## Build
Pure Python stdlib — no Node, no dependencies.

```bash
python build.py            # regenerate index.html + chapters/*.html from data/*.json
python tools/check_math.py # validate KaTeX delimiters / macros
```

Content lives in `data/*.json`; `build.py` is the generator. To add a chapter, drop a
`data/chXX_*.json` file and flip its `status` to `ready` in `data/chapters.json`.

`python tools/check_sources.py` cross-checks every `SSyy x.y` citation against the original
exam text, so a wrong reference (e.g. `SS20 P6b` vs `P7b`) is caught automatically.

## Deploy (GitHub Pages)
One-time GitHub login (only you can do this — GitHub security):

```powershell
& "C:\Program Files\GitHub CLI\gh.exe" auth login   # GitHub.com → HTTPS → web browser
```

Then publish (creates the repo, pushes, enables Pages, prints the URL):

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy.ps1
```

---
*For personal revision. Answers follow the official I2DL sample solutions; AI-generated items are marked and intended only as extra practice.*
