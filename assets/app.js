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

    const anyChecked = () => inputs.some((i) => i.checked);
    inputs.forEach((i) =>
      i.addEventListener("change", () => {
        if (!quiz.classList.contains("done")) checkBtn.disabled = !anyChecked();
      })
    );

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
      checkBtn.disabled = true;
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

  // ---- global site-wide search (index page only) ----
  const gbox = document.getElementById("gsearch");
  const gres = document.getElementById("gresults");
  if (gbox && gres) {
    let index = null, loading = false;
    const TYPE = { mc: "MC", open: "Open", ai: "AI" };
    async function ensureIndex() {
      if (index || loading) return;
      loading = true;
      try {
        const r = await fetch("search-index.json");
        index = await r.json();
      } catch (e) { index = []; }
      loading = false;
    }
    function runSearch() {
      const term = gbox.value.trim().toLowerCase();
      if (!term) { gres.hidden = true; gres.innerHTML = ""; return; }
      const words = term.split(/\s+/);
      const hits = (index || []).filter((e) => words.every((w) => e.txt.includes(w))).slice(0, 40);
      if (!hits.length) {
        gres.innerHTML = "<div class='gempty'>No questions match “" + gbox.value + "”.</div>";
      } else {
        gres.innerHTML = hits.map((e) =>
          "<a class='ghit' href='chapters/" + e.c + ".html#" + e.a + "'>" +
          "<span class='ghit-tag'>" + (TYPE[e.t] || e.t) + "</span>" +
          "<span class='ghit-q'>" + e.q.replace(/</g, "&lt;") + "</span>" +
          "<span class='ghit-meta'>" + e.kp + " · " + e.src + "</span></a>"
        ).join("");
      }
      gres.hidden = false;
    }
    gbox.addEventListener("focus", ensureIndex);
    gbox.addEventListener("input", async () => { await ensureIndex(); runSearch(); });
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
