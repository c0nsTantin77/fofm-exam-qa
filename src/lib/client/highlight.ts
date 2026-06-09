// Search-keyword highlighting, shared by the homepage search island (string /
// v-html) and the chapter-page filter (live DOM). Matches are wrapped in
// <mark class="ghit-hl"> (soft-yellow + bold-italic, styled in home.css).

const HL_CLASS = "ghit-hl";

export const escapeHtml = (s: string): string =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

export const escapeRe = (s: string): string => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

/** String highlight for already-plain text (homepage results, via v-html).
 *  `needles` are the search words; each occurrence is wrapped. */
export function highlightHtml(text: string, needles: string[]): string {
  const esc = escapeHtml(text);
  const ws = needles.filter(Boolean).map(escapeRe);
  if (!ws.length) return esc;
  const re = new RegExp("(" + ws.join("|") + ")", "gi");
  return esc.replace(re, `<mark class="${HL_CLASS}">$1</mark>`);
}

// ---- live DOM highlighting (chapter-page filter) ------------------------

/** Remove all highlight marks under `root`, merging the text back together. */
export function clearHighlights(root: HTMLElement): void {
  const marks = root.querySelectorAll("mark." + HL_CLASS);
  if (!marks.length) return;
  marks.forEach((m) => {
    m.parentNode?.replaceChild(document.createTextNode(m.textContent || ""), m);
  });
  root.normalize(); // merge adjacent text nodes so re-highlighting sees clean text
}

function isInside(node: Node, root: Node): boolean {
  // skip text already inside a KaTeX render (would corrupt the formula) or a mark
  let el = node.parentElement;
  while (el && el !== root) {
    if (el.tagName === "MARK" || el.classList.contains("katex")) return true;
    el = el.parentElement;
  }
  return false;
}

function wrapMatches(textNode: Text, lowerNeedle: string): void {
  const text = textNode.nodeValue || "";
  const lower = text.toLowerCase();
  let idx = lower.indexOf(lowerNeedle);
  if (idx === -1) return;
  const frag = document.createDocumentFragment();
  let last = 0;
  while (idx !== -1) {
    if (idx > last) frag.appendChild(document.createTextNode(text.slice(last, idx)));
    const mark = document.createElement("mark");
    mark.className = HL_CLASS;
    mark.textContent = text.slice(idx, idx + lowerNeedle.length);
    frag.appendChild(mark);
    last = idx + lowerNeedle.length;
    idx = lower.indexOf(lowerNeedle, last);
  }
  if (last < text.length) frag.appendChild(document.createTextNode(text.slice(last)));
  textNode.parentNode?.replaceChild(frag, textNode);
}

/** Highlight every occurrence of `needle` (a literal substring) inside the given
 *  containers, skipping KaTeX. Collect first, then mutate (don't edit mid-walk). */
export function highlightIn(containers: HTMLElement[], needle: string): void {
  const lower = needle.toLowerCase();
  if (!lower) return;
  for (const container of containers) {
    const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        const v = node.nodeValue;
        if (!v || !v.trim()) return NodeFilter.FILTER_REJECT;
        if (isInside(node, container)) return NodeFilter.FILTER_REJECT;
        return v.toLowerCase().includes(lower) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
      },
    });
    const targets: Text[] = [];
    let n: Node | null;
    while ((n = walker.nextNode())) targets.push(n as Text);
    for (const t of targets) wrapMatches(t, lower);
  }
}
