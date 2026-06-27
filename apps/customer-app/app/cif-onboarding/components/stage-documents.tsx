'use client';

import { useCIFStore } from '@/lib/cif-store';
import { cifApi } from '@/lib/cif-api';
import { useState } from 'react';

interface StageDocumentsProps {
  onNext: () => void;
}

export default function StageDocuments({ onNext }: StageDocumentsProps) {
  const { customerId, documents, addDocument, removeDocument, setLoading, setError, markStageComplete } =
    useCIFStore();
  const [newDoc, setNewDoc] = useState({
    type: 'income_proof',
    title: '',
    file: null as File | null,
  });

  const handleAddDocument = async () => {
    if (!customerId || !newDoc.type || !newDoc.title || !newDoc.file) {
      setError('Please select a document, title, and file.');
      return;
    }

    const file = newDoc.file;
    setLoading(true);
    try {
      await cifApi.addDocument(customerId, {
        document_type: newDoc.type,
        document_title: newDoc.title,
        document_file: file,
      });

      addDocument({ type: newDoc.type, title: newDoc.title, file });
      setNewDoc({ type: 'income_proof', title: '', file: null });
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Unable to upload supporting document');
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    markStageComplete(15);
    onNext();
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Stage 15: Document Vault</h2>
        <p className="text-slate-600">
          Upload supporting documents. They will be versioned and maintained for compliance.
        </p>
      </div>

      <div className="border border-slate-300 rounded-lg p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Document Type</label>
          <select
            value={newDoc.type}
            onChange={(e) => setNewDoc({ ...newDoc, type: e.target.value })}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
          >
            <option value="income_proof">Income Proof (Salary Slip/ITR)</option>
            <option value="address_proof">Address Proof (Utility Bill)</option>
            <option value="bank_statement">Bank Statement</option>
            <option value="business_proof">Business Document</option>
            <option value="other">Other</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Document Title</label>
          <input
            type="text"
            value={newDoc.title}
            onChange={(e) => setNewDoc({ ...newDoc, title: e.target.value })}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
            placeholder="e.g., Salary Slip - June 2024"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Upload File</label>
          <input
            type="file"
            accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
            onChange={(e) => setNewDoc({ ...newDoc, file: e.target.files?.[0] || null })}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
          />
        </div>

        <button
          onClick={handleAddDocument}
          disabled={!newDoc.type || !newDoc.title || !newDoc.file}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-semibold"
        >
          ➕ Upload Document
        </button>
      </div>

      {/* Uploaded Documents */}
      {documents.length > 0 && (
        <div>
          <h3 className="font-bold text-slate-900 mb-3">📦 Document Vault</h3>
          <div className="space-y-2">
            {documents.map((doc, index) => (
              <div key={index} className="flex items-center justify-between bg-slate-50 p-4 rounded-lg">
                <div>
                  <p className="font-semibold text-slate-900">{doc.title}</p>
                  <p className="text-xs text-slate-600">{doc.type}</p>
                </div>
                <button
                  onClick={() => removeDocument(index)}
                  className="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 text-sm"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {documents.length > 0 && (
        <button
          onClick={handleNext}
          className="w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-semibold"
        >
          ✅ Continue to Approval
        </button>
      )}

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-semibold text-blue-900 mb-2">📋 Document Management</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• All documents are versioned for audit trail</li>
          <li>• Expiry dates tracked automatically</li>
          <li>• Secure encryption at rest</li>
          <li>• Accessible across all products</li>
        </ul>
      </div>
    </div>
  );
}
