#!/usr/bin/env python3
"""
Static-site generator for the I2DL Exam Q&A review.

Reads data/chapters.json (manifest) and data/<chapter>.json (content),
emits index.html (hub) and chapters/<id>.html (one page per ready chapter).

Formulas are written inline as $...$ / $$...$$ and rendered client-side by
KaTeX auto-render. Zero build dependencies beyond the Python stdlib.
"""
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).parent
DATA = ROOT / "data"
CHAPTERS_DIR = ROOT / "chapters"

# ---------------------------------------------------------------- helpers

def esc(s: str) -> str:
    """HTML-escape text but keep $...$ math and `code` for later passes."""
    return html.escape(s, quote=False)

def md_inline(s: str) -> str:
    """Tiny markdown: **bold**, `code`, and newlines. Escapes HTML first,
    but leaves $...$ math spans untouched for KaTeX."""
    # protect math spans
    spans = []
    def stash(m):
        spans.append(m.group(0))
        return f"\x00{len(spans)-1}\x00"
    import re
    s = re.sub(r"\$\$.*?\$\$|\$.*?\$", stash, s, flags=re.DOTALL)
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`([^`]+?)`", r"<code>\1</code>", s)
    s = s.replace("\n", "<br>")
    # restore math
    def pop(m):
        return spans[int(m.group(1))]
    s = re.sub(r"\x00(\d+)\x00", pop, s)
    return s

def md_block(s: str) -> str:
    """Render a multi-line answer: fenced ```code``` blocks + paragraphs."""
    import re
    out, i = [], 0
    for m in re.finditer(r"```(?:\w+)?\n(.*?)```", s, flags=re.DOTALL):
        pre = s[i:m.start()].strip()
        if pre:
            out.append(f"<p>{md_inline(pre)}</p>")
        code = html.escape(m.group(1), quote=False)
        out.append(f"<pre class='code'>{code}</pre>")
        i = m.end()
    rest = s[i:].strip()
    if rest:
        out.append(f"<p>{md_inline(rest)}</p>")
    return "\n".join(out)

def freq_badge(f: int) -> str:
    if f >= 6:
        cls, lab = "freq-hot", f"🔥 {f}×"
    elif f >= 3:
        cls, lab = "freq-mid", f"🔥 {f}×"
    elif f >= 1:
        cls, lab = "freq-low", f"{f}×"
    else:
        cls, lab = "freq-ai", "practice"
    return f"<span class='badge {cls}' title='Times this point appears across exams'>{lab}</span>"

TUM_LOGO = "<img class='tum-logo' src='{base}assets/tum.svg' alt='TUM' width='44' height='23'>"

EXAM_NAMES = {
    "SS20": "SoSe 2020", "SS21": "SoSe 2021", "SS22": "SoSe 2022",
    "SS23": "SoSe 2023", "SS24": "SoSe 2024", "SS25": "SoSe 2025",
    "WS21": "WiSe 2021/22", "WS22": "WiSe 2022/23", "WS23": "WiSe 2023/24",
    "WS24": "WiSe 2024/25", "WS26": "WiSe 2025/26", "Mock": "Mock exam",
}

def site_footer(exams, *, base) -> str:
    rows = "".join(
        f"<li><span class='src'>{esc(e)}</span> {esc(EXAM_NAMES.get(e, e))} endterm</li>"
        for e in exams
    )
    return f"""
<footer class="sources">
  <div class="sources-inner">
    {TUM_LOGO.format(base=base)}
    <div class="sources-cols">
      <div>
        <h4>Sources</h4>
        <ul class="src-list">
          {rows}
          <li><span class='src'>Summary</span> <em>Summary of the lecture I2DL</em> (per-chapter questions)</li>
        </ul>
      </div>
      <div>
        <h4>About</h4>
        <p>Revision deck for <b>Introduction to Deep Learning (IN2346)</b>, TU&nbsp;München.
        Answers follow the <b>official sample solutions</b>; for variant phrasings the scoring
        points are merged. Items tagged <span class="src-ai">AI-generated</span> are model-written
        practice and are not from past exams.</p>
        <p>Formulas rendered with <a href="https://katex.org/" rel="noopener">KaTeX</a>.
        Built from the official I2DL materials for personal study. Spotted a mistake? Open an issue on the repo.</p>
      </div>
    </div>
  </div>
  <div class="sources-bar">TUM IN2346 · I2DL Exam Q&amp;A · for educational use only — not affiliated with or endorsed by TUM.</div>
</footer>"""

def source_tags(sources) -> str:
    out = []
    for s in sources:
        ai = s.lower().startswith("ai")
        cls = "src-ai" if ai else "src"
        out.append(f"<span class='{cls}'>{esc(s)}</span>")
    return " ".join(out)

# ---------------------------------------------------------------- rendering

def render_question(q) -> str:
    qtype = q["type"]
    primary = q["sources"][0]
    type_label = {"mc": "Multiple Choice", "open": "Open", "ai": "AI-generated"}[qtype]
    type_cls = {"mc": "t-mc", "open": "t-open", "ai": "t-ai"}[qtype]

    head = (
        f"<div class='q-head'>"
        f"<span class='qtype {type_cls}'>{type_label}</span>"
        f"{freq_badge(q.get('freq', 0))}"
        f"<span class='q-src'>{source_tags(q['sources'])}</span>"
        f"</div>"
    )

    # md_block so questions that embed a ```code``` snippet render properly
    qrender = md_block(q["q"]) if "```" in q["q"] else md_inline(q["q"])
    qbody = f"<div class='q-text'>{qrender}</div>"

    answer_html = f"<div class='answer'><div class='answer-label'>Answer</div>{md_block(q['answer'])}</div>"
    extend_html = (
        f"<div class='extend'><div class='extend-label'>💡 Extended memory</div>{md_block(q['extend'])}</div>"
        if q.get("extend") else ""
    )

    if qtype == "mc":
        # Interactive quiz: blank options; reveal answer + analysis only after the
        # learner picks option(s) and hits "Check". Any number of options may be correct.
        opts = []
        for o in q["options"]:
            c = "true" if o["correct"] else "false"
            opts.append(
                "<li class='opt'><label>"
                f"<input type='checkbox' data-correct='{c}'>"
                f"<span class='opt-text'>{md_inline(o['text'])}</span>"
                "<span class='opt-mark' aria-hidden='true'></span>"
                "</label></li>"
            )
        body_inner = (
            "<div class='quiz'>"
            "<p class='quiz-hint'>Select all options you think are correct, then check.</p>"
            "<ul class='options interactive'>" + "".join(opts) + "</ul>"
            "<div class='quiz-actions'>"
            "<button type='button' class='check-btn' disabled>Check answer</button>"
            "<button type='button' class='reset-btn' hidden>Try again</button>"
            "</div>"
            "<div class='reveal' hidden>"
            "<div class='verdict' role='status'></div>"
            f"{answer_html}{extend_html}"
            "</div>"
            "</div>"
        )
    else:
        # Open / AI: opening the card reveals the answer directly.
        body_inner = f"{answer_html}{extend_html}"

    data_attr = f"data-type='{qtype}' data-freq='{q.get('freq',0)}'"
    return (
        f"<details class='q' {data_attr}>"
        f"<summary>{head}{qbody}</summary>"
        f"<div class='q-body'>{body_inner}</div>"
        f"</details>"
    )

