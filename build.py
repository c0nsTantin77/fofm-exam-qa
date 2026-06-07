#!/usr/bin/env python3
"""
Static-site generator for the I2DL Exam Q&A review.

Reads data/chapters.json (manifest) and data/<chapter>.json (content),
emits index.html (hub) and chapters/<id>.html (one page per ready chapter).

Formulas are written inline as $...$ / $$...$$ and rendered client-side by
KaTeX auto-render. Zero build dependencies beyond the Python stdlib.
"""
import hashlib
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).parent

def qid(kp_id, q):
    """Stable per-question id (content hash) — survives reordering/insertions,
    so it can key persistent study data (reviewed / notes / SRS)."""
    h = hashlib.sha1((kp_id + "::" + q["q"]).encode("utf-8")).hexdigest()
    return "q" + h[:9]
DATA = ROOT / "data"
CHAPTERS_DIR = ROOT / "chapters"

def _asset_ver():
    """Short content hash of the CSS/JS so their URLs change when they change,
    forcing browsers to fetch fresh assets (no stale cache after an update)."""
    h = hashlib.sha1()
    for rel in ("assets/style.css", "assets/app.js"):
        p = ROOT / rel
        if p.exists():
            h.update(p.read_bytes())
    return h.hexdigest()[:8]

ASSET_VER = _asset_ver()

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

