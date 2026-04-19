import type { Project } from "@/data/projects";

/**
 * Backend base URL. Empty string = same origin (use Vite dev proxy to your API).
 * Optional: VITE_API_BASE_URL if you call the API directly.
 */
const base = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ?? "";

export type ChatResponse = {
  session_id: string;
  reply: string;
  reply_raw?: string | unknown[] | null;
  routing?: Record<string, unknown> | null;
  errors: string[];
  warnings: string[];
};

export async function postChat(body: {
  message: string;
  session_id?: string | null;
  intent?: string | null;
  course_context?: Record<string, unknown> | null;
}): Promise<ChatResponse> {
  const r = await fetch(`${base}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: body.message,
      session_id: body.session_id ?? null,
      intent: body.intent ?? null,
      course_context: body.course_context ?? null,
    }),
  });
  if (!r.ok) {
    const t = await r.text();
    throw new Error(t || `${r.status} ${r.statusText}`);
  }
  return r.json() as Promise<ChatResponse>;
}

export async function deleteSession(sessionId: string): Promise<void> {
  await fetch(`${base}/api/session/${encodeURIComponent(sessionId)}`, { method: "DELETE" });
}

export type CorpusFile = {
  name: string;
  size_bytes: number;
  kind: "document" | "rag_index";
};

export async function fetchCorpusFiles(): Promise<{
  data_dir: string;
  files: CorpusFile[];
  error?: string;
}> {
  const r = await fetch(`${base}/api/corpus/files`);
  if (!r.ok) {
    const t = await r.text();
    throw new Error(t || `${r.status} ${r.statusText}`);
  }
  return r.json() as Promise<{ data_dir: string; files: CorpusFile[]; error?: string }>;
}

/** URL to stream a corpus file (same-origin in dev via Vite proxy). */
export function corpusFileUrl(filename: string): string {
  return `${base}/api/corpus/file/${encodeURIComponent(filename)}`;
}

export async function fetchProjects(): Promise<Project[]> {
  const r = await fetch(`${base}/api/projects`);
  if (!r.ok) {
    const t = await r.text();
    throw new Error(t || `${r.status} ${r.statusText}`);
  }
  const data = (await r.json()) as { projects: Project[] };
  return data.projects ?? [];
}

export async function saveProjects(projects: Project[]): Promise<void> {
  const r = await fetch(`${base}/api/projects`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ projects }),
  });
  if (!r.ok) {
    const t = await r.text();
    throw new Error(t || `${r.status} ${r.statusText}`);
  }
}

export type ReadinessApiResponse = {
  readiness_percent: number;
  readiness_signal: Record<string, unknown>;
  recommended_intensity: string;
  session_id: string | null;
};

/** Same readiness pipeline as chat (`run_readiness_agent`). Uses projects for passive signals; optional session merges stored signals from workspace chat. */
export async function fetchReadiness(sessionId: string | null): Promise<ReadinessApiResponse> {
  const q =
    sessionId && sessionId.length > 0
      ? `?session_id=${encodeURIComponent(sessionId)}`
      : "";
  const r = await fetch(`${base}/api/readiness${q}`);
  if (!r.ok) {
    const t = await r.text();
    throw new Error(t || `${r.status} ${r.statusText}`);
  }
  return r.json() as Promise<ReadinessApiResponse>;
}

export async function getHealth(): Promise<{
  status: string;
  data_dir: string;
  data_dir_exists: boolean;
  groq_configured: boolean;
}> {
  const r = await fetch(`${base}/health`);
  if (!r.ok) throw new Error(r.statusText);
  return r.json() as Promise<{
    status: string;
    data_dir: string;
    data_dir_exists: boolean;
    groq_configured: boolean;
  }>;
}