def render_kp(kp) -> str:
    qs = "\n".join(render_question(q) for q in kp["questions"])
    return (
        f"<section class='kp' id='{kp['id']}'>"
        f"<h2>{esc(kp['title'])}</h2>"
        f"<div class='recap'>{md_block(kp['recap'])}</div>"
        f"<div class='qlist'>{qs}</div>"
        f"</section>"
    )

def page_shell(title, body, *, depth, extra_head="") -> str:
    base = "../" if depth else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" integrity="sha384-nB0miv6/jRmo5UMMR1wu3Gz6NLsoTkbqJghGIsx//Rlm+ZU03BU6SQNC66uf4l5+" crossorigin="anonymous">
<link rel="stylesheet" href="{base}assets/style.css">
{extra_head}
</head>
<body>
{body}
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js" integrity="sha384-7zkQWkzuo3B5mTepMUcHkMB5jZaolc2xDwL6VFqjFALcbeS9Ggm/Yr2r3Dy4lfFg" crossorigin="anonymous"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js" integrity="sha384-43gviWU0YVjaDtb/GhzOouOXtZMP/7XUzwPTstBeZFe/+rCMvRwr4yROQP43s0Xk" crossorigin="anonymous"></script>
<script defer src="{base}assets/app.js"></script>
</body>
</html>
"""

# ---------------------------------------------------------------- build

def build():
    manifest = json.loads((DATA / "chapters.json").read_text(encoding="utf-8"))
    CHAPTERS_DIR.mkdir(exist_ok=True)

    # ---- chapter pages
    for ch in manifest["chapters"]:
        if ch["status"] != "ready":
            continue
        data = json.loads((DATA / ch["file"]).read_text(encoding="utf-8"))
        nq = sum(len(kp["questions"]) for kp in data["knowledge_points"])
        nai = sum(1 for kp in data["knowledge_points"] for q in kp["questions"] if q["type"] == "ai")

        toc = "\n".join(
            f"<li><a href='#{kp['id']}'>{esc(kp['title'])}</a>"
            f"<span class='toc-n'>{len(kp['questions'])}</span></li>"
            for kp in data["knowledge_points"]
        )
        kps = "\n".join(render_kp(kp) for kp in data["knowledge_points"])

        body = f"""