def plain(s: str) -> str:
    """Strip markdown/LaTeX/code to plain text for the search index."""
    s = re.sub(r"```.*?```", " ", s, flags=re.DOTALL)
    s = re.sub(r"\$\$.*?\$\$|\$[^$]*\$", " ", s, flags=re.DOTALL)  # drop math
    s = re.sub(r"[*`#>_]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()

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

_Q_MARKER = re.compile(r"\((?:\d+(?:\.\d+)*|[a-z]|[ivx]{1,3})\)")
_A_BOLD = re.compile(r"\*\*[^*]+?\*\*")

def _insert_breaks(s: str, positions) -> str:
    """Insert a newline (→ <br>) before each given index, eating preceding spaces
    and never doubling an existing newline. Apply back-to-front to keep indices."""
    for pos in sorted(positions, reverse=True):
        k = pos
        while k > 0 and s[k - 1] == " ":
            k -= 1
        if k > 0 and s[k - 1] != "\n":
            s = s[:k] + "\n" + s[pos:]
    return s

def break_question(s: str) -> str:
    """Put a sub-part marker like '(8.3)' on a new line when it follows an inline
    math formula (separating the setup from the question). Short consecutive
    markers not preceded by a formula stay inline. Standalone markers only — so
    function notation like f(x)/σ(x) (no leading space) is never split."""
    cuts, prev = [], 0
    for m in _Q_MARKER.finditer(s):
        spaced = m.start() == 0 or s[m.start() - 1] in " \n"
        if spaced and m.start() != 0 and "$" in s[prev:m.start()]:
            cuts.append(m.start())
        if spaced:
            prev = m.end()
    return _insert_breaks(s, cuts)

def break_answer(s: str) -> str:
    """Lay out a multi-part answer / knowledge summary: break before any **bold**
    span that begins a new clause (preceded by . ? ! : ;) — so labels and key
    terms (**6.3:**, **True:**, **L2**, **Dropout** …) each start on their own
    line, while bold emphasis mid-sentence (preceded by a word) is left inline."""
    cuts = []
    for m in _A_BOLD.finditer(s):
        if m.start() == 0:
            continue
        before = s[:m.start()].rstrip()
        if before and before[-1] in ".?!:;":
            cuts.append(m.start())
    return _insert_breaks(s, cuts)

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

def _coverage_html():
    """Full coverage list under Sources (from coverage-summary.json) — every exam + the summary."""
    p = DATA / "coverage-summary.json"
    if not p.exists():
        return ""
    s = json.loads(p.read_text(encoding="utf-8"))
    allrows = sorted(s["per_exam"], key=lambda r: r["pct"], reverse=True)
    chips = " ".join(f"<span class='cov-chip'>{esc(r['exam'])} {r['pct']}%</span>" for r in allrows)
    chips += " <span class='cov-chip cov-chip-full'>Summary · backbone</span>"
    return (
        f"<div class='coverage'><h4>Coverage</h4>"
        f"<p><b>{s['overall_pct']}%</b> of past-exam questions are cited directly "
        f"({s['cited']}/{s['detected']}); the remainder are covered through the course summary "
        f"(the backbone) or folded into merged cards.</p>"
        f"<div class='cov-chips'>{chips}</div></div>"
    )

def site_footer(exams, *, base) -> str:
    src_line = (
        "<p class='src-line'>"
        "<span class='src'>SS25</span> SoSe 2025 endterm, "
        "<span class='src'>WS24</span> WiSe 2024/25 endterm, … — all 12 TUM IN2346 endterms "
        "(SS20–SS25, WS21–WS26, Mock) plus the <span class='src'>Summary</span> course summary.</p>"
    )
    return f"""
<footer class="sources">
  <div class="sources-inner">
    {TUM_LOGO.format(base=base)}
    <div class="sources-cols">
      <div>
        <h4>Sources</h4>
        {src_line}
        {_coverage_html()}
      </div>
      <div>
        <h4>About</h4>
        <p>Revision deck for <b>Introduction to Deep Learning (IN2346)</b>, TU&nbsp;München.
        Answers follow the <b>official sample solutions</b>; for variant phrasings the scoring
        points are merged. Items tagged <span class="src-ai">AI-generated</span> are model-written
        practice and are not from past exams.</p>
        <p>Formulas rendered with <a href="https://katex.org/" rel="noopener">KaTeX</a>.
        Built from the official I2DL materials for personal study. Spotted a mistake?
        <a href="https://github.com/c0nsTantin77/i2dl-exam-qa/issues" rel="noopener">Open an issue on the repo</a>.</p>
        <p><a class="gh-star" href="https://github.com/c0nsTantin77/i2dl-exam-qa" rel="noopener">
          <svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
          Star this project on GitHub</a></p>
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

LETTERS = "ABCDEFGH"

def render_question(q, anchor, qnum="") -> str:
    qtype = q["type"]
    is_ai = qtype == "ai"
    is_mc = qtype == "mc" or (is_ai and "options" in q)   # AI questions can be MC too
    fmt_label = "Multiple choice" if is_mc else "Open"
    qn = f"<span class='q-num'>{esc(qnum)}</span>" if qnum else ""

    if is_ai:
        # AI items: keep the "AI-generated" marker, show the format (Open/MC) as a
        # badge instead of "practice", and drop the redundant right-side source chip.
        head = (
            f"<div class='q-head'>"
            f"{qn}"
            f"<span class='qtype t-ai'>AI-generated</span>"
            f"<span class='fmt-badge'>{fmt_label}</span>"
            f"</div>"
        )
    else:
        type_label = {"mc": "Multiple Choice", "open": "Open"}[qtype]
        type_cls = {"mc": "t-mc", "open": "t-open"}[qtype]
        head = (
            f"<div class='q-head'>"
            f"{qn}"
            f"<span class='qtype {type_cls}'>{type_label}</span>"
            f"{freq_badge(q.get('freq', 0))}"
            f"<span class='q-src'>{source_tags(q['sources'])}</span>"
            f"</div>"
        )

    # md_block so questions that embed a ```code``` snippet render properly;
    # break_question puts a formula-led sub-part marker on its own line.
    qsrc = break_question(q["q"])
    qrender = md_block(qsrc) if "```" in qsrc else md_inline(qsrc)
    qbody = f"<div class='q-text'>{qrender}</div>"

    answer_html = f"<div class='answer'><div class='answer-label'>Answer</div>{md_block(break_answer(q['answer']))}</div>"
    extend_html = (
        f"<div class='extend'><div class='extend-label'>💡 Extended memory</div>{md_block(q['extend'])}</div>"
        if q.get("extend") else ""
    )

    if is_mc:
        # Interactive quiz: blank options; reveal answer + analysis only after the
        # learner picks option(s) and hits "Check". Any number of options may be correct.
        opts, correct_letters = [], []
        for i, o in enumerate(q["options"]):
            letter = LETTERS[i]
            c = "true" if o["correct"] else "false"
            if o["correct"]:
                correct_letters.append(letter)
            opts.append(
                "<li class='opt'><label>"
                f"<input type='checkbox' data-correct='{c}'>"
                f"<span class='opt-letter'>{letter}</span>"
                f"<span class='opt-text'>{md_inline(o['text'])}</span>"
                "<span class='opt-mark' aria-hidden='true'></span>"
                "</label></li>"
            )
        # explicit, fixed reference for quick memorization
        cl = ", ".join(correct_letters) if correct_letters else "none (all options are false)"
        correct_line = f"<div class='correct-line'>✅ Correct: <b>{cl}</b></div>"
        body_inner = (
            "<div class='quiz'>"
            "<p class='quiz-hint'>Select the options you think are correct (it may be none), then check.</p>"
            "<ul class='options interactive'>" + "".join(opts) + "</ul>"
            "<div class='quiz-actions'>"
            "<button type='button' class='check-btn'>Check answer</button>"
            "<button type='button' class='reset-btn' hidden>Try again</button>"
            "</div>"
            "<div class='reveal' hidden>"
            "<div class='verdict' role='status'></div>"
            f"{correct_line}{answer_html}{extend_html}"
            "</div>"
            "</div>"
        )
    else:
        # Open / AI: opening the card reveals the answer directly.
        body_inner = f"{answer_html}{extend_html}"

    # cross-cutting concept tags → link to a site-wide search on the index
    tags = q.get("tags", [])
    if tags:
        import urllib.parse as _up
        chips = "".join(
            f"<a class='tag' href='../tags.html?t={_up.quote(t)}'>{esc(t)}</a>" for t in tags
        )
        body_inner += f"<div class='tags'>{chips}</div>"

    # per-question study controls (state saved in the browser via app.js)
    body_inner += (
        "<div class='study'>"
        "<label class='study-rev'><input type='checkbox' class='rev-box'> Reviewed</label>"
        "<button type='button' class='wrong-btn'>★ Wrong book</button>"
        "<button type='button' class='note-btn'>📝 Note</button>"
        "<span class='srs-due'></span>"
        "<div class='note-wrap' hidden><textarea class='note-area' rows='3' placeholder='Your notes for this question…'></textarea></div>"
        "</div>"
    )

    data_attr = f"data-type='{qtype}' data-freq='{q.get('freq',0)}'"
    return (
        f"<details class='q' id='{anchor}' {data_attr}>"
        f"<summary>{head}{qbody}</summary>"
        f"<div class='q-body'>{body_inner}</div>"
        f"</details>"
    )

def sorted_questions(kp):
    """Render order: by exam frequency (desc), stable. AI practice (freq 0) sinks last."""
    return sorted(kp["questions"], key=lambda q: q.get("freq", 0), reverse=True)

def render_kp(kp, kpnum="") -> str:
    qs = "\n".join(
        render_question(q, qid(kp["id"], q), f"{kpnum}.{j}" if kpnum else "")
        for j, q in enumerate(sorted_questions(kp), 1)
    )
    num = f"<span class='kp-num'>{esc(kpnum)}</span> " if kpnum else ""
    return (
        f"<section class='kp' id='{kp['id']}'>"
        f"<h2>{num}{esc(kp['title'])}</h2>"
        f"<div class='recap'>{md_block(break_answer(kp['recap']))}</div>"
        f"<div class='qlist'>{qs}</div>"
        f"</section>"
    )

def page_shell(title, body, *, depth, extra_head="", need_index=False) -> str:
    base = "../" if depth else ""
    # search index is inlined as a JS global (works under file:// and http — no fetch)
    index_js = f'<script defer src="{base}search-index.js"></script>' if need_index else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<!-- Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-163M4VJ1VD"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){{dataLayer.push(arguments);}}
gtag('js', new Date());
gtag('config', 'G-163M4VJ1VD');
</script>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" integrity="sha384-nB0miv6/jRmo5UMMR1wu3Gz6NLsoTkbqJghGIsx//Rlm+ZU03BU6SQNC66uf4l5+" crossorigin="anonymous">
<link rel="stylesheet" href="{base}assets/style.css?v={ASSET_VER}">
{extra_head}
</head>
<body>
<div id="presence-bar" aria-live="polite"></div>
{body}
{index_js}
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js" integrity="sha384-7zkQWkzuo3B5mTepMUcHkMB5jZaolc2xDwL6VFqjFALcbeS9Ggm/Yr2r3Dy4lfFg" crossorigin="anonymous"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js" integrity="sha384-43gviWU0YVjaDtb/GhzOouOXtZMP/7XUzwPTstBeZFe/+rCMvRwr4yROQP43s0Xk" crossorigin="anonymous"></script>
<script defer src="{base}assets/config.js"></script>
<script defer src="{base}assets/app.js?v={ASSET_VER}"></script>
</body>
</html>
"""

# ---------------------------------------------------------------- build

def build():
    manifest = json.loads((DATA / "chapters.json").read_text(encoding="utf-8"))
    CHAPTERS_DIR.mkdir(exist_ok=True)
    search_index = []

    # ---- chapter pages
    for ch in manifest["chapters"]:
        if ch["status"] != "ready":
            continue
        data = json.loads((DATA / ch["file"]).read_text(encoding="utf-8"))
        nq = sum(len(kp["questions"]) for kp in data["knowledge_points"])
        nai = sum(1 for kp in data["knowledge_points"] for q in kp["questions"] if q["type"] == "ai")

        # search index: one entry per question, same anchor (stable qid) as render_kp
        for kp in data["knowledge_points"]:
            for q in sorted_questions(kp):
                tagtext = " ".join(q.get("tags", []))
                srcs = q["sources"]
                search_index.append({
                    "c": ch["id"], "ct": data["title"], "kp": kp["title"],
                    "a": qid(kp["id"], q), "t": q["type"],
                    "src": srcs[0], "srcs": srcs,
                    "q": plain(q["q"]),
                    "tg": q.get("tags", []),
                    "txt": (plain(q["q"] + " " + q.get("answer", "") + " " + kp["title"])
                            + " " + tagtext + " " + " ".join(srcs)).lower(),
                })

        chnum = int(re.sub(r"\D", "", ch["id"]) or "0")
        toc = "\n".join(
            f"<li><a href='#{kp['id']}'>"
            f"<span class='toc-num'>{chnum}.{i}</span>"
            f"<span class='toc-label'>{esc(kp['title'])}</span>"
            f"<span class='toc-n'>{len(kp['questions'])}</span></a></li>"
            for i, kp in enumerate(data["knowledge_points"], 1)
        )
        kps = "\n".join(
            render_kp(kp, f"{chnum}.{i}")
            for i, kp in enumerate(data["knowledge_points"], 1)
        )

        body = f"""
<header class="topbar">
  <a class="brand" href="../index.html">{TUM_LOGO.format(base='../')}<span class="brand-back">← All<span class="brand-full"> chapters</span></span></a>
  <div class="nowat-wrap">
    <button id="nowAt" class="nowat" type="button" aria-haspopup="true" aria-expanded="false" aria-controls="tocPop" title="Jump to a topic">
      <span class="nowat-here">Contents</span><span class="nowat-caret" aria-hidden="true">▾</span>
    </button>
    <nav id="tocPop" class="toc-pop toc" hidden aria-label="Chapter contents"><ol>{toc}</ol></nav>
  </div>
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
    <div class="ch-progress" data-ch="{ch['id']}"></div>
    <div class="legend">
      <div><span class="badge freq-hot">🔥 n×</span> high frequency</div>
      <div><span class="src">SS22 3.1</span> source = exam + problem no.</div>
      <div><span class="src-ai">AI-generated</span> AI practice question</div>
      <div><span class="tag" style="cursor:default">tag</span> click to find related Qs site-wide</div>
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
            inner = (
                f"<a class='card' href='{href}'>"
                f"<div class='card-top'><span class='card-roman'>{esc(ch['roman'])}</span>"
                f"<span class='card-prog' data-ch='{ch['id']}'></span></div>"
                f"<h3>{esc(ch['title'])}</h3>{meta}</a>"
            )
        else:
            inner = (
                f"<div class='card card-soon'><div class='card-roman'>{esc(ch['roman'])}</div>"
                f"<h3>{esc(ch['title'])}</h3><div class='card-meta'>coming soon</div></div>"
            )
        cards.append(inner)

    import urllib.parse as _up0
    exams = " ".join(
        f"<a class='exam' href='exams.html?e={_up0.quote(e)}'>{esc(e)}</a>"
        for e in manifest["exams"]
    )

    # popular concept-tag chips (top by question count)
    import urllib.parse as _up
    from collections import Counter
    tagc = Counter(t for e in search_index for t in e.get("tg", []))
    poptags = [t for t, _ in tagc.most_common(4)]
    chips = "".join(
        f"<a class='ptag' href='tags.html?t={_up.quote(t)}'>{esc(t)}"
        f"<span class='ptag-n'>{tagc[t]}</span></a>" for t in poptags
    )
    poptags_html = (
        "<section class='poptags'><div class='poptags-head'>"
        "<span class='poptags-label'>Popular tags</span>"
        f"<a class='poptags-all' href='tags.html'>All {len(tagc)} tags →</a></div>"
        f"<div class='poptags-row'>{chips}</div></section>"
    )

    # recent updates widget (optional)
    updates_html = ""
    upath = DATA / "updates.json"
    if upath.exists():
        ups = json.loads(upath.read_text(encoding="utf-8"))[:3]
        items = "".join(
            f"<li><span class='up-date'>{esc(u['date'])}</span>"
            f"<span class='up-text'>{esc(u['text'])}</span></li>"
            for u in ups
        )
        updates_html = (
            "<aside class='updates'><h2>📣 Recent updates</h2>"
            f"<ul class='up-list'>{items}</ul></aside>"
        )

    body = f"""
<header class="hero">
  <div class="hero-inner">
    <div class="hero-top">{TUM_LOGO.format(base='')}<span class="kicker">Technische Universität München · IN2346</span></div>
    <h1>Introduction to Deep Learning</h1>
    <ul class="hero-points">
      <li><span class="hp-ic">🔎</span><span class="hp-t">Search by concept tag</span><span class="hp-d">jump between related questions across chapters</span></li>
      <li><span class="hp-ic">✅</span><span class="hp-t">Interactive multiple-choice</span><span class="hp-d">pick, check, then reveal the answer</span></li>
      <li><span class="hp-ic">🤖</span><span class="hp-t">AI-generated practice</span><span class="hp-d">extra questions on every knowledge point</span></li>
    </ul>
    <div class="exams-block">
      <span class="exams-hint">Tap an exam to browse its questions ↓</span>
      <div class="exams">{exams}</div>
    </div>
  </div>
</header>
<main class="hub">
  <div class="gsearch">
    <div class="gsearch-box">
      <svg class="gsearch-icon" viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" d="M21 21l-4.3-4.3M11 18a7 7 0 100-14 7 7 0 000 14z"/></svg>
      <input id="gsearch" type="search" placeholder="Search all {total_q} questions — try “dropout”, “Adam”, or “SS23 6.1”" autocomplete="off" aria-label="Search all questions">
    </div>
    <div id="gresults" class="gresults" hidden></div>
  </div>
  {poptags_html}
  <details class="progress-card" id="progress" hidden open>
    <summary class="prog-head"><span class="prog-title">Your progress</span><span id="authctl" class="authctl"></span></summary>
    <div id="prog-body"></div>
  </details>
  <div class="cards">
    {''.join(cards)}
  </div>
  {updates_html}
  <section class="how">
    <h2>How to use this deck</h2>
    <div class="how-grid">
      <div class="how-col">
        <h3>🔎 Find</h3>
        <ul>
          <li>Search any keyword or concept <b>tag</b> (e.g. <i>dropout</i>, <i>Adam</i>).</li>
          <li>Jump to an exact question by code — type <span class="src">SS23 6.1</span>.</li>
          <li>Browse <b>by exam</b> (tap a paper above) or <b>by tag</b> across all chapters.</li>
        </ul>
      </div>
      <div class="how-col">
        <h3>📝 Practice</h3>
        <ul>
          <li>Answers follow the <b>official solutions</b>; <span class="src-ai">AI-generated</span> items are marked.</li>
          <li><b>Interactive multiple-choice</b> — pick options, check, then reveal.</li>
          <li>Questions are ordered by <b>exam frequency</b> — drill the 🔥 ones first.</li>
        </ul>
      </div>
      <div class="how-col">
        <h3>📈 Track</h3>
        <ul>
          <li>Mark a question <b>Reviewed</b>, add it to your <b>wrong book</b>, or jot a <b>note</b>.</li>
          <li><b>Spaced repetition</b> tells you what to review today.</li>
          <li><b>Sign in</b> to sync your progress across devices.</li>
        </ul>
      </div>
    </div>
  </section>
  <section class="feedback" id="feedback">
    <div class="feedback-text"><span class="feedback-title">💬 Feedback</span>
      <span class="feedback-sub">Spotted a wrong answer or have a suggestion? It goes straight to the author.</span></div>
    <a class="feedback-link" id="feedback-link" target="_blank" rel="noopener">Open the feedback form →</a>
  </section>
  <p class="hubnote">All 7 chapters complete — {total_q} questions across {total_topics} knowledge points, from 12 past exams + the course summary.</p>
</main>
{site_footer(manifest['exams'], base='')}
"""
    out = page_shell("I2DL Exam Q&A · TUM IN2346", body, depth=0, need_index=True)
    (ROOT / "index.html").write_text(out, encoding="utf-8")
    print("built index.html")

    # search index — inlined as a JS global (no fetch; works under file:// + http)
    blob = json.dumps(search_index, ensure_ascii=False, separators=(",", ":"))
    (ROOT / "search-index.js").write_text(f"window.SEARCH_INDEX={blob};", encoding="utf-8")
    print(f"built search-index.js  ({len(search_index)} entries)")

    # ---- tags overview page (standalone) ----
    from collections import Counter
    tag_counts = Counter(t for e in search_index for t in e.get("tg", []))
    tag_body = f"""
<header class="topbar">
  <a class="brand" href="index.html">{TUM_LOGO.format(base='')}<span class="brand-back">← All<span class="brand-full"> chapters</span></span></a>
</header>
<main class="tagpage" id="tagpage" data-tagcount="{len(tag_counts)}">
  <div id="tagpage-body"><p class="hint">Loading…</p></div>
</main>
{site_footer(manifest['exams'], base='')}
"""
    out = page_shell("Concept tags · I2DL Exam Q&A", tag_body, depth=0, need_index=True)
    (ROOT / "tags.html").write_text(out, encoding="utf-8")
    print(f"built tags.html  ({len(tag_counts)} tags)")

    # ---- browse-by-exam page (standalone) ----
    exam_meta = json.dumps({"order": manifest["exams"], "names": EXAM_NAMES}, ensure_ascii=False)
    exam_body = f"""
<header class="topbar">
  <a class="brand" href="index.html">{TUM_LOGO.format(base='')}<span class="brand-back">← All<span class="brand-full"> chapters</span></span></a>
</header>
<main class="tagpage" id="exampage" data-exams='{exam_meta}'>
  <div id="exampage-body"><p class="hint">Loading…</p></div>
</main>
{site_footer(manifest['exams'], base='')}
"""
    out = page_shell("Browse by exam · I2DL Exam Q&A", exam_body, depth=0, need_index=True)
    (ROOT / "exams.html").write_text(out, encoding="utf-8")
    print("built exams.html")

    # ---- review page: due-today (Ebbinghaus) + wrong book + export/import ----
    review_body = f"""
<header class="topbar">
  <a class="brand" href="index.html">{TUM_LOGO.format(base='')}<span class="brand-back">← All<span class="brand-full"> chapters</span></span></a>
  <div class="filters">
    <button id="exportBtn" type="button" class="io-btn">⬇ Export</button>
    <label class="io-btn" for="importFile">⬆ Import</label>
    <input id="importFile" type="file" accept="application/json" hidden>
  </div>
</header>
<main class="tagpage" id="reviewpage">
  <div id="reviewpage-body"><p class="hint">Loading…</p></div>
</main>
{site_footer(manifest['exams'], base='')}
"""
    out = page_shell("Review · I2DL Exam Q&A", review_body, depth=0, need_index=True)
    (ROOT / "review.html").write_text(out, encoding="utf-8")
    print("built review.html")

if __name__ == "__main__":
    build()
