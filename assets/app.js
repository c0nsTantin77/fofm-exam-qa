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