<header class="topbar">
  <a class="brand" href="../index.html">{TUM_LOGO.format(base='../')}<span>← All chapters</span></a>
  <div class="filters">
    <input id="search" type="search" placeholder="Search questions…" autocomplete="off">
    <label><input type="checkbox" class="ftype" value="mc" checked> MC</label>
    <label><input type="checkbox" class="ftype" value="open" checked> Open</label>
    <label><input type="checkbox" class="ftype" value="ai" checked> AI</label>
    <button id="expandAll" type="button">Expand all</button>
  </div>
</header>
<div class="layout">
  <aside class="sidebar">
    <div class="ch-tag">Chapter {esc(data['roman'])}</div>
    <h1>{esc(data['title'])}</h1>
    <p class="ch-blurb">{esc(data['blurb'])}</p>
    <div class="stat-row">
      <span class="stat"><b>{nq}</b> questions</span>
      <span class="stat"><b>{len(data['knowledge_points'])}</b> topics</span>
      <span class="stat"><b>{nai}</b> AI practice</span>
    </div>
    <details class="toc-wrap">
      <summary>Jump to topic</summary>
      <nav class="toc"><ol>{toc}</ol></nav>
    </details>
    <div class="legend">
      <div><span class="badge freq-hot">🔥 n×</span> high frequency</div>
      <div><span class="src">SS22 3.1</span> source = exam + problem no.</div>
      <div><span class="src-ai">AI-generated</span> AI practice question</div>
      <div>✅ correct option &nbsp; ❌ wrong option</div>
    </div>
  </aside>
  <main class="content">
    <p class="hint">Knowledge points are ordered by the lecture syllabus; questions within each point are sorted by exam frequency. Click any question to reveal the answer.</p>
    {kps}
    <p class="noresults" hidden>No questions match your filter.</p>
  </main>
</div>
<button id="toTop" type="button" aria-label="Back to top" hidden>↑</button>
{site_footer(manifest['exams'], base='../')}
"""
        out = page_shell(f"{data['roman']}. {data['title']} · I2DL Exam Q&A", body, depth=1)
        (CHAPTERS_DIR / f"{ch['id']}.html").write_text(out, encoding="utf-8")
        print(f"built chapters/{ch['id']}.html  ({nq} questions)")

    # ---- index hub
    cards = []
    total_q = total_topics = 0
    for ch in manifest["chapters"]:
        ready = ch["status"] == "ready"
        if ready:
            data = json.loads((DATA / ch["file"]).read_text(encoding="utf-8"))
            nq = sum(len(kp["questions"]) for kp in data["knowledge_points"])
            ntopic = len(data["knowledge_points"])
            total_q += nq
            total_topics += ntopic
            meta = f"<div class='card-meta'>{nq} questions · {ntopic} topics</div>"
            href = f"chapters/{ch['id']}.html"
            cls, badge = "card", ""
            inner = f"<a class='{cls}' href='{href}'><div class='card-roman'>{esc(ch['roman'])}</div><h3>{esc(ch['title'])}</h3>{meta}</a>"
        else:
            inner = (
                f"<div class='card card-soon'><div class='card-roman'>{esc(ch['roman'])}</div>"
                f"<h3>{esc(ch['title'])}</h3><div class='card-meta'>coming soon</div></div>"
            )
        cards.append(inner)

    exams = " ".join(f"<span class='exam'>{esc(e)}</span>" for e in manifest["exams"])
    body = f"""
<header class="hero">
  <div class="hero-inner">
    <div class="hero-top">{TUM_LOGO.format(base='')}<span class="kicker">Technische Universität München · IN2346</span></div>
    <h1>Introduction to Deep Learning</h1>
    <p class="tagline">Exam Q&amp;A Bank · closed-book revision · open &amp; free</p>
    <p class="lead">Every problem from 12 past exams + the course summary, classified by chapter and knowledge point, sorted by exam frequency, answered from the official solutions, with LaTeX-rendered formulas.</p>
    <div class="exams">{exams}</div>
  </div>
</header>
<main class="hub">
  <div class="cards">
    {''.join(cards)}
  </div>
  <section class="how">
    <h2>How to use this deck</h2>
    <ul>
      <li><b>Frequency-first:</b> within each topic, questions are ordered by how often they appear across exams — drill the 🔥 ones first.</li>
      <li><b>Source-tagged:</b> every question cites its origin, e.g. <span class="src">SS22 3.1</span> = SoSe&nbsp;2022 exam, problem 3.1.</li>
      <li><b>Answers = official solutions.</b> For variant phrasings, the scoring points are merged. <span class="src-ai">AI-generated</span> practice items are clearly marked.</li>
      <li><b>Closed-book ready:</b> click a question to reveal the answer and an “extended memory” hook.</li>
    </ul>
  </section>
  <p class="hubnote">All 7 chapters complete — {total_q} questions across {total_topics} knowledge points, from 12 past exams + the course summary.</p>
</main>
{site_footer(manifest['exams'], base='')}
"""
    out = page_shell("I2DL Exam Q&A · TUM IN2346", body, depth=0)
    (ROOT / "index.html").write_text(out, encoding="utf-8")
    print("built index.html")

if __name__ == "__main__":
    build()
