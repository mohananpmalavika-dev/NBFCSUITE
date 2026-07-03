'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';

export default function DocumentUploadPage() {
  const [categories, setCategories] = useState<any[]>([]);
  const [tags, setTags] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Form state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [formData, setFormData] = useState({
    category_id: '',
    document_type: 'loan',
    title: '',
    description: '',
    entity_type: '',
    entity_id: '',
    selectedTags: [] as string[],
    perform_ocr: false
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [catsData, tagsData] = await Promise.all([
        goldApi.listDocumentCategories({ is_active: true }),
        goldApi.listDocumentTags({ is_active: true })
      ]);
      
      setCategories(catsData);
      setTags(tagsData);
    } catch (err: any) {
      setError('Failed to load form data: ' + err.message);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      if (!formData.title) {
        setFormData(prev => ({ ...prev, title: file.name }));
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedFile) {
      setError('Please select a file to upload');
      return;
    }
    
    if (!formData.category_id) {
      setError('Please select a category');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      // In a real implementation, you would upload the file to storage first
      // and get the storage path/URL, then create the document record
      
      // For now, we'll create a mock document record
      const documentPayload = {
        category_id: formData.category_id,
        document_type: formData.document_type,
        title: formData.title,
        description: formData.description || null,
        entity_type: formData.entity_type || null,
        entity_id: formData.entity_id || null,
        file_name: selectedFile.name,
        file_size_bytes: selectedFile.size,
        mime_type: selectedFile.type,
        storage_path: `/uploads/${Date.now()}-${selectedFile.name}`, // Mock path
        storage_status: 'uploaded',
        uploaded_by: 'current-user-id', // TODO: Replace with actual user ID
        metadata: {
          original_filename: selectedFile.name,
          file_type: selectedFile.type,
          uploaded_from: 'web_ui'
        }
      };

      const document = await goldApi.createDocument(documentPayload);
      
      // Add tags if selected
      if (formData.selectedTags.length > 0) {
        for (const tagId of formData.selectedTags) {
          await goldApi.addTagToDocument(document.document_id, {
            document_id: document.document_id,
            tag_id: tagId,
            tagged_by: 'current-user-id'
          });
        }
      }
      
      // Perform OCR if requested
      if (formData.perform_ocr) {
        await goldApi.extractDocumentTextOCR({
          document_id: document.document_id,
          ocr_language: 'eng',
          extract_tables: false,
          extract_signatures: false
        });
      }

      setSuccess(`Document "${formData.title}" uploaded successfully!`);
      
      // Reset form
      setSelectedFile(null);
      setFormData({
        category_id: '',
        document_type: 'loan',
        title: '',
        description: '',
        entity_type: '',
        entity_id: '',
        selectedTags: [],
        perform_ocr: false
      });
      
      // Reset file input
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
      
    } catch (err: any) {
      setError('Failed to upload document: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Document</h1>
        <p className="text-gray-600">Upload and categorize new documents</p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {success && (
        <div className="mb-6 bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg">
          {success}
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 space-y-6">
        {/* File Upload */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select File *
          </label>
          <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg hover:border-blue-400 transition-colors">
            <div className="space-y-1 text-center">
              {selectedFile ? (
                <div className="flex items-center justify-center space-x-3">
                  <svg className="h-12 w-12 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div className="text-left">
                    <p className="text-sm font-medium text-gray-900">{selectedFile.name}</p>
                    <p className="text-xs text-gray-500">{formatFileSize(selectedFile.size)}</p>
                  </div>
                </div>
              ) : (
                <>
                  <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                    <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  <div className="text-sm text-gray-600">
                    <label className="relative cursor-pointer rounded-md font-medium text-blue-600 hover:text-blue-500">
                      <span>Upload a file</span>
                      <input
                        type="file"
                        className="sr-only"
                        onChange={handleFileSelect}
                        accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.xlsx,.xls"
                      />
                    </label>
                    <span className="pl-1">or drag and drop</span>
                  </div>
                  <p className="text-xs text-gray-500">PDF, DOC, DOCX, JPG, PNG, XLSX up to 10MB</p>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Document Details */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Category *
            </label>
            <select
              value={formData.category_id}
              onChange={(e) => setFormData(prev => ({ ...prev, category_id: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">Select Category</option>
              {categories.map(cat => (
                <option key={cat.category_id} value={cat.category_id}>
                  {cat.category_name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Document Type *
            </label>
            <select
              value={formData.document_type}
              onChange={(e) => setFormData(prev => ({ ...prev, document_type: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="loan">Loan</option>
              <option value="kyc">KYC</option>
              <option value="valuation">Valuation</option>
              <option value="pledge">Pledge</option>
              <option value="repayment">Repayment</option>
              <option value="collection">Collection</option>
              <option value="compliance">Compliance</option>
              <option value="audit">Audit</option>
              <option value="other">Other</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Document Title *
          </label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Enter document title"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Enter document description (optional)"
          />
        </div>

        {/* Entity Association */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Entity Type
            </label>
            <select
              value={formData.entity_type}
              onChange={(e) => setFormData(prev => ({ ...prev, entity_type: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">None</option>
              <option value="customer">Customer</option>
              <option value="loan">Loan</option>
              <option value="ornament">Ornament</option>
              <option value="collection_case">Collection Case</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Entity ID
            </label>
            <input
              type="text"
              value={formData.entity_id}
              onChange={(e) => setFormData(prev => ({ ...prev, entity_id: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="Enter entity ID (optional)"
            />
          </div>
        </div>

        {/* Tags */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tags
          </label>
          <div className="flex flex-wrap gap-2">
            {tags.map(tag => (
              <label
                key={tag.tag_id}
                className="flex items-center space-x-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={formData.selectedTags.includes(tag.tag_id)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setFormData(prev => ({
                        ...prev,
                        selectedTags: [...prev.selectedTags, tag.tag_id]
                      }));
                    } else {
                      setFormData(prev => ({
                        ...prev,
                        selectedTags: prev.selectedTags.filter(id => id !== tag.tag_id)
                      }));
                    }
                  }}
                  className="rounded border-gray-300"
                />
                <span className="text-sm text-gray-700">{tag.tag_name}</span>
              </label>
            ))}
          </div>
        </div>

        {/* OCR Option */}
        <div className="flex items-center">
          <input
            type="checkbox"
            id="perform_ocr"
            checked={formData.perform_ocr}
            onChange={(e) => setFormData(prev => ({ ...prev, perform_ocr: e.target.checked }))}
            className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          />
          <label htmlFor="perform_ocr" className="ml-2 block text-sm text-gray-700">
            Perform OCR text extraction after upload
          </label>
        </div>

        {/* Submit Buttons */}
        <div className="flex gap-4 pt-4">
          <button
            type="submit"
            disabled={loading || !selectedFile}
            className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            {loading ? 'Uploading...' : 'Upload Document'}
          </button>
          <button
            type="button"
            onClick={() => {
              setSelectedFile(null);
              setFormData({
                category_id: '',
                document_type: 'loan',
                title: '',
                description: '',
                entity_type: '',
                entity_id: '',
                selectedTags: [],
                perform_ocr: false
              });
              const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
              if (fileInput) fileInput.value = '';
            }}
            className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 font-medium"
          >
            Clear
          </button>
        </div>
      </form>
    </div>
  );
}
