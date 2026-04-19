/**
<<<<<<< HEAD
 * Backend base URL. Empty string = same origin (use Vite dev proxy to port 8000).
 * Override with VITE_API_BASE_URL=http://127.0.0.1:8000 if you call the API directly.
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
=======
 * API client configuration and base setup
 */

const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface ApiError {
  detail?: string;
  message?: string;
}

export interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
  status: number;
}

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
    this.loadToken();
  }

  private loadToken() {
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('access_token');
    }
  }

  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token);
    }
  }

  getToken(): string | null {
    return this.token;
  }

  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...this.getHeaders(),
          ...options.headers,
        },
      });

      if (!response.ok) {
        const error = await response.json();
        return {
          data: undefined,
          error: error as ApiError,
          status: response.status,
        };
      }

      const data = await response.json();
      return {
        data: data as T,
        error: undefined,
        status: response.status,
      };
    } catch (error) {
      return {
        data: undefined,
        error: {
          message: error instanceof Error ? error.message : 'Network error',
        },
        status: 0,
      };
    }
  }

  get<T>(endpoint: string) {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  post<T>(endpoint: string, body?: any) {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  put<T>(endpoint: string, body?: any) {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(body),
    });
  }

  delete<T>(endpoint: string) {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

export const apiClient = new ApiClient();
>>>>>>> 073348942a85b4d4d8cd0c9e2a6dfb52cd16ad57
