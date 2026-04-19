/** Persists chat session id so the dashboard can align readiness with the same server-side session. */

export const CHAT_SESSION_STORAGE_KEY = "greennovation_chat_session_id";

export function getStoredChatSessionId(): string | null {
  if (typeof localStorage === "undefined") return null;
  return localStorage.getItem(CHAT_SESSION_STORAGE_KEY);
}

export function setStoredChatSessionId(id: string | null): void {
  if (typeof localStorage === "undefined") return;
  if (id) localStorage.setItem(CHAT_SESSION_STORAGE_KEY, id);
  else localStorage.removeItem(CHAT_SESSION_STORAGE_KEY);
}
