'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';

export default function DocumentRepositoryPage() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [tags, setTags] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Filters
  const [categoryFilter, setCategoryFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  
  // Pagination
  const [page, setPage] = useState(0);
  const [limit] = useState(20);
  
  // Selection
  const [selectedDocs, setSelectedDocs] = useState<string[]>([]);

  useEffect(() => {
    loadData();
  }, [page, categoryFilter, typeFilter, statusFilter, searchQuery]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [docsData, catsData, tagsData] = await Promise.all([
        goldApi.listDocuments({
          category_id: categoryFilter || undefined,
          document_type: typeFilter || undefined,
          storage_status: statusFilter || undefined,
          search: searchQuery || undefined,
          skip: page * limit,
          limit
        }),
        goldApi.listDocumentCategories({ is_active: true }),
        goldApi.listDocumentTags({ is_active: true })
      ]);
      
      setDocuments(docsData);
      setCategories(catsData);
      setTags(tagsData);
      setError('');
    } catch (err: any) {
      setError(err.message || 'Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectDoc = (docId: string) => {
    setSelectedDocs(prev => 
      prev.includes(docId) 
        ? prev.filter(id => id !== docId)
        : [...prev, docId]
    );
  };

  const handleSelectAll = () => {
    if (selectedDocs.length === documents.length) {
      setSelectedDocs([]);
    } else {
      setSelectedDocs(documents.map(d => d.document_id));
    }
  };

  const handleBulkTag = async () => {
    if (selectedDocs.length === 0 || selectedTags.length === 0) return;
    
    try {
      await goldApi.bulkTagDocuments({
        document_ids: selectedDocs,
        tag_ids: selectedTags,
        tagged_by: 'current-user-id' // TODO: Replace with actual user ID
      });
      alert('Tags applied successfully');
      setSelectedDocs([]);
      loadData();
    } catch (err: any) {
      alert('Failed to apply tags: ' + err.message);
    }
  };

  const handleBulkDelete = async () => {
    if (selectedDocs.length === 0) return;
    if (!confirm(`Delete ${selectedDocs.length} document(s)?`)) return;
    
    try {
      await goldApi.bulkDeleteDocuments({
        document_ids: selectedDocs,
        deleted_by: 'current-user-id', // TODO: Replace with actual user ID
        deletion_reason: 'Bulk deletion from repository'
      });
      alert('Documents deleted successfully');
      setSelectedDocs([]);
      loadData();
    } catch (err: any) {
      alert('Failed to delete documents: ' + err.message);
    }
  };

  const handleDownload = (doc: any) => {
    // TODO: Implement actual download
    alert(`Downloading document: ${doc.title}`);
  };

  const handleShare = (doc: any) => {
    // TODO: Implement sharing
    alert(`Share document: ${doc.title}`);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading && documents.length === 0) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
            <p className="text-gray-600">Loading documents...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Document Repository</h1>
        <p className="text-gray-600">Search, filter, and manage all documents</p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Filters */}
      <div className="mb-6 bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by title or description..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Categories</option>
              {categories.map(cat => (
                <option key={cat.category_id} value={cat.category_id}>
                  {cat.category_name}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Types</option>
              <option value="loan">Loan</option>
              <option value="kyc">KYC</option>
              <option value="valuation">Valuation</option>
              <option value="pledge">Pledge</option>
              <option value="repayment">Repayment</option>
              <option value="collection">Collection</option>
              <option value="compliance">Compliance</option>
              <option value="audit">Audit</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Status</option>
              <option value="uploaded">Uploaded</option>
              <option value="processing">Processing</option>
              <option value="verified">Verified</option>
              <option value="archived">Archived</option>
            </select>
          </div>
        </div>
      </div>

      {/* Bulk Actions */}
      {selectedDocs.length > 0 && (
        <div className="mb-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-blue-900">
              {selectedDocs.length} document(s) selected
            </span>
            <div className="flex gap-2">
              <button
                onClick={handleBulkTag}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
              >
                Apply Tags
              </button>
              <button
                onClick={handleBulkDelete}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm"
              >
                Delete
              </button>
              <button
                onClick={() => setSelectedDocs([])}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 text-sm"
              >
                Clear Selection
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Documents Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3">
                  <input
                    type="checkbox"
                    checked={selectedDocs.length === documents.length && documents.length > 0}
                    onChange={handleSelectAll}
                    className="rounded border-gray-300"
                  />
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Document
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Size
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Uploaded
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {documents.map((doc) => (
                <tr key={doc.document_id} className="hover:bg-gray-50">
                  <td className="px-4 py-4">
                    <input
                      type="checkbox"
                      checked={selectedDocs.includes(doc.document_id)}
                      onChange={() => handleSelectDoc(doc.document_id)}
                      className="rounded border-gray-300"
                    />
                  </td>
                  <td className="px-6 py-4">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{doc.title}</div>
                      <div className="text-sm text-gray-500">{doc.document_number}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {categories.find(c => c.category_id === doc.category_id)?.category_name || 'N/A'}
                  </td>
                  <td className="px-6 py-4">
                    <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                      {doc.document_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {formatFileSize(doc.file_size_bytes || 0)}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {formatDate(doc.created_at)}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      doc.storage_status === 'verified' ? 'bg-green-100 text-green-800' :
                      doc.storage_status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                      doc.storage_status === 'archived' ? 'bg-gray-100 text-gray-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {doc.storage_status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right text-sm font-medium space-x-2">
                    <button
                      onClick={() => handleDownload(doc)}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      Download
                    </button>
                    <button
                      onClick={() => handleShare(doc)}
                      className="text-green-600 hover:text-green-900"
                    >
                      Share
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {documents.length === 0 && (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No documents found</h3>
            <p className="mt-1 text-sm text-gray-500">Try adjusting your filters or upload a new document.</p>
          </div>
        )}
      </div>

      {/* Pagination */}
      {documents.length > 0 && (
        <div className="mt-6 flex items-center justify-between">
          <div className="text-sm text-gray-700">
            Showing {page * limit + 1} to {page * limit + documents.length} documents
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(Math.max(0, page - 1))}
              disabled={page === 0}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <button
              onClick={() => setPage(page + 1)}
              disabled={documents.length < limit}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
