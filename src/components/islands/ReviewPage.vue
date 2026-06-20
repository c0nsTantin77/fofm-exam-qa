<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import type { SearchEntry } from "../../lib/types";
import { loadIndex, questionHref, TYPE_LABEL } from "../../lib/client/index-data";
import { Store, onChange } from "../../lib/client/store";

const index = ref<SearchEntry[]>([]);
const loaded = ref(false);
const version = ref(0); // bumped to recompute when the store changes

const byId = computed(() => {
  const m: Record<string, SearchEntry> = {};
  index.value.forEach((e) => (m[e.a] = e));
  return m;
});

interface Group {
  c: string;
  ct: string;
  items: SearchEntry[];
}

/** Group entries by chapter, preserving the index's syllabus order. */
function groupByChapter(entries: SearchEntry[]): Group[] {
  const map = new Map<string, Group>();
  for (const e of entries) {
    let g = map.get(e.c);
    if (!g) {
      g = { c: e.c, ct: e.ct, items: [] };
      map.set(e.c, g);
    }
    g.items.push(e);
  }
  return [...map.values()];
}

const dueGroups = computed(() => {
  void version.value;
  const due = Store.dueList(Object.keys(byId.value))
    .map((id) => byId.value[id])
    .filter(Boolean);
  return groupByChapter(due);
});
const dueCount = computed(() => dueGroups.value.reduce((n, g) => n + g.items.length, 0));

const wrongGroups = computed(() => {
  void version.value;
  const w = Store.wrongIds()
    .map((id) => byId.value[id])
    .filter(Boolean);
  return groupByChapter(w);
});
const wrongCount = computed(() => wrongGroups.value.reduce((n, g) => n + g.items.length, 0));

// per-chapter reviewed progress, for the ring (mirrors the home-page rings)
const chapterTotals = computed(() => {
  const t: Record<string, number> = {};
  index.value.forEach((e) => (t[e.c] = (t[e.c] || 0) + 1));
  return t;
});
function ringPct(c: string): number {
  void version.value;
  const tot = chapterTotals.value[c] || 0;
  if (!tot) return 0;
  const done = index.value.filter((e) => e.c === c && Store.isReviewed(e.a)).length;
  return Math.round((100 * done) / tot);
}
const R = 16;
const CIRC = 2 * Math.PI * R;
const ringOffset = (pct: number): number => CIRC * (1 - pct / 100);

function dueLabel(id: string): string {
  void version.value;
  const d = Store.due(id);
  if (!d) return "";
  return d <= new Date().toISOString().slice(0, 10) ? "due now" : "next " + d;
}

function markReviewed(id: string): void {
  Store.setReviewed(id, true);
  version.value++;
}
function removeWrong(id: string): void {
  Store.setWrong(id, false);
  version.value++;
}

let unsub = () => {};
onMounted(async () => {
  index.value = await loadIndex();
  loaded.value = true;
  unsub = onChange(() => version.value++); // import / cloud merge → refresh
});
onUnmounted(() => unsub());
</script>

<template>
  <div v-if="!loaded"><p class="hint">Loading…</p></div>
  <div v-else>
    <h1 class="tp-title">Review</h1>
    <p class="tp-sub">
      Your spaced-repetition queue and wrong book — saved in this browser (and synced if you sign in).
    </p>

    <details class="rv-explain">
      <summary>How “Review” and the “Wrong book” fit together</summary>
      <ul>
        <li>
          <b>Mark “Reviewed”</b> on any question to start <b>spaced repetition</b> — it returns after
          1 → 2 → 4 → 7 → 15 → 30 → 60 days, the gap growing each time you review it.
        </li>
        <li>
          <b>Due today</b> is everything whose scheduled date has arrived. Review it, hit
          <b>✓ Reviewed</b>, and it’s pushed further out.
        </li>
        <li>
          <b>Wrong book</b> collects questions you got wrong (MC) or marked <b>Missed</b> (short
          answer). They stay until you remove them and resurface in “Due today” the next day.
        </li>
      </ul>
    </details>

    <section class="rv-section">
      <h2 class="rv-h rv-h-due">🧠 Due today <span class="rv-cnt">{{ dueCount }}</span></h2>
      <p v-if="!dueCount" class="tp-empty">Nothing due — mark questions “Reviewed” to schedule them.</p>
      <details v-for="g in dueGroups" :key="'d-' + g.c" class="rv-group" open>
        <summary class="rv-group-head">
          <svg class="rv-ring" viewBox="0 0 40 40" aria-hidden="true">
            <circle class="rv-ring-bg" cx="20" cy="20" :r="R" />
            <circle
              class="rv-ring-fg"
              cx="20"
              cy="20"
              :r="R"
              :style="{ strokeDasharray: CIRC, strokeDashoffset: ringOffset(ringPct(g.c)) }" />
            <text x="20" y="21" class="rv-ring-txt">{{ ringPct(g.c) }}</text>
          </svg>
          <span class="rv-group-title">{{ g.ct }}</span>
          <span class="rv-group-n">{{ g.items.length }} due</span>
        </summary>
        <div class="tp-list">
          <div v-for="e in g.items" :key="e.a" class="ghit ghit-row">
            <a class="ghit-main" :href="questionHref(e)">
              <span class="ghit-tag">{{ TYPE_LABEL[e.t] || e.t }}</span>
              <span class="ghit-q">{{ e.q }}</span>
              <span class="ghit-meta">{{ e.kp }} · {{ e.src }}</span>
            </a>
            <button class="io-btn rev-now" @click="markReviewed(e.a)">✓ Reviewed</button>
          </div>
        </div>
      </details>
    </section>

    <section class="rv-section">
      <h2 class="rv-h rv-h-wrong">★ Wrong book <span class="rv-cnt">{{ wrongCount }}</span></h2>
      <p v-if="!wrongCount" class="tp-empty">
        Empty — multiple-choice you answer wrong, or “Missed” on a short answer, lands here automatically.
      </p>
      <details v-for="g in wrongGroups" :key="'w-' + g.c" class="rv-group" open>
        <summary class="rv-group-head">
          <svg class="rv-ring" viewBox="0 0 40 40" aria-hidden="true">
            <circle class="rv-ring-bg" cx="20" cy="20" :r="R" />
            <circle
              class="rv-ring-fg"
              cx="20"
              cy="20"
              :r="R"
              :style="{ strokeDasharray: CIRC, strokeDashoffset: ringOffset(ringPct(g.c)) }" />
            <text x="20" y="21" class="rv-ring-txt">{{ ringPct(g.c) }}</text>
          </svg>
          <span class="rv-group-title">{{ g.ct }}</span>
          <span class="rv-group-n">{{ g.items.length }}</span>
        </summary>
        <div class="tp-list">
          <div v-for="e in g.items" :key="e.a" class="ghit ghit-row">
            <a class="ghit-main" :href="questionHref(e)">
              <span class="ghit-tag">{{ TYPE_LABEL[e.t] || e.t }}</span>
              <span class="ghit-q">{{ e.q }}</span>
              <span class="ghit-meta">
                {{ e.kp }} · {{ e.src }}
                <span v-if="dueLabel(e.a)" class="rv-due-pill">{{ dueLabel(e.a) }}</span>
              </span>
            </a>
            <button class="io-btn rm-wrong" @click="removeWrong(e.a)">Remove</button>
          </div>
        </div>
      </details>
    </section>
  </div>
</template>
