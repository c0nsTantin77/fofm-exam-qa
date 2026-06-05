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
