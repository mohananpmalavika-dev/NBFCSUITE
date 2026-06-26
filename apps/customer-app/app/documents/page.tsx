'use client';

import { apiClient } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { ChangeEvent, useCallback, useEffect, useState } from 'react';

interface DocumentRecord {
  id: string;
  document_type: string;
  document_name: string;
  document_url: string;
  status: string;
  expiry_date?: string | null;
  created_at: string;
}

export default function DocumentsPage() {
  const { user, token, isLoading } = useAuth();
  const router = useRouter();
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [expiringDocuments, setExpiringDocuments] = useState<DocumentRecord[]>([]);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!isLoading && !token) {
      router.push('/login');
    }
  }, [token, isLoading, router]);

  const loadDocuments = useCallback(async () => {
    if (!user || !token) {
      return;
    }
    setMessage('');
    try {
      const [documentsRes, expiringRes] = await Promise.all([
        apiClient.getCustomerDocuments(user.id),
        apiClient.getExpiringDocuments(user.id, 45),
      ]);
      setDocuments(documentsRes.data.items || []);
      setExpiringDocuments(expiringRes.data.items || []);
    } catch {
      setMessage('Could not load documents from the document service.');
    }
  }, [user, token]);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  const handleUpload = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !user) {
      return;
    }

    setUploading(true);
    setMessage('');
    try {
      await apiClient.createDocument({
        subject_type: 'customer',
        subject_id: user.id,
        document_type: file.name.split('.').pop()?.toUpperCase() || 'OTHER',
        document_name: file.name,
        document_url: `local-upload://${encodeURIComponent(file.name)}`,
        metadata: {
          original_filename: file.name,
          size_bytes: file.size,
          source_service: 'customer-app',
          source_reference_id: user.id,
        },
      });
      setMessage('Document registered successfully.');
      event.target.value = '';
      await loadDocuments();
    } catch {
      setMessage('Upload failed. The document service rejected the request.');
    } finally {
      setUploading(false);
    }
  };

  const handleExpire = async (documentId: string) => {
    setMessage('');
    try {
      await apiClient.expireDocument(documentId);
      setMessage('Document marked expired.');
      await loadDocuments();
    } catch {
      setMessage('Could not expire this document.');
    }
  };

  if (isLoading) {
    return <div className="p-8 text-center">Loading...</div>;
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8">
      <div className="mx-auto max-w-6xl">
        <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-950">Documents</h1>
            <p className="mt-1 text-slate-600">Manage KYC and servicing documents.</p>
          </div>
          <button
            onClick={() => router.push('/')}
            className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-white"
          >
            Dashboard
          </button>
        </div>

        {message && (
          <div className="mb-4 rounded-md border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900">
            {message}
          </div>
        )}

        <section className="mb-6 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-xl font-semibold text-slate-950">Upload Document</h2>
          <label className="flex min-h-36 cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-slate-300 bg-slate-50 px-4 py-8 text-center hover:bg-slate-100">
            <span className="text-sm font-medium text-blue-700">{uploading ? 'Uploading...' : 'Choose PDF or image'}</span>
            <span className="mt-1 text-xs text-slate-500">The service stores metadata and a URL reference.</span>
            <input
              type="file"
              onChange={handleUpload}
              disabled={uploading}
              className="hidden"
              accept=".pdf,.jpg,.jpeg,.png"
            />
          </label>
        </section>

        {expiringDocuments.length > 0 && (
          <section className="mb-6 rounded-lg border border-amber-200 bg-amber-50 p-5">
            <h2 className="mb-2 text-lg font-semibold text-amber-950">Expiring Soon</h2>
            <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
              {expiringDocuments.map((document) => (
                <DocumentRow key={document.id} document={document} onExpire={handleExpire} compact />
              ))}
            </div>
          </section>
        )}

        <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-xl font-semibold text-slate-950">Your Documents</h2>
          {documents.length === 0 ? (
            <p className="rounded-md bg-slate-50 p-4 text-sm text-slate-600">No documents found.</p>
          ) : (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
              {documents.map((document) => (
                <DocumentRow key={document.id} document={document} onExpire={handleExpire} />
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}

function DocumentRow({
  document,
  onExpire,
  compact = false,
}: {
  document: DocumentRecord;
  onExpire: (documentId: string) => void;
  compact?: boolean;
}) {
  const statusClass =
    document.status === 'verified'
      ? 'bg-emerald-100 text-emerald-800'
      : document.status === 'expired'
        ? 'bg-slate-200 text-slate-700'
        : document.status === 'rejected'
          ? 'bg-red-100 text-red-800'
          : 'bg-amber-100 text-amber-800';

  return (
    <article className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="mb-3 flex items-start justify-between gap-3">
        <div>
          <p className="font-semibold text-slate-950">{document.document_name}</p>
          <p className="text-xs uppercase text-slate-500">{document.document_type}</p>
        </div>
        <span className={`rounded px-2 py-1 text-xs font-semibold ${statusClass}`}>{document.status}</span>
      </div>
      <p className="text-xs text-slate-500">
        Added: {new Date(document.created_at).toLocaleDateString()}
      </p>
      <p className="mt-1 text-xs text-slate-500">
        Expires: {document.expiry_date ? new Date(document.expiry_date).toLocaleDateString() : 'Not set'}
      </p>
      {!compact && (
        <div className="mt-4 flex gap-2">
          <a
            href={document.document_url}
            className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-center text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            View
          </a>
          <button
            onClick={() => onExpire(document.id)}
            disabled={document.status === 'expired' || document.status === 'rejected'}
            className="flex-1 rounded-md border border-red-200 px-3 py-2 text-sm font-medium text-red-700 hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Expire
          </button>
        </div>
      )}
    </article>
  );
}
