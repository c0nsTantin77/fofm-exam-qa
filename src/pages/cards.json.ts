import type { APIRoute } from "astro";
import { getOrderedChapters, sortedQuestions } from "../lib/content";
import { qid } from "../lib/qid";

// Flashcard payload, generated at build time and fetched only when the user
// starts a flashcard session (review page). Ships RAW markdown (not pre-rendered
// KaTeX HTML) to stay small; the client renders it on demand with lib/md.ts.
export const GET: APIRoute = async () => {
  const chapters = await getOrderedChapters();
  const cards = [];
  for (const ch of chapters) {
    for (const kp of ch.data.knowledge_points) {
      for (const q of sortedQuestions(kp.questions)) {
        cards.push({
          a: qid(kp.id, q.q),
          q: q.q,
          ans: q.answer,
          ext: q.extend ?? "",
          t: q.type,
          opts: q.options ?? null,
          calc: q.calc ?? null,
          src: q.sources[0],
          ct: ch.data.title,
          kp: kp.title,
          fig: q.figure ?? null,
        });
      }
    }
  }
  return new Response(JSON.stringify(cards), {
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
};
