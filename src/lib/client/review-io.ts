import { Store } from "./store";

// Export / import the progress blob. The buttons live in the review-page
// topbar; the ReviewPage island refreshes itself via the store's onChange.

export function initReviewIO(): void {
  const exp = document.getElementById("exportBtn");
  if (exp) {
    exp.addEventListener("click", () => {
      const blob = new Blob([Store.exportBlob()], { type: "application/json" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "i2dl-progress.json";
      a.click();
      URL.revokeObjectURL(a.href);
    });
  }

  const imp = document.getElementById("importFile") as HTMLInputElement | null;
  if (imp) {
    imp.addEventListener("change", () => {
      const f = imp.files?.[0];
      if (!f) return;
      const r = new FileReader();
      r.onload = () => {
        try {
          Store.importBlob(String(r.result));
          alert("Progress imported.");
        } catch {
          alert("Invalid file.");
        }
      };
      r.readAsText(f);
    });
  }
}
