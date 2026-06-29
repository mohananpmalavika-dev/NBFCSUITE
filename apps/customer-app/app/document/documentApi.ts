export const DOCUMENT_API_BASE = process.env.NEXT_PUBLIC_DOCUMENT_API_URL ?? 'http://localhost:8010';

export interface DocumentRecord {
  id: string;
  [key: string]: unknown;
}

export interface DocumentListResponse {
  items: DocumentRecord[];
  skip: number;
  limit: number;
  total: number;
}

export function documentApiUrl(path: string) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${DOCUMENT_API_BASE}${normalizedPath}`;
}

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(documentApiUrl(path));
  if (!response.ok) {
    throw new Error(`Document API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

async function postForm<T>(path: string, form: FormData): Promise<T> {
  const response = await fetch(documentApiUrl(path), {
    method: 'POST',
    body: form,
  });
  if (!response.ok) {
    throw new Error(`Document API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const documentApi = {
  listDocuments: (params = '') => getJson<DocumentListResponse>(`/documents${params}`),
  getDocument: (id: string) => getJson<DocumentRecord>(`/documents/${id}`),
  uploadDocument: (form: FormData) => postForm<DocumentRecord>('/documents/upload', form),
};
