import { Store } from "./store";

// One-time study-data key migration for questions merged during the 2026-06
// de-duplication pass. Each removed duplicate's stable id (qid) is remapped onto
// the kept question's id so a user's reviewed / wrong book / notes / SRS data is
// preserved rather than orphaned in localStorage / the cloud doc.
//
// Idempotent and flag-free: once the old ids are gone (after the first run) it
// is a cheap no-op, so it is safe to call again after a cloud merge that may
// re-introduce old ids from another device.

// removed-duplicate qid -> kept-question qid
const MERGES: Record<string, string> = {
  qa60f0bdd5: "qeca844220", // tasks: Semantic Segmentation MC (SS23 1.6)
  qebd4ef4e1: "q35e2044ff", // unsupervised-methods: methods usable unsupervised (WS22 1.9)
  qf2c96721a: "qaf97415fe", // splits: purpose of train/val/test (WS22 8.1)
  qc99bf7b58: "q5273dd05f", // splits: k-fold larger k disadvantage (WS21 2.1)
  q7980ca4cb: "q9847ef86e", // shuffle-distribution: Amazon photos domain gap (WS22 8.4)
  q81bf83edb: "q95e7fe4f3", // augmentation: MNIST suitable augmentations (WS21 1.1)
  qf4f8e72d8: "q64db63b98", // augmentation: augmentation statements (SS23 1.8)
  q901f6bd33: "qa64fbe4b6", // dataloaders: __getitem__ / DataLoader (SS23 7.5)
  qcc1f9174b: "qbe48ab1a9", // regression-loss: final activations for [-1,1] (WS23 1.6)
  q54666f58c: "q83e9148e7", // conv-def: single-filter param count (SS24 2.8)
  q640ac25d5: "q0867bdac8", // conv-def: what affects output shape (WS23 1.8)
  q60971c7c9: "qc856181a3", // weight-init: Xavier weights/variance (SS21 2.4)
  qb9cb3ecd4: "qba9be6d52", // positional-encoding: why PE in transformers (WS23 2.2)
  q693fd3af5: "q916edb6fa", // splits: how to split dataset (WS26 P3a)
};

const PAIRS = Object.entries(MERGES) as [string, string][];

export function runMigrations(): void {
  try {
    Store.migrate(PAIRS);
  } catch {
    /* never block page init on a migration hiccup */
  }
}
