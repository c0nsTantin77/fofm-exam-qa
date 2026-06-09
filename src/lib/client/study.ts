import { Store } from "./store";

// Per-question study controls: Reviewed / wrong book / notes, all persisted via
// the Store (localStorage, optionally cloud-synced). Re-runnable so the UI can
// reflect synced state after a cloud merge.

const todayStr = () => new Date().toISOString().slice(0, 10);

/** (Re)reflect saved state onto one control bar. */
function applyStudy(bar: HTMLElement): void {
  const qel = bar.closest("details.q") as HTMLElement | null;
  if (!qel) return;
  const id = qel.id;
  const rev = bar.querySelector(".rev-box") as HTMLInputElement;
  const wrongBtn = bar.querySelector(".wrong-btn") as HTMLElement;
  const noteArea = bar.querySelector(".note-area") as HTMLTextAreaElement;
  const due = bar.querySelector(".srs-due") as HTMLElement;

  rev.checked = Store.isReviewed(id);
  wrongBtn.classList.toggle("on", Store.isWrong(id));
  if (!noteArea.matches(":focus")) noteArea.value = Store.note(id);
  qel.classList.toggle("has-note", !!Store.note(id));
  qel.classList.toggle("is-reviewed", Store.isReviewed(id));

  const d = Store.due(id);
  if (Store.isReviewed(id) && d) {
    const overdue = d <= todayStr();
    due.textContent = overdue ? "review due" : "next review " + d;
    due.className = "srs-due" + (overdue ? " over" : "");
  } else {
    due.textContent = "";
  }
}

export function initStudy(root: ParentNode = document): void {
  root.querySelectorAll<HTMLElement>(".study").forEach((bar) => {
    if (bar.dataset.wired) {
      applyStudy(bar);
      return;
    }
    bar.dataset.wired = "1";
    const qel = bar.closest("details.q") as HTMLElement | null;
    if (!qel) return;
    const id = qel.id;
    const rev = bar.querySelector(".rev-box") as HTMLInputElement;
    const wrongBtn = bar.querySelector(".wrong-btn") as HTMLElement;
    const noteBtn = bar.querySelector(".note-btn") as HTMLElement;
    const noteWrap = bar.querySelector(".note-wrap") as HTMLElement;
    const noteArea = bar.querySelector(".note-area") as HTMLTextAreaElement;

    applyStudy(bar);
    rev.addEventListener("change", () => {
      Store.setReviewed(id, rev.checked);
      applyStudy(bar);
    });
    wrongBtn.addEventListener("click", () => {
      Store.setWrong(id, !Store.isWrong(id));
      applyStudy(bar);
    });
    noteBtn.addEventListener("click", () => {
      noteWrap.hidden = !noteWrap.hidden;
      if (!noteWrap.hidden) noteArea.focus();
    });
    noteArea.addEventListener("input", () => {
      Store.setNote(id, noteArea.value.trim());
      applyStudy(bar);
    });
  });
}

export function applyAllStudy(): void {
  document.querySelectorAll<HTMLElement>(".study").forEach(applyStudy);
}
