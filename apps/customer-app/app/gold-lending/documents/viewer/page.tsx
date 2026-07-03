'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';

export default function DocumentViewerPage() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<any | null>(null);
  const [versions, setVersions] = useState<any[]>([]);
  const [metadata, setMetadata] = useState<any[]>([]);
  const [tags, setTags] = useState<any[]>([]);
  const [accessLogs, setAccessLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'details' | 'versions' | 'metadata' | 'tags' | 'activity'>('details');

  useEffect(() => {
    loadRecentDocuments();
  }, []);

  const loadRecentDocuments = async () => {
    try {
      const docsData = await goldApi.listDocuments({ limit: 10 });
      setDocuments(docsData);
      if (docsData.length > 0) {
        loadDocument(docsData[0].document_id);
      }
    } catch (err: any) {
      setError('Failed to load documents: ' + err.message);
    }
  };

  const loadDocument = async (documentId: string) => {
    setLoading(true);
    setError('');
    
    try {
      const [doc, vers, meta, docTags, logs] = await Promise.all([
        goldApi.getDocument(documentId),
        goldApi.listDocumentVersions(documentId),
        goldApi.listDocumentMetadata(documentId),
        goldApi.listDocumentTagsForDocument(documentId),
        goldApi.getDocumentAccessLogs(documentId, 0, 20)
      ]);
      
      setSelectedDoc(doc);
      setVersions(vers);
      setMetadata(meta);
      setTags(docTags);
      setAccessLogs(logs);
      
      // Log access
      await goldApi.createDocumentAccessLog({
        document_id: documentId,
        action_type: 'view',
        user_id: 'current-user-id', // TODO: Replace with actual user ID
        access_result: 'success',
        ip_address: '0.0.0.0',
        access_device: 'web'
      });
    } catch (err: any) {
      setError('Failed to load document: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!selectedDoc) return;
    
    try {
      await goldApi.createDocumentAccessLog({
        document_id: selectedDoc.document_id,
        action_type: 'download',
        user_id: 'current-user-id',
        access_result: 'success',
        download_size_bytes: selectedDoc.file_size_bytes
      });
      
      // TODO: Implement actual download
      alert(`Downloading: ${selectedDoc.title}`);
    } catch (err: any) {
      alert('Failed to log download: ' + err.message);
    }
  };

  const handlePrint = async () => {
    if (!selectedDoc) return;
    
    try {
      await goldApi.createDocumentAccessLog({
        document_id: selectedDoc.document_id,
        action_type: 'print',
        user_id: 'current-user-id',
        access_result: 'success'
      });
      
      // TODO: Implement actual print
      alert(`Printing: ${selectedDoc.title}`);
    } catch (err: any) {
      alert('Failed to log print: ' + err.message);
    }
  };

  const handleRestoreVersion = async (versionNumber: number) => {
    if (!selectedDoc) return;
    if (!confirm(`Restore version ${versionNumber}?`)) return;
    
    try {
      await goldApi.restoreDocumentVersion(
        selectedDoc.document_id,
        versionNumber,
        'current-user-id'
      );
      alert('Version restored successfully');
      loadDocument(selectedDoc.document_id);
    } catch (err: any) {
      alert('Failed to restore version: ' + err.message);
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  if (loading && !selectedDoc) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
            <p className="text-gray-600">Loading document...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Document Viewer</h1>
        <p className="text-gray-600">View and manage document details</p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      <div className="grid grid-cols-12 gap-6">
        {/* Document List Sidebar */}
        <div className="col-span-3">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Documents</h3>
            <div className="space-y-2">
              {documents.map(doc => (
                <button
                  key={doc.document_id}
                  onClick={() => loadDocument(doc.document_id)}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                    selectedDoc?.document_id === doc.document_id
                      ? 'bg-blue-50 border-2 border-blue-500'
                      : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
                  }`}
                >
                  <div className="text-sm font-medium text-gray-900 truncate">
                    {doc.title}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {doc.document_number}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="col-span-9">
          {selectedDoc ? (
            <>
              {/* Document Header */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">
                      {selectedDoc.title}
                    </h2>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <span className="flex items-center">
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                        </svg>
                        {selectedDoc.document_number}
                      </span>
                      <span className="flex items-center">
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {formatDate(selectedDoc.created_at)}
                      </span>
                      <span className="flex items-center">
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                        </svg>
                        {formatFileSize(selectedDoc.file_size_bytes || 0)}
                      </span>
                    </div>
                  </div>
                  
                  <div className="flex gap-2">
                    <button
                      onClick={handleDownload}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                      Download
                    </button>
                    <button
                      onClick={handlePrint}
                      className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 flex items-center gap-2"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                      </svg>
                      Print
                    </button>
                  </div>
                </div>

                {/* Document Preview Placeholder */}
                <div className="bg-gray-100 rounded-lg p-8 text-center">
                  <svg className="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p className="text-gray-600">Document preview not available</p>
                  <p className="text-sm text-gray-500 mt-1">Download to view the full document</p>
                </div>
              </div>

              {/* Tabs */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                <div className="border-b border-gray-200">
                  <nav className="flex">
                    {['details', 'versions', 'metadata', 'tags', 'activity'].map(tab => (
                      <button
                        key={tab}
                        onClick={() => setActiveTab(tab as any)}
                        className={`px-6 py-3 text-sm font-medium capitalize ${
                          activeTab === tab
                            ? 'border-b-2 border-blue-500 text-blue-600'
                            : 'text-gray-600 hover:text-gray-900'
                        }`}
                      >
                        {tab}
                      </button>
                    ))}
                  </nav>
                </div>

                <div className="p-6">
                  {activeTab === 'details' && (
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="text-sm font-medium text-gray-500">Document Type</label>
                          <p className="mt-1 text-sm text-gray-900">{selectedDoc.document_type}</p>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-gray-500">Storage Status</label>
                          <p className="mt-1">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              selectedDoc.storage_status === 'verified' ? 'bg-green-100 text-green-800' :
                              selectedDoc.storage_status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-blue-100 text-blue-800'
                            }`}>
                              {selectedDoc.storage_status}
                            </span>
                          </p>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-gray-500">File Name</label>
                          <p className="mt-1 text-sm text-gray-900">{selectedDoc.file_name}</p>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-gray-500">MIME Type</label>
                          <p className="mt-1 text-sm text-gray-900">{selectedDoc.mime_type}</p>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-gray-500">Current Version</label>
                          <p className="mt-1 text-sm text-gray-900">{selectedDoc.current_version}</p>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-gray-500">File Hash</label>
                          <p className="mt-1 text-sm text-gray-900 font-mono truncate">{selectedDoc.file_hash || 'N/A'}</p>
                        </div>
                      </div>
                      
                      {selectedDoc.description && (
                        <div>
                          <label className="text-sm font-medium text-gray-500">Description</label>
                          <p className="mt-1 text-sm text-gray-900">{selectedDoc.description}</p>
                        </div>
                      )}
                    </div>
                  )}

                  {activeTab === 'versions' && (
                    <div className="space-y-3">
                      {versions.length === 0 ? (
                        <p className="text-center text-gray-500 py-8">No version history available</p>
                      ) : (
                        versions.map(version => (
                          <div key={version.version_id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                            <div>
                              <div className="font-medium text-gray-900">
                                Version {version.version_number}
                                {version.version_number === selectedDoc.current_version && (
                                  <span className="ml-2 px-2 py-1 text-xs bg-green-100 text-green-800 rounded">Current</span>
                                )}
                              </div>
                              <div className="text-sm text-gray-600 mt-1">
                                {formatDate(version.created_at)}
                              </div>
                              {version.change_description && (
                                <div className="text-sm text-gray-500 mt-1">{version.change_description}</div>
                              )}
                            </div>
                            {version.version_number !== selectedDoc.current_version && (
                              <button
                                onClick={() => handleRestoreVersion(version.version_number)}
                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                              >
                                Restore
                              </button>
                            )}
                          </div>
                        ))
                      )}
                    </div>
                  )}

                  {activeTab === 'metadata' && (
                    <div className="space-y-3">
                      {metadata.length === 0 ? (
                        <p className="text-center text-gray-500 py-8">No metadata available</p>
                      ) : (
                        metadata.map(item => (
                          <div key={item.metadata_id} className="flex items-start justify-between p-4 bg-gray-50 rounded-lg">
                            <div className="flex-1">
                              <div className="font-medium text-gray-900">{item.metadata_key}</div>
                              <div className="text-sm text-gray-600 mt-1">{item.metadata_value}</div>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  )}

                  {activeTab === 'tags' && (
                    <div className="flex flex-wrap gap-2">
                      {tags.length === 0 ? (
                        <p className="text-center text-gray-500 py-8 w-full">No tags assigned</p>
                      ) : (
                        tags.map(tag => (
                          <span
                            key={tag.tag_id}
                            className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
                          >
                            {tag.tag_name}
                          </span>
                        ))
                      )}
                    </div>
                  )}

                  {activeTab === 'activity' && (
                    <div className="space-y-3">
                      {accessLogs.length === 0 ? (
                        <p className="text-center text-gray-500 py-8">No activity logs available</p>
                      ) : (
                        accessLogs.map(log => (
                          <div key={log.log_id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                            <div className="flex items-center gap-3">
                              <div className={`w-2 h-2 rounded-full ${
                                log.access_result === 'success' ? 'bg-green-500' : 'bg-red-500'
                              }`}></div>
                              <div>
                                <div className="font-medium text-gray-900 capitalize">{log.action_type}</div>
                                <div className="text-sm text-gray-600">{formatDate(log.accessed_at)}</div>
                              </div>
                            </div>
                            <span className={`px-2 py-1 text-xs font-medium rounded ${
                              log.access_result === 'success' 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {log.access_result}
                            </span>
                          </div>
                        ))
                      )}
                    </div>
                  )}
                </div>
              </div>
            </>
          ) : (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
              <svg className="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Document Selected</h3>
              <p className="text-gray-600">Select a document from the sidebar to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
