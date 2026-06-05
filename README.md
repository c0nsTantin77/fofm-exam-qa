# I2DL Exam Q&A — TUM IN2346

A static, closed-book revision deck for **Introduction to Deep Learning (IN2346)** at TUM.
Every problem from the past exams + the official course summary is extracted, classified by
**chapter → knowledge point**, sorted by **exam frequency**, and answered with the **official
sample solutions** (scoring points merged for variant phrasings). Formulas render with KaTeX.

🔗 **Live site:** https://c0nsTantin77.github.io/i2dl-exam-qa/

## Status
Draft build — **Chapter I: Machine Learning Basics** is complete (39 questions across 9 knowledge points). Remaining chapters (II–VII) are scaffolded and marked *coming soon*.

## Features
- **Index hub → per-chapter pages** (matches a clean, mobile-friendly review layout).
- **Frequency-first ordering** with ★ badges; **source tags** like `SS22 3.1` (= SoSe 2022, problem 3.1).
- **Multiple-choice** answers marked ✅ / ❌ with extended-memory notes.
- **AI-generated** practice questions per topic, clearly labelled.
- **KaTeX** LaTeX rendering; live **search** and **MC/Open/AI** filters; collapsible answers.

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

---
*For personal revision. Answers follow the official I2DL sample solutions; AI-generated items are marked and intended only as extra practice.*
