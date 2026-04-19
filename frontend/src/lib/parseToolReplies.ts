/**
 * Parse AI replies for Summary / Quiz / Explain tool flows.
 */

export type QuizItem = {
  question: string;
  answer: string;
  difficulty?: string;
};

/** Prefer structured list from API (exercise JSON). */
export function extractQuizItems(reply: string, replyRaw: unknown): QuizItem[] | null {
  if (Array.isArray(replyRaw)) {
    const out: QuizItem[] = [];
    for (const x of replyRaw) {
      if (x && typeof x === "object") {
        const o = x as Record<string, unknown>;
        const q = o.question != null ? String(o.question).trim() : "";
        const a = o.answer != null ? String(o.answer).trim() : "";
        if (q || a) {
          out.push({
            question: q,
            answer: a,
            difficulty: o.difficulty != null ? String(o.difficulty) : undefined,
          });
        }
      }
    }
    if (out.length) return out;
  }
  return parseQuizMarkdown(reply);
}

/** Matches **Q1** question line then *Answer:* (markdown fallback). */
export function parseQuizMarkdown(text: string): QuizItem[] | null {
  const t = text.replace(/\r\n/g, "\n");
  const blocks = t.split(/\*\*Q\s*\d+\*\*/i);
  if (blocks.length < 2) return null;
  const items: QuizItem[] = [];
  for (let i = 1; i < blocks.length; i++) {
    const chunk = blocks[i].trim();
    const m = chunk.match(/^([^\n]+)\s*\n\s*\*Answer:?\*?\s*([\s\S]+)$/i);
    if (m) {
      items.push({ question: m[1].trim(), answer: m[2].trim() });
    } else {
      const idx = chunk.search(/\*Answer:?\*?\s*/i);
      if (idx > 0) {
        items.push({
          question: chunk.slice(0, idx).replace(/\n/g, " ").trim(),
          answer: chunk.slice(idx).replace(/^\*Answer:?\*?\s*/i, "").trim(),
        });
      }
    }
  }
  return items.length ? items : null;
}

/** Text before first quiz question (if any). */
export function quizIntroText(reply: string): string {
  const t = reply.replace(/\r\n/g, "\n");
  const idx = t.search(/\*\*Q\s*1\s*\*\*/i);
  if (idx <= 0) return "";
  return t.slice(0, idx).trim();
}

export type SummarySections = { lead: string; rest: string };

/**
 * Split summary + follow-up (questions / revision) when the model uses clear separators.
 */
export function parseSummarySections(text: string): SummarySections | null {
  const t = text.replace(/\r\n/g, "\n").trim();
  if (t.length < 80) return null;

  const splitters: RegExp[] = [
    /\n\n(?:#{1,3}\s*)?(?:Revision questions|Practice questions|Questions)\b/i,
    /\n\n(?:#{1,3}\s*)?\d+[\.)]\s*(?:Revision|Practice|Check)[^\n]*/i,
    /\n\n\*{0,2}(?:Q\d+|Question\s*\d+)/i,
  ];

  for (const re of splitters) {
    const m = t.match(re);
    if (m?.index != null && m.index > 60) {
      return { lead: t.slice(0, m.index).trim(), rest: t.slice(m.index).trim() };
    }
  }

  const h2 = t.search(/\n##\s+/);
  if (h2 > 80) {
    return { lead: t.slice(0, h2).trim(), rest: t.slice(h2).trim() };
  }

  return null;
}
