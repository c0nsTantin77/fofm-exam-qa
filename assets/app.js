// I2DL Exam Q&A — client interactions: KaTeX render, search & type filter.
(function () {
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
      if (!hits.length) {
        gres.innerHTML = "<div class='gempty'>No questions match “" + esc(gbox.value) + "”.</div>";
      } else {
        gres.innerHTML =
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
      Object.keys(byChapter).forEach((ct) => {
        html += "<h2 class='tp-ch'>" + esc(ct) + "</h2><div class='tp-list'>" +
          byChapter[ct].map((e) =>
            "<a class='ghit' href='" + qHref(e) + "'>" +
            "<span class='ghit-tag'>" + (TYPE[e.t] || e.t) + "</span>" +
            "<span class='ghit-q'>" + esc(e.q) + "</span>" +
            "<span class='ghit-meta'>" + esc(e.kp) + " · " + esc(e.src) + "</span></a>"
          ).join("") + "</div>";
      });
      tagPage.innerHTML = html;
    }

    if (current && counts[current]) renderTag(current); else renderOverview();
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
})();
