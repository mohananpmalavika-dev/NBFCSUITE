export const AI_API_BASE = process.env.NEXT_PUBLIC_AI_API_URL ?? 'http://localhost:8030';
export const DEFAULT_AI_TENANT = process.env.NEXT_PUBLIC_AI_TENANT_ID ?? 'tenant-local-accounting';

export function aiApiUrl(path: string) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${AI_API_BASE}${normalizedPath}`;
}

async function postJson<T>(path: string, payload: unknown): Promise<T> {
  const response = await fetch(aiApiUrl(path), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error(`AI API request failed: ${response.status}`);
  return response.json() as Promise<T>;
}

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(aiApiUrl(path));
  if (!response.ok) throw new Error(`AI API request failed: ${response.status}`);
  return response.json() as Promise<T>;
}

export const aiApi = {
  chat: (tenantId = DEFAULT_AI_TENANT, prompt = '') => postJson(`/api/v1/ai/chat`, { tenant_id: tenantId, prompt }),
  models: () => getJson(`/api/v1/ai/models`),
  prompts: () => getJson(`/api/v1/ai/prompts`),
  dashboard: (tenantId = DEFAULT_AI_TENANT) => getJson(`/api/v1/ai/dashboard?tenant_id=${encodeURIComponent(tenantId)}`),
};
