const EOM_API_BASE = process.env.NEXT_PUBLIC_EOM_API_URL ?? 'http://localhost:8002';

export function eomApiUrl(path: string) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${EOM_API_BASE}${normalizedPath}`;
}
