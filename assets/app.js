// I2DL Exam Q&A — client interactions: KaTeX, search, tags/exams, study system.
(function () {
  // ===================================================================
  // Progress store — one JSON blob in localStorage. Designed so a cloud
  // sync layer can later batch-push this same object (one doc per user).
  // ===================================================================
  const Store = (function () {
    const KEY = "i2dl_progress_v1";
    const SRS_DAYS = [1, 2, 4, 7, 15, 30, 60]; // Ebbinghaus-style intervals
    const DAY = 86400000;
    const today = () => new Date().toISOString().slice(0, 10);
    const addDays = (n) => new Date(Date.now() + n * DAY).toISOString().slice(0, 10);
    let P;
    try { P = JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { P = {}; }
    ["reviewed", "wrong", "notes", "srs", "activity"].forEach((k) => { if (!P[k]) P[k] = {}; });

    let timer = null, dirty = false;
    function persist() {
      try { localStorage.setItem(KEY, JSON.stringify(P)); } catch (e) {}
      dirty = false;
      if (window.CloudSync) window.CloudSync.schedule(P); // optional Stage-3 hook
    }
    function save() { // debounced — avoids writing on every keystroke
      dirty = true;
      clearTimeout(timer);
      timer = setTimeout(persist, 600);
    }
    window.addEventListener("visibilitychange", () => { if (document.hidden && dirty) persist(); });
    window.addEventListener("beforeunload", () => { if (dirty) persist(); });

    function bumpActivity() { const d = today(); P.activity[d] = (P.activity[d] || 0) + 1; }

    return {
      data: () => P,
      isReviewed: (id) => !!P.reviewed[id],
      isWrong: (id) => !!P.wrong[id],
      note: (id) => P.notes[id] || "",
      due: (id) => (P.srs[id] ? P.srs[id].due : null),
      setReviewed(id, on) {
        if (on) {
          P.reviewed[id] = Date.now();
          const s = P.srs[id] || { n: 0 };
          s.n = Math.min((s.n || 0) + 1, SRS_DAYS.length);
          s.last = today(); s.due = addDays(SRS_DAYS[s.n - 1]);
          P.srs[id] = s; bumpActivity();
        } else { delete P.reviewed[id]; delete P.srs[id]; }
        save();
      },
      setWrong(id, on) {
        if (on) { P.wrong[id] = Date.now(); P.srs[id] = { n: 0, last: today(), due: addDays(1) }; bumpActivity(); }
        else delete P.wrong[id];
        save();
      },
      setNote(id, text) { if (text) P.notes[id] = text; else delete P.notes[id]; save(); },
      dueList(ids) {
        const t = today();
        return ids.filter((id) => P.srs[id] && P.srs[id].due && P.srs[id].due <= t);
      },
      wrongIds: () => Object.keys(P.wrong),
      reviewedIds: () => Object.keys(P.reviewed),
      exportBlob: () => JSON.stringify(P, null, 2),
      importBlob(json) {
        const obj = JSON.parse(json);
        ["reviewed", "wrong", "notes", "srs", "activity"].forEach((k) => { P[k] = obj[k] || P[k] || {}; });
        persist();
      },
    };
  })();
  window.Store = Store;

  function renderMath() {
    if (window.renderMathInElement) {
      renderMathInElement(document.body, {
        delimiters: [
          { left: "$$", right: "$$", display: true },
          { left: "$", right: "$", display: false },
        ],
        throwOnError: false,
      });
    }
  }
  // auto-render.min.js is deferred; run after it is ready.
  if (document.readyState === "complete") renderMath();
  else window.addEventListener("load", renderMath);

  const search = document.getElementById("search");
  const typeBoxes = Array.from(document.querySelectorAll(".ftype"));
  const noResults = document.querySelector(".noresults");

  function activeTypes() {
    return new Set(typeBoxes.filter((b) => b.checked).map((b) => b.value));
  }

  function applyFilter() {
    if (!search && !typeBoxes.length) return;
    const term = (search ? search.value : "").trim().toLowerCase();
    const types = activeTypes();
    let visible = 0;
    document.querySelectorAll(".kp").forEach((kp) => {
      let kpVisible = 0;
      kp.querySelectorAll("details.q").forEach((q) => {
        const typeOk = types.has(q.dataset.type);
        const textOk = !term || q.textContent.toLowerCase().includes(term);
        const show = typeOk && textOk;
        q.hidden = !show;
        if (show) {
          kpVisible++;
          visible++;
        }
      });
      kp.hidden = kpVisible === 0;
    });
    if (noResults) noResults.hidden = visible !== 0;
  }

  if (search) search.addEventListener("input", applyFilter);
  typeBoxes.forEach((b) => b.addEventListener("change", applyFilter));

  // ---- interactive multiple-choice quizzes ----------------------------
  document.querySelectorAll(".quiz").forEach((quiz) => {
    const inputs = Array.from(quiz.querySelectorAll("input[type=checkbox]"));
    const checkBtn = quiz.querySelector(".check-btn");
    const resetBtn = quiz.querySelector(".reset-btn");
    const reveal = quiz.querySelector(".reveal");
    const verdict = quiz.querySelector(".verdict");

    // Note: the check button is always enabled — for some questions the correct
    // answer is to select NONE of the options, which must be submittable.
    checkBtn.addEventListener("click", () => {
      let allRight = true;
      inputs.forEach((inp) => {
        const correct = inp.dataset.correct === "true";
        const li = inp.closest(".opt");
        const mark = li.querySelector(".opt-mark");
        li.classList.add(correct ? "is-correct" : "is-wrong");
        mark.textContent = correct ? "✅" : "❌";
        if (inp.checked && !correct) { li.classList.add("picked-wrong"); allRight = false; }
        if (!inp.checked && correct) { li.classList.add("missed"); allRight = false; }
        if (inp.checked && correct) li.classList.add("picked-right");
        inp.disabled = true;
      });
      verdict.textContent = allRight ? "✓ Correct — well done!" : "✗ Not quite — see the correct marks and explanation below.";
      verdict.className = "verdict " + (allRight ? "ok" : "no");
      reveal.hidden = false;
      quiz.classList.add("done");
      checkBtn.hidden = true;
      resetBtn.hidden = false;
      // got it wrong → add to the wrong book automatically
      const qel = quiz.closest("details.q");
      if (qel && !allRight) {
        Store.setWrong(qel.id, true);
        const wb = qel.querySelector(".wrong-btn");
        if (wb) wb.classList.add("on");
      }
    });

    resetBtn.addEventListener("click", () => {
      inputs.forEach((inp) => {
        inp.checked = false;
        inp.disabled = false;
        const li = inp.closest(".opt");
        li.className = "opt";
        li.querySelector(".opt-mark").textContent = "";
      });
      reveal.hidden = true;
      verdict.textContent = "";
      quiz.classList.remove("done");
      checkBtn.hidden = false;
      resetBtn.hidden = true;
    });
  });

  // ---- per-question study controls (reviewed / wrong book / notes) ----
  function applyStudy(bar) { // (re)reflect saved state onto one control bar
    const qel = bar.closest("details.q"); if (!qel) return;
    const id = qel.id;
    const rev = bar.querySelector(".rev-box");
    const wrongBtn = bar.querySelector(".wrong-btn");
    const noteArea = bar.querySelector(".note-area");
    const due = bar.querySelector(".srs-due");
    rev.checked = Store.isReviewed(id);
    wrongBtn.classList.toggle("on", Store.isWrong(id));
    if (!noteArea.matches(":focus")) noteArea.value = Store.note(id);
    qel.classList.toggle("has-note", !!Store.note(id));
    qel.classList.toggle("is-reviewed", Store.isReviewed(id));
    const d = Store.due(id);
    if (Store.isReviewed(id) && d) {
      const overdue = d <= new Date().toISOString().slice(0, 10);
      due.textContent = overdue ? "review due" : "next review " + d;
      due.className = "srs-due" + (overdue ? " over" : "");
    } else due.textContent = "";
  }
  document.querySelectorAll(".study").forEach((bar) => {
    const qel = bar.closest("details.q"); if (!qel) return;
    const id = qel.id;
    const rev = bar.querySelector(".rev-box");
    const wrongBtn = bar.querySelector(".wrong-btn");
    const noteBtn = bar.querySelector(".note-btn");
    const noteWrap = bar.querySelector(".note-wrap");
    const noteArea = bar.querySelector(".note-area");
    applyStudy(bar);
    rev.addEventListener("change", () => { Store.setReviewed(id, rev.checked); applyStudy(bar); });
    wrongBtn.addEventListener("click", () => { Store.setWrong(id, !Store.isWrong(id)); applyStudy(bar); });
    noteBtn.addEventListener("click", () => { noteWrap.hidden = !noteWrap.hidden; if (!noteWrap.hidden) noteArea.focus(); });
    noteArea.addEventListener("input", () => { Store.setNote(id, noteArea.value.trim()); applyStudy(bar); });
  });
  function applyAllStudy() { document.querySelectorAll(".study").forEach(applyStudy); }

  // ---- deep-link: open the target question when arriving via #anchor ----
  function openHashTarget() {
    if (!location.hash) return;
    const el = document.querySelector(location.hash);
    if (el && el.tagName === "DETAILS") {
      el.open = true;
      el.scrollIntoView({ block: "center" });
      el.classList.add("flash");
      setTimeout(() => el.classList.remove("flash"), 1600);
    }
  }
  window.addEventListener("load", openHashTarget);
  window.addEventListener("hashchange", openHashTarget);

  const INDEX = window.SEARCH_INDEX || [];          // inlined; no fetch needed
  const TYPE = { mc: "MC", open: "Open", ai: "AI" };
  const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");
  // link from this page (index/tags at root, chapters in /chapters/) to a question
  const onChapters = /\/chapters\//.test(location.pathname);
  const qHref = (e) => (onChapters ? "" : "chapters/") + e.c + ".html#" + e.a;

  // ---- global site-wide search (index page) ----
  const gbox = document.getElementById("gsearch");
  const gres = document.getElementById("gresults");
  if (gbox && gres) {
    function runSearch() {
      const term = gbox.value.trim().toLowerCase();
      if (!term) { gres.hidden = true; gres.innerHTML = ""; return; }
      const words = term.split(/\s+/);
      const hits = INDEX.filter((e) => words.every((w) => e.txt.includes(w))).slice(0, 60);
      // if the query starts with an exam code, offer the full exam view
      const em = term.match(/^(ss\d\d|ws\d\d|mock)\b/);
      const banner = em
        ? "<a class='gbanner' href='exams.html?e=" + em[1].toUpperCase() +
          "'>📄 Browse all " + em[1].toUpperCase() + " questions →</a>"
        : "";
      if (!hits.length && !banner) {
        gres.innerHTML = "<div class='gempty'>No questions match “" + esc(gbox.value) + "”.</div>";
      } else {
        gres.innerHTML = banner +
          "<div class='gcount'>" + hits.length + " match" + (hits.length > 1 ? "es" : "") + "</div>" +
          hits.map((e) =>
            "<a class='ghit' href='" + qHref(e) + "'>" +
            "<span class='ghit-tag'>" + (TYPE[e.t] || e.t) + "</span>" +
            "<span class='ghit-q'>" + esc(e.q) + "</span>" +
            "<span class='ghit-meta'>" + esc(e.ct) + " · " + esc(e.kp) + " · " + esc(e.src) + "</span></a>"
          ).join("");
      }
      gres.hidden = false;
    }
    gbox.addEventListener("input", runSearch);
    const q0 = new URLSearchParams(location.search).get("q");
    if (q0) { gbox.value = q0; runSearch(); }
  }

  // ---- standalone tags page (tags.html) ----
  const tagPage = document.getElementById("tagpage-body");
  if (tagPage) {
    const counts = {};
    INDEX.forEach((e) => (e.tg || []).forEach((t) => (counts[t] = (counts[t] || 0) + 1)));
    const allTags = Object.keys(counts).sort((a, b) => counts[b] - counts[a] || a.localeCompare(b));
    const current = new URLSearchParams(location.search).get("t");

    function renderOverview() {
      document.title = "Concept tags · I2DL Exam Q&A";
      tagPage.innerHTML =
        "<h1 class='tp-title'>Concept tags</h1>" +
        "<p class='tp-sub'>" + allTags.length + " concepts across " + INDEX.length +
        " questions — click a tag to see every related question, across all chapters.</p>" +
        "<div class='tagcloud'>" +
        allTags.map((t) =>
          "<a class='tagbig' href='tags.html?t=" + encodeURIComponent(t) + "'>" +
          esc(t) + "<span class='tagbig-n'>" + counts[t] + "</span></a>"
        ).join("") + "</div>";
    }
    function renderTag(tag) {
      document.title = tag + " · Concept tags · I2DL";
      const hits = INDEX.filter((e) => (e.tg || []).includes(tag));
      const byChapter = {};
      hits.forEach((e) => (byChapter[e.ct] = byChapter[e.ct] || []).push(e));
      let html =
        "<a class='tp-back' href='tags.html'>← All tags</a>" +
        "<h1 class='tp-title'>Tag: <span class='tag'>" + esc(tag) + "</span></h1>" +
        "<p class='tp-sub'>" + hits.length + " question" + (hits.length > 1 ? "s" : "") +
        " across " + Object.keys(byChapter).length + " chapter(s).</p>";
      const groups = [];
      Object.keys(byChapter).forEach((ct) => {
        const id = "sec-" + slug(ct);
        groups.push({ id: id, title: ct, n: byChapter[ct].length });
        html += "<h2 class='tp-ch' id='" + id + "'>" + esc(ct) + "</h2><div class='tp-list'>" +
          byChapter[ct].map((e) =>
            "<a class='ghit' href='" + qHref(e) + "'>" +
            "<span class='ghit-tag'>" + (TYPE[e.t] || e.t) + "</span>" +
            "<span class='ghit-q'>" + esc(e.q) + "</span>" +
            "<span class='ghit-meta'>" + esc(e.kp) + " · " + esc(e.src) + "</span></a>"
          ).join("") + "</div>";
      });
      tagPage.innerHTML = html;
      buildContents(groups);
    }

    if (current && counts[current]) renderTag(current); else renderOverview();
  }

  // ---- standalone browse-by-exam page (exams.html) ----
  const examPage = document.getElementById("exampage-body");
  if (examPage) {
    const meta = JSON.parse(document.getElementById("exampage").dataset.exams || "{}");
    const order = meta.order || [], names = meta.names || {};
    const examOf = (src) => { const m = src.match(/^(SS\d\d|WS\d\d|Mock)\b/); return m ? m[1] : null; };
    const labelOf = (src) => src.replace(/^(SS\d\d|WS\d\d|Mock)\s*/, "");
    const counts = {};
    INDEX.forEach((e) => {
      const seen = new Set();
      (e.srcs || []).forEach((s) => { const x = examOf(s); if (x && !seen.has(x)) { seen.add(x); counts[x] = (counts[x] || 0) + 1; } });
    });
    const current = new URLSearchParams(location.search).get("e");

    function renderOverview() {
      document.title = "Browse by exam · I2DL Exam Q&A";
      const cards = order.filter((ex) => counts[ex]).map((ex) =>
        "<a class='examcard' href='exams.html?e=" + encodeURIComponent(ex) + "'>" +
        "<span class='examcard-code'>" + esc(ex) + "</span>" +
        "<span class='examcard-name'>" + esc(names[ex] || ex) + "</span>" +
        "<span class='examcard-n'>" + counts[ex] + " questions</span></a>"
      ).join("");
      examPage.innerHTML =
        "<h1 class='tp-title'>Browse by exam</h1>" +
        "<p class='tp-sub'>Pick an exam to see its questions grouped by chapter. " +
        "Tip: you can also type an exact code like <b>SS23 6.1</b> in the search on the home page.</p>" +
        "<div class='examgrid'>" + cards + "</div>";
    }
    function renderExam(ex) {
      document.title = ex + " · Browse by exam · I2DL";
      const hits = INDEX.filter((e) => (e.srcs || []).some((s) => examOf(s) === ex));
      // sort by the exam's own question number where possible
      const num = (e) => {
        const s = (e.srcs || []).find((x) => examOf(x) === ex) || "";
        const m = labelOf(s).match(/(\d+)\.?(\d+)?/);
        return m ? parseInt(m[1]) * 100 + (parseInt(m[2] || "0")) : 9999;
      };
      hits.sort((a, b) => num(a) - num(b));
      const byChapter = {};
      hits.forEach((e) => (byChapter[e.ct] = byChapter[e.ct] || []).push(e));
      let html =
        "<h1 class='tp-title'>" + esc(names[ex] || ex) + " <span class='tag'>" + esc(ex) + "</span></h1>" +
        "<p class='tp-sub'>" + hits.length + " question" + (hits.length > 1 ? "s" : "") +
        " across " + Object.keys(byChapter).length + " chapter(s).</p>";
      const groups = [];
      Object.keys(byChapter).forEach((ct) => {
        const id = "sec-" + slug(ct);
        groups.push({ id: id, title: ct, n: byChapter[ct].length });
        html += "<h2 class='tp-ch' id='" + id + "'>" + esc(ct) + "</h2><div class='tp-list'>" +
          byChapter[ct].map((e) => {
            const lbl = (e.srcs || []).filter((s) => examOf(s) === ex).map(labelOf).join(", ");
            return "<a class='ghit' href='" + qHref(e) + "'>" +
              "<span class='ghit-tag'>" + ex + " " + esc(lbl) + "</span>" +
              "<span class='ghit-q'>" + esc(e.q) + "</span>" +
              "<span class='ghit-meta'>" + esc(e.kp) + "</span></a>";
          }).join("") + "</div>";
      });
      examPage.innerHTML = html;
      buildContents(groups);
    }
    // bare exams.html (no ?e=) is now redundant with the homepage "By exam"
    // view → bounce there; only the single-exam ?e=X pages render here.
    if (current && counts[current]) renderExam(current);
    else location.replace("index.html#by-exam");
  }

  // ---- homepage: toggle the main grid between "By chapter" and "By exam" ----
  (function () {
    const toggle = document.querySelector(".view-toggle");
    const vChapters = document.getElementById("view-chapters");
    const vExams = document.getElementById("view-exams");
    if (!toggle || !vChapters || !vExams) return;
    const KEY = "i2dl_homeview";
    const setView = (v) => {
      const exams = v === "exams";
      vExams.hidden = !exams;
      vChapters.hidden = exams;
      toggle.querySelectorAll(".vt-btn").forEach((b) => {
        const on = b.dataset.view === v;
        b.classList.toggle("active", on);
        b.setAttribute("aria-selected", on ? "true" : "false");
      });
      try { localStorage.setItem(KEY, v); } catch (e) {}
    };
    toggle.addEventListener("click", (e) => {
      const b = e.target.closest(".vt-btn");
      if (b) setView(b.dataset.view);
    });
    let saved = "chapters";
    try { saved = localStorage.getItem(KEY) || "chapters"; } catch (e) {}
    if (location.hash === "#by-exam") saved = "exams";   // arriving from a single-exam page
    setView(saved);
  })();

  // ---- per-chapter totals + reviewed (shared by dashboard, cards, sidebar) ----
  function chapterStats() {
    const reviewedSet = new Set(Store.reviewedIds());
    const byCh = {};
    INDEX.forEach((e) => {
      const o = (byCh[e.c] = byCh[e.c] || { ct: e.ct, total: 0, done: 0 });
      o.total++; if (reviewedSet.has(e.a)) o.done++;
    });
    return { reviewedSet, byCh };
  }
  function examStats() {                            // per-exam reviewed/total (for the "By exam" cards)
    const reviewedSet = new Set(Store.reviewedIds());
    const byExam = {};
    const examOf = (s) => { const m = s.match(/^(SS\d\d|WS\d\d|Mock)\b/); return m ? m[1] : null; };
    INDEX.forEach((e) => {
      const seen = new Set();
      (e.srcs || []).forEach((s) => {
        const x = examOf(s);
        if (x && !seen.has(x)) {
          seen.add(x);
          const o = (byExam[x] = byExam[x] || { total: 0, done: 0 });
          o.total++; if (reviewedSet.has(e.a)) o.done++;
        }
      });
    });
    return byExam;
  }
  function miniRing(pct, size) {
    const r = size / 2 - 3, C = 2 * Math.PI * r, off = C * (1 - pct / 100);
    return "<svg class='mini-ring' width='" + size + "' height='" + size + "' viewBox='0 0 " + size + " " + size + "'>" +
      "<circle cx='" + size / 2 + "' cy='" + size / 2 + "' r='" + r + "' class='mr-bg'/>" +
      "<circle cx='" + size / 2 + "' cy='" + size / 2 + "' r='" + r + "' class='mr-fg' " +
      "style='stroke-dasharray:" + C + ";stroke-dashoffset:" + off + "'/>" +
      "<text x='50%' y='52%' class='mr-txt'>" + pct + "</text></svg>";
  }

  // ---- progress UI (dashboard ring + card rings + sidebar bar) — re-runnable ----
  function renderProgressUI() {
    if (!INDEX.length) return;
    const { reviewedSet, byCh } = chapterStats();
    const progBody = document.getElementById("prog-body");
    if (progBody) {
      const total = INDEX.length;
      const reviewed = INDEX.filter((e) => reviewedSet.has(e.a)).length;
      const dueCount = Store.dueList(INDEX.map((e) => e.a)).length;
      const wrongCount = INDEX.filter((e) => Store.isWrong(e.a)).length;
      const pct = total ? Math.round((100 * reviewed) / total) : 0;
      const C = 2 * Math.PI * 42, off = C * (1 - pct / 100);
      const ring =
        "<div class='prog-ring-wrap'><svg class='prog-ring' viewBox='0 0 100 100'>" +
        "<circle class='ring-bg' cx='50' cy='50' r='42'/>" +
        "<circle class='ring-fg' cx='50' cy='50' r='42' style='stroke-dasharray:" + C +
        ";stroke-dashoffset:" + off + "'/></svg>" +
        "<div class='prog-ring-num'><b>" + reviewed + "</b><span>/ " + total + "</span></div></div>";
      const stats =
        "<div class='prog-stats'>" +
        "<div class='pstat'><b>" + pct + "%</b>reviewed</div>" +
        "<div class='pstat'><b class='due'>" + dueCount + "</b>due today</div>" +
        "<div class='pstat'><b class='wrong'>" + wrongCount + "</b>wrong book</div></div>";
      progBody.innerHTML = "<div class='prog-top'>" + ring + stats +
        "<a class='prog-link' href='review.html'>Review due &amp; wrong book →</a></div>";
      const pc = document.getElementById("progress"); if (pc) pc.hidden = false;
    }
    document.querySelectorAll(".card-prog[data-ch]").forEach((el) => {
      const o = byCh[el.dataset.ch]; if (!o) return;
      const pct = o.total ? Math.round((100 * o.done) / o.total) : 0;
      el.innerHTML = miniRing(pct, 38);
      el.title = o.done + " / " + o.total + " reviewed";
      el.classList.toggle("has-prog", o.done > 0);
    });
    const byExam = examStats();
    document.querySelectorAll(".card-prog[data-exam]").forEach((el) => {
      const o = byExam[el.dataset.exam]; if (!o) return;
      const pct = o.total ? Math.round((100 * o.done) / o.total) : 0;
      el.innerHTML = miniRing(pct, 38);
      el.title = o.done + " / " + o.total + " reviewed";
      el.classList.toggle("has-prog", o.done > 0);
    });
    document.querySelectorAll(".ch-progress").forEach((el) => {
      const o = byCh[el.dataset.ch]; if (!o) return;
      const pct = o.total ? Math.round((100 * o.done) / o.total) : 0;
      const dueIds = Store.dueList(INDEX.filter((e) => e.c === el.dataset.ch).map((e) => e.a)).length;
      el.innerHTML =
        "<div class='chp-head'><span class='chp-label'>Reviewed</span>" +
        "<span class='chp-num'>" + o.done + " / " + o.total + "</span></div>" +
        "<span class='pbar-track'><span class='pbar-fill' style='width:" + pct + "%'></span></span>" +
        (dueIds ? "<a class='chp-due' href='../review.html'>" + dueIds + " due today →</a>" : "");
    });
  }
  renderProgressUI();
  // called by CloudSync after a cloud merge so the UI reflects synced data
  window.refreshStudyUI = function () { applyAllStudy(); renderProgressUI(); };

  // ---- review page: due-today (Ebbinghaus) + wrong book + export/import ----
  const reviewBody = document.getElementById("reviewpage-body");
  if (reviewBody) {
    const byId = {}; INDEX.forEach((e) => (byId[e.a] = e));
    const item = (e, action) =>
      "<div class='ghit ghit-row'><a class='ghit-main' href='" + qHref(e) + "'>" +
      "<span class='ghit-tag'>" + (TYPE[e.t] || e.t) + "</span>" +
      "<span class='ghit-q'>" + esc(e.q) + "</span>" +
      "<span class='ghit-meta'>" + esc(e.ct) + " · " + esc(e.kp) + " · " + esc(e.src) + "</span></a>" + action + "</div>";
    function render() {
      const due = Store.dueList(Object.keys(byId)).map((id) => byId[id]).filter(Boolean);
      const wrong = Store.wrongIds().map((id) => byId[id]).filter(Boolean);
      let html = "<h1 class='tp-title'>Review</h1><p class='tp-sub'>Spaced-repetition queue and your wrong book — saved in this browser.</p>";
      html += "<h2 class='tp-ch'>🧠 Due today <span class='cnt'>" + due.length + "</span></h2>";
      html += due.length ? "<div class='tp-list'>" + due.map((e) =>
        item(e, "<button class='io-btn rev-now' data-id='" + e.a + "'>✓ Reviewed</button>")).join("") + "</div>"
        : "<p class='tp-empty'>Nothing due — mark questions “Reviewed” to schedule them.</p>";
      html += "<h2 class='tp-ch'>★ Wrong book <span class='cnt'>" + wrong.length + "</span></h2>";
      html += wrong.length ? "<div class='tp-list'>" + wrong.map((e) =>
        item(e, "<button class='io-btn rm-wrong' data-id='" + e.a + "'>Remove</button>")).join("") + "</div>"
        : "<p class='tp-empty'>Empty — multiple-choice you answer wrong land here automatically.</p>";
      reviewBody.innerHTML = html;
      reviewBody.querySelectorAll(".rev-now").forEach((b) => b.addEventListener("click", () => { Store.setReviewed(b.dataset.id, true); render(); }));
      reviewBody.querySelectorAll(".rm-wrong").forEach((b) => b.addEventListener("click", () => { Store.setWrong(b.dataset.id, false); render(); }));
    }
    render();
    const exp = document.getElementById("exportBtn");
    if (exp) exp.addEventListener("click", () => {
      const blob = new Blob([Store.exportBlob()], { type: "application/json" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob); a.download = "i2dl-progress.json"; a.click();
      URL.revokeObjectURL(a.href);
    });
    const imp = document.getElementById("importFile");
    if (imp) imp.addEventListener("change", () => {
      const f = imp.files[0]; if (!f) return;
      const r = new FileReader();
      r.onload = () => { try { Store.importBlob(r.result); render(); alert("Progress imported."); } catch (e) { alert("Invalid file."); } };
      r.readAsText(f);
    });
  }

  // ---- back-to-top button (mobile) ----
  const toTop = document.getElementById("toTop");
  if (toTop) {
    const onScroll = () => { toTop.hidden = window.scrollY < 400; };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    toTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
  }

  // ---- mobile: collapse the TOC panel after tapping a topic link ----
  const tocWrap = document.querySelector(".toc-wrap");
  if (tocWrap) {
    tocWrap.querySelectorAll(".toc a").forEach((a) =>
      a.addEventListener("click", () => {
        if (window.matchMedia("(max-width:860px)").matches) tocWrap.open = false;
      })
    );
  }

  const expandBtn = document.getElementById("expandAll");
  if (expandBtn) {
    expandBtn.addEventListener("click", () => {
      const qs = Array.from(document.querySelectorAll("details.q")).filter((q) => !q.hidden);
      const anyClosed = qs.some((q) => !q.open);
      qs.forEach((q) => (q.open = anyClosed));
      expandBtn.textContent = anyClosed ? "Collapse all" : "Expand all";
    });
  }

  // ===================================================================
  // Cloud sync (Firebase) — localStorage stays primary; this batches the
  // single progress doc per user (push on 30s interval / tab hide).
  // ===================================================================
  const CFG = window.APP_CONFIG || {};
  const CloudSync = (function () {
    const FB = "https://www.gstatic.com/firebasejs/10.12.2/";
    let db = null, uid = null, ready = false, dirty = false;
    const load = (src) => new Promise((res, rej) => {
      const s = document.createElement("script"); s.src = src; s.onload = res; s.onerror = rej;
      document.head.appendChild(s);
    });
    function mergeProgress(local, cloud) { // union; local (this device) wins on conflict
      const out = {};
      ["reviewed", "wrong", "srs", "activity", "notes"].forEach((k) => {
        out[k] = Object.assign({}, cloud[k] || {}, local[k] || {});
      });
      return out;
    }
    function pushNow() {
      if (!ready || !uid) return;
      dirty = false;
      db.collection("users").doc(uid).set({ progress: Store.data(), updated: Date.now() }, { merge: true })
        .catch((e) => console.warn("cloud push failed", e));
    }
    async function pullMergePush() {
      try {
        const doc = await db.collection("users").doc(uid).get();
        const cloud = doc.exists ? (doc.data().progress || {}) : {};
        const merged = mergeProgress(Store.data(), cloud);
        Store.importBlob(JSON.stringify(merged));         // updates local + persists
        await db.collection("users").doc(uid).set({ progress: merged, updated: Date.now() }, { merge: true });
        if (window.refreshStudyUI) window.refreshStudyUI();
      } catch (e) { console.warn("cloud pull failed", e); }
    }
    setInterval(() => { if (dirty) pushNow(); }, 30000);
    window.addEventListener("visibilitychange", () => { if (document.hidden && dirty) pushNow(); });
    window.addEventListener("beforeunload", () => { if (dirty) pushNow(); });
    function renderAuth(user) {
      const el = document.getElementById("authctl");
      if (!el) return;
      if (user) {
        el.innerHTML = "<span class='auth-on'>☁ Synced · " + esc(user.email || user.displayName || "signed in") +
          "</span><button type='button' class='auth-btn' id='signoutBtn'>Sign out</button>";
        el.querySelector("#signoutBtn").addEventListener("click", (ev) => { ev.preventDefault(); ev.stopPropagation(); API.signOut(); });
      } else {
        el.innerHTML = "<button type='button' class='auth-btn primary' id='signinBtn'>Sign in to sync</button>";
        el.querySelector("#signinBtn").addEventListener("click", (ev) => { ev.preventDefault(); ev.stopPropagation(); API.signIn(); });
      }
    }
    const API = {
      schedule() { dirty = true; },        // called by Store.persist()
      async init(cfg) {
        try {
          await load(FB + "firebase-app-compat.js");
          const extra = [load(FB + "firebase-auth-compat.js"), load(FB + "firebase-firestore-compat.js")];
          if (cfg.databaseURL) extra.push(load(FB + "firebase-database-compat.js"));
          await Promise.all(extra);
          firebase.initializeApp(cfg);
          db = firebase.firestore();
          if (cfg.databaseURL) Presence.start();
          firebase.auth().onAuthStateChanged(async (user) => {
            if (user) { uid = user.uid; ready = true; await pullMergePush(); renderAuth(user); }
            else { uid = null; ready = false; renderAuth(null); }
          });
        } catch (e) { console.warn("Firebase init failed", e); }
      },
      signIn() { firebase.auth().signInWithPopup(new firebase.auth.GoogleAuthProvider()).catch((e) => alert("Sign-in failed: " + e.message)); },
      signOut() { if (dirty) pushNow(); firebase.auth().signOut(); },
    };
    return API;
  })();
  window.CloudSync = CloudSync;

  // ===================================================================
  // Presence — live "people online now" banner via Realtime Database.
  // Each open tab pushes a child under /presence and removes it on
  // disconnect (Firebase server-side onDisconnect), so the count tracks
  // real concurrent visitors without any backend.
  // ===================================================================
  const Presence = (function () {
    function render(n) {
      const el = document.getElementById("presence-bar");
      if (!el) return;
      const others = Math.max(0, n - 1);
      el.textContent = others > 0
        ? "🟢 You are not alone! " + others + (others === 1 ? " other person is" : " others are") + " studying right now"
        : "🟢 You're the only one studying right now — keep going!";
      el.classList.add("show");
    }
    function start() {
      try {
        const dbRT = firebase.database();
        const listRef = dbRT.ref("presence");
        const connRef = dbRT.ref(".info/connected");
        let myRef = null;
        connRef.on("value", (snap) => {
          if (snap.val() !== true) return;
          myRef = listRef.push();
          myRef.onDisconnect().remove();
          myRef.set({ t: firebase.database.ServerValue.TIMESTAMP });
        });
        listRef.on("value", (snap) => render(snap.numChildren()));
      } catch (e) { console.warn("Presence init failed", e); }
    }
    return { start };
  })();

  if (CFG.firebase && CFG.firebase.apiKey) {
    const a = document.getElementById("authctl");
    if (a) a.innerHTML = "<span class='auth-load'>☁ sync loading…</span>";
    CloudSync.init(CFG.firebase);
  }

  // ---- feedback link (opens the Google Form in a new tab) ----
  const fbLink = document.getElementById("feedback-link");
  if (fbLink && CFG.feedbackFormUrl) {
    fbLink.href = CFG.feedbackFormUrl.replace("?embedded=true", "");
  } else if (fbLink) {
    fbLink.textContent = "Feedback form not configured yet";
    fbLink.removeAttribute("href");
  }

  // ---- share button: copy the site link so users can send it to a friend ----
  document.querySelectorAll(".share-pill").forEach((btn) => {
    const txt = btn.querySelector(".share-txt");
    btn.addEventListener("click", async () => {
      const url = btn.dataset.share || location.href;
      let ok = false;
      try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(url); ok = true;
        } else {
          const ta = document.createElement("textarea");
          ta.value = url; ta.style.position = "fixed"; ta.style.opacity = "0";
          document.body.appendChild(ta); ta.focus(); ta.select();
          ok = document.execCommand("copy"); document.body.removeChild(ta);
        }
      } catch (e) { ok = false; }
      if (!txt) return;
      const orig = btn.dataset.label || (btn.dataset.label = txt.textContent);
      txt.textContent = ok ? "Copied — paste & send! 🎉" : "Press Ctrl+C to copy";
      btn.classList.toggle("copied", ok);
      clearTimeout(btn._t);
      btn._t = setTimeout(() => { txt.textContent = orig; btn.classList.remove("copied"); }, 1800);
    });
  });

  // ---- topbar "you are here" pill + floating contents popover ----------
  //  The pill always shows the section currently in view (scroll-spy); tapping
  //  it opens a floating panel that is the full table of contents.
  // Reusable: wire the topbar pill + popover for whatever section links are
  // currently inside #tocPop. Called on chapter pages (server-rendered links)
  // and again on tag/exam pages once their sections are rendered by JS.
  function setupContentsPill() {
    const pill = document.getElementById("nowAt");
    const pop = document.getElementById("tocPop");
    const here = pill && pill.querySelector(".nowat-here");
    if (!pill || !pop) return;
    const wrap = pill.closest(".nowat-wrap");
    const links = Array.from(pop.querySelectorAll("a[href^='#']"));
    if (!links.length) { if (wrap) wrap.hidden = true; return; }  // nothing to navigate → hide pill
    if (wrap) wrap.hidden = false;

    // position the panel: on phones make it a full-width dropdown pinned to the
    // viewport (titles wrap to the screen width, nothing clips); on desktop keep
    // it under the pill but nudged left so it never runs off the right edge.
    const place = () => {
      if (window.innerWidth <= 700) {
        const pr = pill.getBoundingClientRect();
        pop.style.position = "fixed";
        pop.style.left = "8px";
        pop.style.right = "8px";
        pop.style.width = "auto";
        pop.style.maxWidth = "none";
        pop.style.top = Math.round(pr.bottom + 6) + "px";
      } else {
        pop.style.position = "";
        pop.style.right = "";
        pop.style.top = "";
        pop.style.width = "";
        pop.style.maxWidth = "";
        pop.style.left = "0px";
        const r = pop.getBoundingClientRect();
        const m = 8;
        let shift = 0;
        if (r.right > window.innerWidth - m) shift = (window.innerWidth - m) - r.right;
        if (r.left + shift < m) shift = m - r.left;
        pop.style.left = shift + "px";
      }
    };
    // open / close the floating contents panel
    const setOpen = (on) => {
      pop.hidden = !on;
      pill.setAttribute("aria-expanded", on ? "true" : "false");
      if (on) place();
    };
    if (!pill.dataset.wired) {                       // attach one-time listeners once
      pill.dataset.wired = "1";
      window.addEventListener("resize", () => { if (!pop.hidden) place(); });
      pill.addEventListener("click", (e) => { e.stopPropagation(); setOpen(pop.hidden); });
      pop.addEventListener("click", (e) => { if (e.target.closest("a")) setOpen(false); });
      document.addEventListener("click", (e) => {
        if (!pop.hidden && !pop.contains(e.target) && !pill.contains(e.target)) setOpen(false);
      });
      document.addEventListener("keydown", (e) => { if (e.key === "Escape") setOpen(false); });
    }

    // scroll-spy: reflect the section in view onto the pill + popover highlight
    const linkFor = new Map();
    links.forEach((a) => {
      const el = document.getElementById(decodeURIComponent(a.getAttribute("href").slice(1)));
      if (el) linkFor.set(el, a);
    });
    let active = null;
    const setActive = (a) => {
      if (!a || a === active) return;
      if (active) active.classList.remove("active");
      active = a;
      active.classList.add("active");
      if (here) {                                   // mirror onto the pill label
        here.textContent = "";
        const n = a.querySelector(".toc-num");
        if (n) {
          const s = document.createElement("span");
          s.className = "nowat-n";
          s.textContent = n.textContent;
          here.appendChild(s);
        }
        const lbl = a.querySelector(".toc-label");
        here.appendChild(document.createTextNode(lbl ? lbl.textContent : a.textContent));
      }
      if (!pop.hidden && active.scrollIntoView) active.scrollIntoView({ block: "nearest" });
    };

    if ("IntersectionObserver" in window) {
      if (pill._io) pill._io.disconnect();          // drop any previous observer on re-init
      const io = new IntersectionObserver((entries) => {
        const vis = entries.filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (vis.length) setActive(linkFor.get(vis[0].target));
      }, { rootMargin: "-80px 0px -65% 0px", threshold: 0 });
      linkFor.forEach((a, el) => io.observe(el));
      pill._io = io;
    }
    setActive(links[0]);                            // initial label before scrolling
  }

  // slugify a chapter title into a stable anchor id
  function slug(s) {
    return String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
  }

  // Build the popover list from rendered chapter-groups, then (re)wire the pill.
  // groups: [{ id, title, n }]
  function buildContents(groups) {
    const pop = document.getElementById("tocPop");
    if (!pop) return;
    pop.innerHTML = "<ol>" + groups.map((g) =>
      "<li><a href='#" + g.id + "'><span class='toc-label'>" + esc(g.title) +
      "</span><span class='toc-n'>" + g.n + "</span></a></li>"
    ).join("") + "</ol>";
    setupContentsPill();
  }

  setupContentsPill();   // chapter pages: section links are server-rendered
})();
