import { eomApiUrl } from '../../../eomApi';


export async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(eomApiUrl(path));
  if (!res.ok) {
    throw new Error(`EOM API request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export async function putJson<T>(path: string, payload: unknown): Promise<T> {
  const res = await fetch(eomApiUrl(path), {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(`EOM API request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

