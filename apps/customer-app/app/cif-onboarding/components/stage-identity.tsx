'use client';

import { useState } from 'react';
import { useCIFStore } from '@/lib/cif-store';
import { cifApi } from '@/lib/cif-api';

interface StageIdentityProps {
  onNext: () => void;
}

export default function StageIdentity({ onNext }: StageIdentityProps) {
  const {
    customerId,
    identityDocuments,
    addIdentityDocument,
    removeIdentityDocument,
    setLoading,
    setError,
    markStageComplete,
  } = useCIFStore();
  const [newDoc, setNewDoc] = useState({
    type: 'pan',
    number: '',
    file: null as File | null,
  });

  const handleAddDocument = async () => {
    if (!customerId || !newDoc.type || !newDoc.number || !newDoc.file) {
      setError('Please select a document type, number, and file.');
      return;
    }

    setLoading(true);
    try {
      const response = await cifApi.addIdentityDocument(customerId, {
        document_type: newDoc.type,
        document_number: newDoc.number,
        document_file: newDoc.file,
      });

      addIdentityDocument({
        type: newDoc.type,
        number: newDoc.number,
        file: newDoc.file,
        extractedData: response,
      });
      setNewDoc({ type: 'pan', number: '', file: null });
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Unable to upload document');
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (identityDocuments.length > 0) {
      markStageComplete(4);
      onNext();
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Stage 4: Identity Verification</h2>
        <p className="text-slate-600">
          Upload identity documents. Our AI will auto-extract key information.
        </p>
      </div>

      <div className="border border-slate-300 rounded-lg p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Document Type</label>
          <select
            value={newDoc.type}
            onChange={(e) => setNewDoc({ ...newDoc, type: e.target.value })}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="pan">PAN Card</option>
            <option value="aadhar">Aadhaar Card</option>
            <option value="passport">Passport</option>
            <option value="driving_licence">Driving Licence</option>
            <option value="voter_id">Voter ID</option>
            <option value="photo">Photo</option>
            <option value="signature">Signature</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Document Number
          </label>
          <input
            type="text"
            value={newDoc.number}
            onChange={(e) => setNewDoc({ ...newDoc, number: e.target.value })}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
            placeholder="Enter document number"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Upload Document
          </label>
          <input
            type="file"
            accept="image/*,application/pdf"
            onChange={(e) => setNewDoc({ ...newDoc, file: e.target.files?.[0] || null })}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
          />
        </div>

        <button
          onClick={handleAddDocument}
          disabled={!newDoc.type || !newDoc.number || !newDoc.file}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-semibold"
        >
          ➕ Add Document
        </button>
      </div>

      {/* Uploaded Documents */}
      <div>
        <h3 className="font-bold text-slate-900 mb-3">Uploaded Documents</h3>
        <div className="space-y-2">
          {identityDocuments.map((doc, index) => (
            <div key={index} className="flex items-center justify-between bg-slate-50 p-4 rounded-lg">
              <div>
                <p className="font-semibold text-slate-900">{doc.type.toUpperCase()}</p>
                <p className="text-sm text-slate-600">{doc.number}</p>
              </div>
              <button
                onClick={() => removeIdentityDocument(index)}
                className="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 text-sm"
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      </div>

      {identityDocuments.length > 0 && (
        <button
          onClick={handleNext}
          className="w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-semibold"
        >
          ✅ Continue to Next Stage
        </button>
      )}

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-semibold text-blue-900 mb-2">🤖 AI OCR Features</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Automatic field extraction from documents</li>
          <li>• Confidence scoring for each extracted field</li>
          <li>• Document validation and fraud detection</li>
          <li>• Support for multiple languages</li>
        </ul>
      </div>
    </div>
  );
}
