# I2DL Exam Q&A — TUM IN2346

A closed-book revision deck for **Introduction to Deep Learning (IN2346)** at TU München.
Every problem from 12 past exams + the official course summary, classified by
**chapter → knowledge point**, sorted by **exam frequency**, and answered from the
**official solutions**. Interactive, searchable, mobile-friendly, formulas in KaTeX.

🔗 **Live:** https://c0nsTantin77.github.io/i2dl-exam-qa/

## Contents
**512 questions** across 7 chapters and 43 knowledge points (every point also has an AI practice question):
Machine Learning Basics (80) · Neural Networks (96) · Convolutions (67) · Optimization (127) ·
Popular Architectures (65) · RNNs & Transformers (57) · Appendix: Matrix Calculus (20).

## Features
- **Site-wide search** + per-question **concept tags** to review a theme across chapters.
- **Interactive multiple-choice**: pick → check → reveal ✅/❌, an explicit "Correct: A, C" line, answer + analysis.
- **Frequency-first** ordering (🔥 badges); every question **source-tagged** like `SS22 3.1`.
- KaTeX formulas, collapsible answers, mobile-optimized.

## Recent updates
- **2026-06-08** — Chapter navigation revamp: the contents menu is now a top-bar **"you are here" pill** (shows your current section, opens a floating popover that's **full-width on mobile**); assets are cache-busted so updates appear immediately.
- **2026-06-07** — ✨ **You're never studying alone!** A live counter at the top of every page shows how many fellow students are grinding through I2DL right now — look up, someone's in the trenches with you. 💪
- **2026-06-07** — Chapter-page readability: **numbered topics** (4.2) **& questions** (4.2.1), an **always-on left contents panel** that highlights your current section as you scroll, and tidier multi-part **answer/summary line breaks**.
- **2026-06-07** — Mined SS20/SS21/SS22/SS24: +87 questions (now **512**); **all 12 exams covered, overall 90%** (SS21 100%, SS22 98%, SS20 91%).
- **2026-06-07** — Mined WS22/WS21/WS26/WS23/SS23/Mock: +144 questions; overall exam coverage **41%→70%** (WS22 95%, SS23 93%, WS26 89%).
- **2026-06-06** — Full WS24 (Winter 2024) endterm mined: +41 questions, WS24 coverage 4%→98%, overall 31%→41%.
- **2026-06-06** — Sign in with Google to sync progress (reviewed / wrong book / notes) across devices.
- **2026-06-06** — Study tools: mark Reviewed, wrong book, per-question notes, spaced-repetition review, progress dashboard.
- **2026-06-06** — Browse by exam paper (`SS23 6.1` jumps to a question), concept-tag pages, AI multiple-choice.

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
