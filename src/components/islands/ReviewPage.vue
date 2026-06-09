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

const due = computed(() => {
  void version.value;
  return Store.dueList(Object.keys(byId.value))
    .map((id) => byId.value[id])
    .filter(Boolean);
});

const wrong = computed(() => {
  void version.value;
  return Store.wrongIds()
    .map((id) => byId.value[id])
    .filter(Boolean);
});

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
    <p class="tp-sub">Spaced-repetition queue and your wrong book — saved in this browser.</p>

    <h2 class="tp-ch">🧠 Due today <span class="cnt">{{ due.length }}</span></h2>
    <div v-if="due.length" class="tp-list">
      <div v-for="e in due" :key="e.a" class="ghit ghit-row">
        <a class="ghit-main" :href="questionHref(e)">
          <span class="ghit-tag">{{ TYPE_LABEL[e.t] || e.t }}</span>
          <span class="ghit-q">{{ e.q }}</span>
          <span class="ghit-meta">{{ e.ct }} · {{ e.kp }} · {{ e.src }}</span>
        </a>
        <button class="io-btn rev-now" @click="markReviewed(e.a)">✓ Reviewed</button>
      </div>
    </div>
    <p v-else class="tp-empty">Nothing due — mark questions “Reviewed” to schedule them.</p>

    <h2 class="tp-ch">★ Wrong book <span class="cnt">{{ wrong.length }}</span></h2>
    <div v-if="wrong.length" class="tp-list">
      <div v-for="e in wrong" :key="e.a" class="ghit ghit-row">
        <a class="ghit-main" :href="questionHref(e)">
          <span class="ghit-tag">{{ TYPE_LABEL[e.t] || e.t }}</span>
          <span class="ghit-q">{{ e.q }}</span>
          <span class="ghit-meta">{{ e.ct }} · {{ e.kp }} · {{ e.src }}</span>
        </a>
        <button class="io-btn rm-wrong" @click="removeWrong(e.a)">Remove</button>
      </div>
    </div>
    <p v-else class="tp-empty">
      Empty — multiple-choice you answer wrong land here automatically.
    </p>
  </div>
</template>
