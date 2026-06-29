export const AUTH_API_BASE = process.env.NEXT_PUBLIC_AUTH_API_URL ?? 'http://localhost:8001';

export function authApiUrl(path: string) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${AUTH_API_BASE}${normalizedPath}`;
}
