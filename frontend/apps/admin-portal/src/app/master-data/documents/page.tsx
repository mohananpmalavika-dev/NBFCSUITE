"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import MasterDataTable, { StatusBadge } from "@/components/MasterDataTable";
import { FileText, CheckCircle } from "lucide-react";

interface DocumentType {
  id: number;
  name: string;
  code: string;
  description?: string;
  is_mandatory: boolean;
  is_identity_proof: boolean;
  is_address_proof: boolean;
  is_income_proof: boolean;
  is_active: boolean;
  created_at: string;
}

export default function DocumentsPage() {
  const router = useRouter();
  const [data, setData] = useState<DocumentType[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterMandatory, setFilterMandatory] = useState<string>("");
  const pageSize = 20;

  // Fetch documents data
  const fetchDocuments = async (page: number, search: string = "", mandatory: string = "") => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
        ...(search && { search }),
        ...(mandatory && { is_mandatory: mandatory })
      });

      const response = await fetch(`/api/v1/masterdata/documents?${params}`, {
        headers: {
          "Content-Type": "application/json",
          // Add auth token from localStorage/cookie
          // "Authorization": `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error("Failed to fetch documents");
      }

      const result = await response.json();
      setData(result.items || []);
      setTotalRecords(result.total || 0);
    } catch (error) {
      console.error("Error fetching documents:", error);
      setData([]);
      setTotalRecords(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments(currentPage, searchQuery, filterMandatory);
  }, [currentPage, filterMandatory]);

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setCurrentPage(1);
    fetchDocuments(1, query, filterMandatory);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const handleAdd = () => {
    console.log("Add new document type");
  };

  const handleEdit = (row: DocumentType) => {
    console.log("Edit document:", row);
  };

  const handleDelete = async (row: DocumentType) => {
    if (!confirm(`Are you sure you want to delete ${row.name}?`)) {
      return;
    }

    try {
      const response = await fetch(`/api/v1/masterdata/documents/${row.id}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        }
      });

      if (!response.ok) {
        throw new Error("Failed to delete document");
      }

      fetchDocuments(currentPage, searchQuery, filterMandatory);
    } catch (error) {
      console.error("Error deleting document:", error);
    }
  };

  const handleExport = () => {
    console.log("Export documents");
  };

  const handleImport = () => {
    console.log("Import documents");
  };

  const columns = [
    {
      key: "code",
      label: "Code",
      render: (value: string) => (
        <span className="font-mono text-xs bg-orange-100 text-orange-800 px-2 py-1 rounded">
          {value}
        </span>
      )
    },
    {
      key: "name",
      label: "Document Name",
      render: (value: string, row: DocumentType) => (
        <div>
          <div className="font-medium text-gray-900 flex items-center gap-2">
            {value}
            {row.is_mandatory && (
              <span className="inline-flex items-center text-xs bg-red-100 text-red-700 px-1.5 py-0.5 rounded">
                Required
              </span>
            )}
          </div>
          {row.description && (
            <div className="text-xs text-gray-500 mt-0.5">{row.description}</div>
          )}
        </div>
      )
    },
    {
      key: "proof_types",
      label: "Proof Types",
      render: (_: any, row: DocumentType) => (
        <div className="flex flex-wrap gap-1">
          {row.is_identity_proof && (
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
              Identity
            </span>
          )}
          {row.is_address_proof && (
            <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">
              Address
            </span>
          )}
          {row.is_income_proof && (
            <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded">
              Income
            </span>
          )}
          {!row.is_identity_proof && !row.is_address_proof && !row.is_income_proof && (
            <span className="text-xs text-gray-500">-</span>
          )}
        </div>
      )
    },
    {
      key: "is_active",
      label: "Status",
      render: (value: boolean) => <StatusBadge active={value} />
    }
  ];

  return (
    <div>
      {/* Header with Document Stats */}
      <div className="bg-gradient-to-r from-orange-600 to-orange-700 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <FileText className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-bold">{totalRecords} Document Types</div>
              <div className="text-sm text-orange-100">
                Identity, Address, Income and other document types
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex items-center gap-4">
            <label className="text-sm font-medium text-gray-700">Filter:</label>
            <select
              value={filterMandatory}
              onChange={(e) => {
                setFilterMandatory(e.target.value);
                setCurrentPage(1);
              }}
              className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            >
              <option value="">All Documents</option>
              <option value="true">Mandatory Only</option>
              <option value="false">Optional Only</option>
            </select>
            {filterMandatory && (
              <button
                onClick={() => {
                  setFilterMandatory("");
                  setCurrentPage(1);
                }}
                className="text-sm text-orange-600 hover:text-orange-800"
              >
                Clear filter
              </button>
            )}
          </div>
        </div>
      </div>

      <MasterDataTable
        title="Document Types"
        description="Manage document types for KYC and loan applications"
        columns={columns}
        data={data}
        loading={loading}
        totalRecords={totalRecords}
        currentPage={currentPage}
        pageSize={pageSize}
        onPageChange={handlePageChange}
        onSearch={handleSearch}
        onAdd={handleAdd}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onImport={handleImport}
        onExport={handleExport}
      />
    </div>
  );
}
