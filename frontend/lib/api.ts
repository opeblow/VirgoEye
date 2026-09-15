// In dev, `/api` is rewritten by next.config.js to the local backend.
// In Docker, set NEXT_PUBLIC_API_BASE to hit the backend container directly
// (relative proxy across containers is not possible).
export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE?.replace(/\/$/, "") ?? "/api";

export async function healthCheck(): Promise<Record<string, unknown>> {
  const res = await fetch(`${API_BASE}/v1/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return res.json();
}
