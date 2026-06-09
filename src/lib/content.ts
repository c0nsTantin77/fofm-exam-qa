import { getCollection, type CollectionEntry } from "astro:content";
import { qid } from "./qid";
import { plain } from "./md";
import { readyChapters } from "./manifest";
import type { SearchEntry } from "./types";

export type { SearchEntry };

export type Chapter = CollectionEntry<"chapters">;
export type KnowledgePoint = Chapter["data"]["knowledge_points"][number];
export type Question = KnowledgePoint["questions"][number];

/** Render order: by exam frequency desc, stable (AI practice freq 0 sinks last).
 *  Array.sort is stable in modern engines, matching Python's stable sort.
 *  Generic so it accepts both the Astro-inferred and the explicit content type. */
export function sortedQuestions<T extends { freq: number }>(questions: T[]): T[] {
  return [...questions].sort((a, b) => b.freq - a.freq);
}

/** Ready chapters in syllabus (manifest) order, each as a loaded collection entry. */
export async function getOrderedChapters(): Promise<Chapter[]> {
  const all = await getCollection("chapters");
  const byId = new Map(all.map((e) => [e.data.id, e]));
  return readyChapters
    .map((m) => byId.get(m.id))
    .filter((c): c is Chapter => Boolean(c));
}

export interface ChapterStats {
  questions: number;
  topics: number;
  ai: number;
}

export function chapterStats(ch: Chapter): ChapterStats {
  const kps = ch.data.knowledge_points;
  return {
    questions: kps.reduce((n, kp) => n + kp.questions.length, 0),
    topics: kps.length,
    ai: kps.reduce((n, kp) => n + kp.questions.filter((q) => q.type === "ai").length, 0),
  };
}

// ---- search index (one entry per question) ------------------------------

export async function buildSearchIndex(): Promise<SearchEntry[]> {
  const chapters = await getOrderedChapters();
  const index: SearchEntry[] = [];
  for (const ch of chapters) {
    for (const kp of ch.data.knowledge_points) {
      for (const q of sortedQuestions(kp.questions)) {
        const tagtext = (q.tags ?? []).join(" ");
        index.push({
          c: ch.data.id,
          ct: ch.data.title,
          kp: kp.title,
          a: qid(kp.id, q.q),
          t: q.type,
          src: q.sources[0],
          srcs: q.sources,
          q: plain(q.q),
          tg: q.tags ?? [],
          txt: (
            plain(q.q + " " + (q.answer ?? "") + " " + kp.title) +
            " " +
            tagtext +
            " " +
            q.sources.join(" ")
          ).toLowerCase(),
        });
      }
    }
  }
  return index;
}
