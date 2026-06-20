import { Store } from "./store";
import { applyAllStudy } from "./study";

// Self-test for open / AI short-answer questions: the reference answer is hidden
// behind "Show answer" with an optional "write your answer" box, mirroring the
// MC quiz flow. After revealing, the student self-assesses (Got it → reviewed,
// Missed → wrong book) and can "Try again" to re-attempt. There is no single
// ground truth, so this stays a self-check (no auto-grading).

export function initOpenAnswer(root: ParentNode = document): void {
  root.querySelectorAll<HTMLElement>(".selftest").forEach((st) => {
    if (st.dataset.wired) return;
    st.dataset.wired = "1";
    const qel = st.closest("details.q") as HTMLElement | null;
    if (!qel) return;
    const id = qel.id;
    const ta = st.querySelector<HTMLTextAreaElement>(".self-area");
    const revealBtn = st.querySelector<HTMLButtonElement>(".reveal-btn");
    const againBtn = st.querySelector<HTMLButtonElement>(".self-again");
    const reveal = st.querySelector<HTMLElement>(".open-reveal");
    const assess = st.querySelector<HTMLElement>(".self-assess");
    if (!revealBtn || !reveal) return;

    const show = (): void => {
      reveal.hidden = false;
      revealBtn.hidden = true;
      if (againBtn) againBtn.hidden = false;
      if (assess) assess.hidden = false;
      if (ta) ta.readOnly = true;
    };
    const reset = (): void => {
      reveal.hidden = true;
      revealBtn.hidden = false;
      if (againBtn) againBtn.hidden = true;
      if (assess) {
        assess.hidden = true;
        delete assess.dataset.done;
      }
      if (ta) {
        ta.readOnly = false;
        ta.focus();
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
