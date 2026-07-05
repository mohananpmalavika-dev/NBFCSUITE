"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { 
  FileText, 
  Upload, 
  Eye, 
  Download, 
  CheckCircle, 
  XCircle, 
  Clock, 
  AlertTriangle,
  Filter,
  X
} from "lucide-react";

interface Document {
  id: number;
  customer_id: number;
  document_type_id: number;
  document_type_name?: string;
  document_number: string;
  file_path?: string;
  file_url?: string;
  status: string;
  verified_at?: string;
  verified_by_name?: string;
  rejection_reason?: string;
  issue_date?: string;
  expiry_date?: string;
  is_expired: boolean;
  remarks?: string;
  created_at: string;
}

interface DocumentType {
  id: number;
  name: string;
  code: string;
  is_mandatory: boolean;
}

export default function CustomerDocumentsPage() {
  const params = useParams();
  const customerId = params?.id as string;

  const [documents, setDocuments] = useState<Document[]>([]);
  const [documentTypes, setDocumentTypes] = useState<DocumentType[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [filterType, setFilterType] = useState<number>(0);

  useEffect(() => {
    if (customerId) {
      fetchDocuments();
      fetchDocumentTypes();
    }
  }, [customerId, filterStatus, filterType]);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      let url = `/api/v1/customers/${customerId}/documents`;
      const params = new URLSearchParams();
      
      if (filterStatus !== "all") {
        params.append("status", filterStatus);
      }
      if (filterType > 0) {
        params.append("document_type_id", filterType.toString());
      }

      if (params.toString()) {
        url += `?${params}`;
      }

      const response = await fetch(url, {
        headers: { "Content-Type": "application/json" }
      });

      if (response.ok) {
        const data = await response.json();
        setDocuments(data);
      }
    } catch (error) {
      console.error("Error fetching documents:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchDocumentTypes = async () => {
    try {
      const response = await fetch("/api/v1/masterdata/document-types", {
        headers: { "Content-Type": "application/json" }
      });

      if (response.ok) {
        const data = await response.json();
        setDocumentTypes(data.items || data);
      }
    } catch (error) {
      console.error("Error fetching document types:", error);
    }
  };

  const handleVerify = async (documentId: number, approve: boolean) => {
    const remarks = approve 
      ? null 
      : prompt("Enter rejection reason:");
    
    if (!approve && !remarks) return;

    try {
      const response = await fetch(
        `/api/v1/customers/${customerId}/documents/${documentId}/verify`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            verified: approve,
            remarks: remarks || undefined
          })
        }
      );

      if (response.ok) {
        await fetchDocuments();
        alert(approve ? "Document verified successfully" : "Document rejected");
      } else {
        alert("Failed to update document status");
      }
    } catch (error) {
      console.error("Error verifying document:", error);
      alert("Failed to update document status");
    }
  };

  const getStatusBadge = (status: string, isExpired: boolean) => {
    if (isExpired) {
      return (
        <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
          <AlertTriangle className="w-3 h-3 mr-1" />
          Expired
        </span>
      );
    }

    const badges = {
      pending: { 
        icon: Clock, 
        bg: "bg-yellow-100", 
        text: "text-yellow-800", 
        label: "Pending" 
      },
      submitted: { 
        icon: Clock, 
        bg: "bg-blue-100", 
        text: "text-blue-800", 
        label: "Submitted" 
      },
      verified: { 
        icon: CheckCircle, 
        bg: "bg-green-100", 
        text: "text-green-800", 
        label: "Verified" 
      },
      rejected: { 
        icon: XCircle, 
        bg: "bg-red-100", 
        text: "text-red-800", 
        label: "Rejected" 
      }
    };

    const badge = badges[status as keyof typeof badges] || badges.pending;
    const Icon = badge.icon;

    return (
      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${badge.bg} ${badge.text}`}>
        <Icon className="w-3 h-3 mr-1" />
        {badge.label}
      </span>
    );
  };

  const stats = {
    total: documents.length,
    verified: documents.filter(d => d.status === 'verified').length,
    pending: documents.filter(d => d.status === 'pending' || d.status === 'submitted').length,
    rejected: documents.filter(d => d.status === 'rejected').length,
    expired: documents.filter(d => d.is_expired).length
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Documents</h2>
          <p className="text-sm text-gray-600 mt-1">
            Manage customer documents, verification, and compliance
          </p>
        </div>
        <button
          onClick={() => alert("Document upload UI coming soon!")}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Upload className="w-4 h-4" />
          Upload Document
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{stats.total}</p>
            </div>
            <FileText className="w-8 h-8 text-gray-600 opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Verified</p>
              <p className="text-2xl font-bold text-green-600 mt-1">{stats.verified}</p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-600 opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Pending</p>
              <p className="text-2xl font-bold text-yellow-600 mt-1">{stats.pending}</p>
            </div>
            <Clock className="w-8 h-8 text-yellow-600 opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Rejected</p>
              <p className="text-2xl font-bold text-red-600 mt-1">{stats.rejected}</p>
            </div>
            <XCircle className="w-8 h-8 text-red-600 opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Expired</p>
              <p className="text-2xl font-bold text-gray-600 mt-1">{stats.expired}</p>
            </div>
            <AlertTriangle className="w-8 h-8 text-gray-600 opacity-20" />
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center gap-4">
          <Filter className="w-5 h-5 text-gray-400" />
          
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">Status:</span>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All</option>
              <option value="pending">Pending</option>
              <option value="submitted">Submitted</option>
              <option value="verified">Verified</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">Type:</span>
            <select
              value={filterType}
              onChange={(e) => setFilterType(Number(e.target.value))}
              className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value={0}>All Types</option>
              {documentTypes.map((type) => (
                <option key={type.id} value={type.id}>
                  {type.name}
                </option>
              ))}
            </select>
          </div>

          {(filterStatus !== "all" || filterType > 0) && (
            <button
              onClick={() => {
                setFilterStatus("all");
                setFilterType(0);
              }}
              className="flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900"
            >
              <X className="w-4 h-4" />
              Clear Filters
            </button>
          )}
        </div>
      </div>

      {/* Documents Grid */}
      {documents.length === 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-sm text-gray-600 mb-4">
            {filterStatus !== "all" || filterType > 0 
              ? "No documents match your filters" 
              : "No documents uploaded yet"}
          </p>
          <button
            onClick={() => alert("Document upload UI coming soon!")}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            Upload your first document
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow"
            >
              {/* Document Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <FileText className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-gray-900">
                      {doc.document_type_name}
                    </h3>
                    <p className="text-xs text-gray-500 font-mono">{doc.document_number}</p>
                  </div>
                </div>
              </div>

              {/* Status Badge */}
              <div className="mb-3">
                {getStatusBadge(doc.status, doc.is_expired)}
              </div>

              {/* Document Details */}
              <div className="space-y-2 text-xs text-gray-600 mb-4">
                {doc.issue_date && (
                  <div className="flex justify-between">
                    <span>Issue Date:</span>
                    <span className="font-medium text-gray-900">
                      {new Date(doc.issue_date).toLocaleDateString('en-IN')}
                    </span>
                  </div>
                )}
                {doc.expiry_date && (
                  <div className="flex justify-between">
                    <span>Expiry Date:</span>
                    <span className={`font-medium ${doc.is_expired ? 'text-red-600' : 'text-gray-900'}`}>
                      {new Date(doc.expiry_date).toLocaleDateString('en-IN')}
                    </span>
                  </div>
                )}
                {doc.verified_at && doc.verified_by_name && (
                  <div className="flex justify-between">
                    <span>Verified By:</span>
                    <span className="font-medium text-gray-900">{doc.verified_by_name}</span>
                  </div>
                )}
              </div>

              {/* Rejection Reason */}
              {doc.status === 'rejected' && doc.rejection_reason && (
                <div className="bg-red-50 border border-red-100 rounded p-2 mb-4">
                  <p className="text-xs text-red-800">
                    <strong>Rejected:</strong> {doc.rejection_reason}
                  </p>
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center gap-2">
                {doc.file_url && (
                  <>
                    <button
                      onClick={() => window.open(doc.file_url, '_blank')}
                      className="flex-1 flex items-center justify-center gap-1 px-3 py-1.5 text-xs font-medium text-gray-700 bg-gray-100 rounded hover:bg-gray-200"
                    >
                      <Eye className="w-3 h-3" />
                      View
                    </button>
                    <button
                      onClick={() => window.open(doc.file_url, '_blank')}
                      className="flex-1 flex items-center justify-center gap-1 px-3 py-1.5 text-xs font-medium text-gray-700 bg-gray-100 rounded hover:bg-gray-200"
                    >
                      <Download className="w-3 h-3" />
                      Download
                    </button>
                  </>
                )}
                
                {(doc.status === 'pending' || doc.status === 'submitted') && (
                  <>
                    <button
                      onClick={() => handleVerify(doc.id, true)}
                      className="flex-1 flex items-center justify-center gap-1 px-3 py-1.5 text-xs font-medium text-white bg-green-600 rounded hover:bg-green-700"
                    >
                      <CheckCircle className="w-3 h-3" />
                      Verify
                    </button>
                    <button
                      onClick={() => handleVerify(doc.id, false)}
                      className="flex-1 flex items-center justify-center gap-1 px-3 py-1.5 text-xs font-medium text-white bg-red-600 rounded hover:bg-red-700"
                    >
                      <XCircle className="w-3 h-3" />
                      Reject
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
