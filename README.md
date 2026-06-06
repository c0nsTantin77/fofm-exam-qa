# I2DL Exam Q&A — TUM IN2346

A closed-book revision deck for **Introduction to Deep Learning (IN2346)** at TU München.
Every problem from 12 past exams + the official course summary, classified by
**chapter → knowledge point**, sorted by **exam frequency**, and answered from the
**official solutions**. Interactive, searchable, mobile-friendly, formulas in KaTeX.

🔗 **Live:** https://c0nsTantin77.github.io/i2dl-exam-qa/

## Contents
**233 questions** across 7 chapters and 43 knowledge points (every point also has an AI practice question):
Machine Learning Basics (47) · Neural Networks (40) · Convolutions (29) · Optimization (47) ·
Popular Architectures (31) · RNNs & Transformers (26) · Appendix: Matrix Calculus (13).

## Features
- **Site-wide search** + per-question **concept tags** to review a theme across chapters.
- **Interactive multiple-choice**: pick → check → reveal ✅/❌, an explicit "Correct: A, C" line, answer + analysis.
- **Frequency-first** ordering (🔥 badges); every question **source-tagged** like `SS22 3.1`.
- KaTeX formulas, collapsible answers, mobile-optimized.

## Recent updates
- **2026-06-06** — Concept tags on every question + a tag index page (review a theme across chapters).
- **2026-06-06** — Coverage pass: +45 questions from SS25 & WS23 → **233 questions**.
- **2026-06-05** — Interactive multiple-choice, site-wide search, mobile-friendly redesign.

## Develop
Pure Python stdlib — content lives in `data/*.json`, `build.py` generates the site.

```bash
python build.py                  # regenerate index.html + chapters/*.html + search-index.json
python tools/check_sources.py    # verify every SSyy x.y citation against the exam text
python tools/check_math.py       # validate KaTeX
python tools/coverage_report.py  # per-exam coverage → COVERAGE.md
```

Deploy with `deploy.ps1` (needs a one-time `gh auth login`).

---
*For personal revision. Answers follow the official I2DL sample solutions; AI-generated items are marked.*
