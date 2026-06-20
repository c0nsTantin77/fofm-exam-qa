import { Store } from "./store";
import { applyAllStudy } from "./study";

// Self-test for open / AI short-answer questions: the reference answer is hidden
// until "Show answer". If the student typed an attempt, the key terms of the
// reference (its **bold** spans) are scored against their text — hit terms turn
// green, missed ones red — and they self-assess (Got it → reviewed, Missed →
// wrong book). There is no single ground truth, so grading stays a self-check.

const STOP = new Set([
  "the", "a", "an", "of", "to", "is", "are", "and", "or", "in", "on", "for", "with",
  "as", "it", "its", "by", "be", "that", "this", "which", "not", "no", "also", "can",
  "used", "use", "using", "via", "your", "you", "we", "they", "their", "from", "at",
]);

const norm = (s: string): string =>
  s.toLowerCase().replace(/[^a-z0-9\s]/g, " ").replace(/\s+/g, " ").trim();

const reEsc = (s: string): string => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

/** Does the user's text cover this reference key term? */
function termHit(term: string, userNorm: string): boolean {
  const t = norm(term);
  if (!t) return false;
  if (userNorm.includes(t)) return true;
  const words = t.split(" ").filter((w) => w.length >= 4 && !STOP.has(w));
  if (!words.length) return false;
  return words.every((w) => new RegExp("\\b" + reEsc(w)).test(userNorm));
}

export function initOpenAnswer(root: ParentNode = document): void {
  root.querySelectorAll<HTMLElement>(".selftest").forEach((st) => {
    if (st.dataset.wired) return;
    st.dataset.wired = "1";
    const qel = st.closest("details.q") as HTMLElement | null;
    if (!qel) return;
    const id = qel.id;
    const ta = st.querySelector<HTMLTextAreaElement>(".self-area");
    const revealBtn = st.querySelector<HTMLButtonElement>(".reveal-btn");
    const reveal = st.querySelector<HTMLElement>(".open-reveal");
    const score = st.querySelector<HTMLElement>(".self-score");
    const assess = st.querySelector<HTMLElement>(".self-assess");
    if (!revealBtn || !reveal) return;

    revealBtn.addEventListener("click", () => {
      reveal.hidden = false;
      revealBtn.hidden = true;
      if (assess) assess.hidden = false;
      if (ta) ta.readOnly = true;

      const userNorm = norm(ta?.value ?? "");
      if (!userNorm || !score) return;
      const terms = Array.from(reveal.querySelectorAll<HTMLElement>(".answer strong"));
      if (!terms.length) return;
      let hit = 0;
      terms.forEach((el) => {
        const ok = termHit(el.textContent ?? "", userNorm);
        el.classList.add(ok ? "kw-hit" : "kw-miss");
        if (ok) hit++;
      });
      score.hidden = false;
      score.textContent = `You covered ${hit} / ${terms.length} key points — green = hit, red = missed.`;
      score.classList.toggle("good", hit >= Math.ceil(terms.length / 2));
    });

    const choose = (kind: "got" | "miss"): void => {
      if (kind === "got") Store.setReviewed(id, true);
      else Store.setWrong(id, true);
      if (assess) assess.dataset.done = kind;
      applyAllStudy();
    };
    assess?.querySelector(".got-btn")?.addEventListener("click", () => choose("got"));
    assess?.querySelector(".miss-btn")?.addEventListener("click", () => choose("miss"));
  });
}
