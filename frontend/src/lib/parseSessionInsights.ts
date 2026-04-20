/**
 * Tutor replies sometimes append structured lines the model was asked to include.
 * We surface those in "Live insights" and remove them from the chat bubble.
 */

import type { SessionInsightsPayload } from "./api";

export type SessionInsights = {
  sessionMinutes?: string;
  breakNeeded?: string;
  difficultyAdjustment?: string;
};

export function hasSessionInsights(s: SessionInsights | null | undefined): boolean {
  return !!(s?.sessionMinutes?.trim() || s?.breakNeeded?.trim() || s?.difficultyAdjustment?.trim());
}

/** Prefer API payload; fill gaps from parsed reply lines. */
export function mergeSessionInsights(
  fromParser: SessionInsights | null,
  fromApi: Partial<SessionInsights> | SessionInsightsPayload | null | undefined,
): SessionInsights | null {
  const p = fromParser ?? {};
  const a = fromApi ?? {};
  const out: SessionInsights = {
    sessionMinutes: (a.sessionMinutes ?? p.sessionMinutes)?.trim() || undefined,
    breakNeeded: (a.breakNeeded ?? p.breakNeeded)?.trim() || undefined,
    difficultyAdjustment: (a.difficultyAdjustment ?? p.difficultyAdjustment)?.trim() || undefined,
  };
  if (!hasSessionInsights(out)) return null;
  return out;
}

function cleanValue(s: string): string {
  return s.replace(/\*{1,2}/g, "").replace(/^[`"'[\]()]+|[`"'[\]()]+$/g, "").trim();
}

function makeFieldExtractor(labelAlternation: string) {
  return (text: string): { value: string; match: string } | null => {
    const sameLine = new RegExp(
      `(?:^|\\n)(\\s*(?:[-*•]+\\s+)?(?:\\*{0,2}\\s*)?(?:${labelAlternation})(?:\\s*\\*{0,2})?\\s*:\\s*[^\\n]+)`,
      "im",
    );
    const m = text.match(sameLine);
    if (m) {
      const inner = m[1];
      const valueMatch = inner.match(/:\s*([^\n]+)/);
      const value = valueMatch ? cleanValue(valueMatch[1]) : "";
      if (value) return { value, match: m[0] };
    }
    const twoLine = new RegExp(
      `(?:^|\\n)(\\s*(?:[-*•]+\\s+)?(?:\\*{0,2}\\s*)?(?:${labelAlternation})(?:\\s*\\*{0,2})?\\s*:\\s*\\n+\\s*[^\\n]+)`,
      "im",
    );
    const m2 = text.match(twoLine);
    if (m2) {
      const inner = m2[1];
      const valueMatch = inner.match(/:\\s*\\n+\\s*([^\n]+)/);
      const value = valueMatch ? cleanValue(valueMatch[1]) : "";
      if (value) return { value, match: m2[0] };
    }
    return null;
  };
}

const extractSessionMinutes = makeFieldExtractor("Session\\s+Minutes|session_minutes");
const extractBreakNeeded = makeFieldExtractor("Break\\s+Needed|break_needed");
const extractDifficulty = makeFieldExtractor("Difficulty\\s+Adjustment|difficulty_adjustment");

/**
 * Pulls Session Minutes / Break Needed / Difficulty Adjustment out of raw reply text.
 * Handles list markers (- *), bold (**), and label on one line with value on the next.
 */
export function stripSessionInsightLines(raw: string): {
  cleaned: string;
  insights: SessionInsights | null;
} {
  const text = raw.replace(/\r\n/g, "\n");
  const insights: SessionInsights = {};
  const removals: { start: number; end: number }[] = [];

  const hits: [keyof SessionInsights, ReturnType<typeof extractSessionMinutes>][] = [
    ["sessionMinutes", extractSessionMinutes(text)],
    ["breakNeeded", extractBreakNeeded(text)],
    ["difficultyAdjustment", extractDifficulty(text)],
  ];

  for (const [key, hit] of hits) {
    if (hit) {
      insights[key] = hit.value;
      const start = text.indexOf(hit.match);
      if (start >= 0) removals.push({ start, end: start + hit.match.length });
    }
  }

  if (!hasSessionInsights(insights)) {
    return { cleaned: raw, insights: null };
  }

  removals.sort((a, b) => b.start - a.start);
  let cleaned = text;
  for (const { start, end } of removals) {
    cleaned = cleaned.slice(0, start) + cleaned.slice(end);
  }

  cleaned = cleaned
    .replace(/\n{3,}/g, "\n\n")
    .replace(/^\n+/, "")
    .replace(/\n+$/, "")
    .trim();

  return { cleaned, insights };
}
