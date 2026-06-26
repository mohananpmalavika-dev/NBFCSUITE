'use client';

import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

interface Document {
  id: string;
  name: string;
  type: string;
  uploadDate: string;
  status: string;
  url: string;
}

export default function DocumentsPage() {
  const { user, token, isLoading } = useAuth();
  const router = useRouter();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    if (!isLoading && !token) {
      router.push('/login');
    }
  }, [token, isLoading, router]);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = () => {
    const mockDocs: Document[] = [
      {
        id: '1',
        name: 'PAN Card',
        type: 'PAN',
        uploadDate: '2026-06-15',
        status: 'verified',
        url: '/documents/pan.jpg',
      },
      {
        id: '2',
        name: 'Aadhar Card',
        type: 'AADHAR',
        uploadDate: '2026-06-14',
        status: 'verified',
        url: '/documents/aadhar.jpg',
      },
      {
        id: '3',
        name: 'Bank Statement',
        type: 'BANK_STATEMENT',
        uploadDate: '2026-06-10',
        status: 'pending',
        url: '/documents/bank.pdf',
      },
    ];
    setDocuments(mockDocs);
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    setUploading(true);
    try {
      // Simulate upload
      const newDoc: Document = {
        id: Date.now().toString(),
        name: files[0].name,
        type: 'OTHER',
        uploadDate: new Date().toISOString().split('T')[0],
        status: 'pending',
        url: URL.createObjectURL(files[0]),
      };
      setDocuments([...documents, newDoc]);
      alert('Document uploaded successfully');
    } catch (err) {
      alert('Upload failed');
    } finally {
      setUploading(false);
    }
  };

  if (isLoading) {
    return <div className="p-8 text-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900">Documents</h1>
          <p className="text-gray-600 mt-2">Manage and upload your documents</p>
        </div>

        {/* Upload Card */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Upload Document</h2>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8">
            <div className="text-center">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                stroke="currentColor"
                fill="none"
                viewBox="0 0 48 48"
              >
                <path
                  d="M28 8H12a4 4 0 00-4 4v20a4 4 0 004 4h24a4 4 0 004-4V20m-6-8v8m0 0l-3-3m3 3l3-3"
                  strokeWidth={2}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <p className="mt-2 text-sm text-gray-600">
                Drag and drop your document or{' '}
                <label className="text-blue-600 hover:text-blue-700 cursor-pointer">
                  browse
                  <input
                    type="file"
                    onChange={handleUpload}
                    disabled={uploading}
                    className="hidden"
                    accept=".pdf,.jpg,.jpeg,.png"
                  />
                </label>
              </p>
            </div>
          </div>
        </div>

        {/* Documents Grid */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Your Documents</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {documents.map((doc) => (
              <div key={doc.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-lg transition">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <p className="font-semibold text-gray-900">{doc.name}</p>
                    <p className="text-xs text-gray-600">{doc.type}</p>
                  </div>
                  <span
                    className={`px-2 py-1 rounded text-xs font-semibold ${
                      doc.status === 'verified'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}
                  >
                    {doc.status}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mb-4">Uploaded: {doc.uploadDate}</p>
                <div className="flex space-x-2">
                  <a
                    href={doc.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 text-center text-blue-600 hover:text-blue-700 text-sm font-medium"
                  >
                    View
                  </a>
                  <button className="flex-1 text-center text-red-600 hover:text-red-700 text-sm font-medium">
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
