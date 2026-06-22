import { Store } from "./store";
import { applyAllStudy } from "./study";

// Self-test for open / AI short-answer questions: the reference answer is hidden
// behind "Show answer" with an optional "write your answer" box, mirroring the
// MC quiz flow. On reveal, the reference's **bold** key terms are scored against
// the student's text — terms they wrote turn green (hit), terms they missed turn
// red — then they self-assess (Got it → reviewed, Missed → wrong book) and can
// "Try again" to re-attempt. There is no single ground truth, so this stays a
// self-check (no auto-grading / no pass-fail).

const STOP = new Set([
  "the", "a", "an", "of", "to", "is", "are", "and", "or", "in", "on", "for", "with",
  "as", "it", "its", "by", "be", "that", "this", "which", "not", "no", "also", "can",
  "used", "use", "using", "via", "your", "you", "we", "they", "their", "from", "at",
  "any", "all", "one", "two", "each", "per", "must", "may", "only", "more", "less",
]);

const norm = (s: string): string =>
  s.toLowerCase().replace(/[^a-z0-9\s]/g, " ").replace(/\s+/g, " ").trim();
const reEsc = (s: string): string => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

const EMPH = new Set(["not", "true", "false", "yes", "no", "both", "all", "none"]);

/** Turn a reference **bold** span into a comparable key term, or null if it is a
 *  label / scoring marker / emphasis word / whole sentence rather than a term
 *  worth scoring (e.g. "Training (1p):", "Three are correct:", "Not"). */
function cleanTerm(raw: string): string | null {
  const trimmed = raw.trim();
  if (/[:：]\s*$/.test(trimmed)) return null; // labels end with a colon
  const t = trimmed
    .replace(/\(\s*\d+(?:\.\d+)?\s*p\s*\)/gi, "") // drop "(1p)" / "(0.5p)" scoring marks
    .replace(/[.,;]+\s*$/, "")
    .trim();
  if (!t || !/[a-zA-Z]/.test(t)) return null;
  const words = t.split(/\s+/).filter(Boolean);
  if (words.length > 5) return null; // sentence-like, not a term
  if (words.length === 1 && (t.length < 3 || EMPH.has(t.toLowerCase()))) return null;
  return t;
}

/** Does the student's text cover this key term? */
function termHit(term: string, userNorm: string): boolean {
  const t = norm(term);
  if (!t) return false;
  if (userNorm.includes(t)) return true;
  const words = t.split(" ").filter((w) => w.length >= 3 && !STOP.has(w));
  if (!words.length) return new RegExp("(^| )" + reEsc(t) + "( |$)").test(userNorm);
  const present = words.filter((w) => new RegExp("(^| )" + reEsc(w)).test(userNorm)).length;
  return present >= Math.ceil(words.length * 0.6);
}

export function initOpenAnswer(root: ParentNode = document): void {
  root.querySelectorAll<HTMLElement>(".selftest").forEach((st) => {
    if (st.dataset.wired) return;
    st.dataset.wired = "1";
    const qel = st.closest("details.q") as HTMLElement | null;
    if (!qel) return;
    const id = qel.id;
    const ta = st.querySelector<HTMLTextAreaElement>(".self-area");
    const calcInputs = Array.from(st.querySelectorAll<HTMLInputElement>(".calc-in"));
    const revealBtn = st.querySelector<HTMLButtonElement>(".reveal-btn");
    const againBtn = st.querySelector<HTMLButtonElement>(".self-again");
    const reveal = st.querySelector<HTMLElement>(".open-reveal");
    const assess = st.querySelector<HTMLElement>(".self-assess");
    if (!revealBtn || !reveal) return;

    const strongs = (): HTMLElement[] =>
      Array.from(reveal.querySelectorAll<HTMLElement>(".answer strong"));

    const show = (): void => {
      reveal.hidden = false;
      revealBtn.hidden = true;
      if (againBtn) againBtn.hidden = false;
      if (assess) assess.hidden = false;
      if (ta) ta.readOnly = true;

      // calculation questions: check each typed number against its expected value
      calcInputs.forEach((inp) => {
        const exp = parseFloat(inp.dataset.val ?? "");
        const tol = Math.max(parseFloat(inp.dataset.tol ?? "0") || 0, 1e-9);
        const got = parseFloat((inp.value ?? "").replace(/[, ]/g, ""));
        const filled = inp.value.trim() !== "";
        const ok = filled && Number.isFinite(got) && Math.abs(got - exp) <= tol;
        inp.classList.toggle("ok", ok);
        inp.classList.toggle("bad", filled && !ok);
        const mark = inp.parentElement?.querySelector(".calc-mark");
        if (mark) mark.textContent = !filled ? "" : ok ? "✓" : "✗";
        inp.readOnly = true;
      });

      // highlight the reference's bold key terms vs what the student wrote:
      // green = they mentioned it, red = they missed it (no count — the bold
      // terms still need a manual curation pass before a score would be meaningful)
      const userNorm = norm(ta?.value ?? "");
      if (!userNorm) return;
      strongs().forEach((el) => {
        const term = cleanTerm(el.textContent ?? "");
        if (!term) return;
        el.classList.add(termHit(term, userNorm) ? "kw-hit" : "kw-miss");
      });
    };

    const reset = (): void => {
      reveal.hidden = true;
      revealBtn.hidden = false;
      if (againBtn) againBtn.hidden = true;
      if (assess) {
        assess.hidden = true;
        delete assess.dataset.done;
      }
      strongs().forEach((el) => el.classList.remove("kw-hit", "kw-miss"));
      calcInputs.forEach((inp) => {
        inp.readOnly = false;
        inp.classList.remove("ok", "bad");
        const mark = inp.parentElement?.querySelector(".calc-mark");
        if (mark) mark.textContent = "";
      });
      if (ta) {
        ta.readOnly = false;
        ta.focus();
      } else if (calcInputs[0]) {
        calcInputs[0].focus();
      }
    };

    revealBtn.addEventListener("click", show);
    againBtn?.addEventListener("click", reset);

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
