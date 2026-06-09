<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from "vue";
import type { SearchEntry } from "../../lib/types";
import { loadIndex, questionHref } from "../../lib/client/index-data";
import { url } from "../../lib/paths";
import { slug, buildContents, type ContentsGroup } from "../../lib/client/contents";
import { EXAM_NAMES, examOf, labelOf } from "../../lib/exams";

const index = ref<SearchEntry[]>([]);
const loaded = ref(false);
const current = ref<string | null>(null);

const counts = computed(() => {
  const c: Record<string, number> = {};
  index.value.forEach((e) => {
    const seen = new Set<string>();
    (e.srcs || []).forEach((s) => {
      const x = examOf(s);
      if (x && !seen.has(x)) {
        seen.add(x);
        c[x] = (c[x] || 0) + 1;
      }
    });
  });
  return c;
});

const activeExam = computed(() =>
  current.value && counts.value[current.value] ? current.value : null,
);

const hits = computed(() => {
  if (!activeExam.value) return [];
  const ex = activeExam.value;
  const list = index.value.filter((e) => (e.srcs || []).some((s) => examOf(s) === ex));
  const num = (e: SearchEntry) => {
    const s = (e.srcs || []).find((x) => examOf(x) === ex) || "";
    const m = labelOf(s).match(/(\d+)\.?(\d+)?/);
    return m ? parseInt(m[1]) * 100 + parseInt(m[2] || "0") : 9999;
  };
  return [...list].sort((a, b) => num(a) - num(b));
});

interface Group extends ContentsGroup {
  entries: SearchEntry[];
}
const byChapter = computed<Group[]>(() => {
  const map = new Map<string, SearchEntry[]>();
  hits.value.forEach((e) => {
    if (!map.has(e.ct)) map.set(e.ct, []);
    map.get(e.ct)!.push(e);
  });
  return [...map.entries()].map(([ct, entries]) => ({
    id: "sec-" + slug(ct),
    title: ct,
    n: entries.length,
    entries,
  }));
});

const examName = computed(() =>
  activeExam.value ? EXAM_NAMES[activeExam.value] ?? activeExam.value : "",
);

const tagFor = (e: SearchEntry) => {
  const ex = activeExam.value!;
  const lbl = (e.srcs || [])
    .filter((s) => examOf(s) === ex)
    .map(labelOf)
    .join(", ");
  return `${ex} ${lbl}`;
};

onMounted(async () => {
  index.value = await loadIndex();
  current.value = new URLSearchParams(location.search).get("e");
  if (!activeExam.value) {
    // bare exams page is redundant with the homepage "By exam" view
    location.replace(url("/") + "#by-exam");
    return;
  }
  loaded.value = true;
  document.title = activeExam.value + " · Browse by exam · I2DL";
  await nextTick();
  buildContents(byChapter.value.map((g) => ({ id: g.id, title: g.title, n: g.n })));
});
</script>

<template>
  <div v-if="!loaded"><p class="hint">Loading…</p></div>
  <div v-else>
    <h1 class="tp-title">{{ examName }} <span class="tag">{{ activeExam }}</span></h1>
    <p class="tp-sub">
      {{ hits.length }} question{{ hits.length > 1 ? "s" : "" }} across {{ byChapter.length }}
      chapter(s).
    </p>
    <template v-for="g in byChapter" :key="g.id">
      <h2 class="tp-ch" :id="g.id">{{ g.title }}</h2>
      <div class="tp-list">
        <a v-for="e in g.entries" :key="e.a" class="ghit" :href="questionHref(e)">
          <span class="ghit-tag">{{ tagFor(e) }}</span>
          <span class="ghit-q">{{ e.q }}</span>
          <span class="ghit-meta">{{ e.kp }}</span>
        </a>
      </div>
    </template>
  </div>
</template>
