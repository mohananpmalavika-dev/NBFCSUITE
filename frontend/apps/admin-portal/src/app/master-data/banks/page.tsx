"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import MasterDataTable, { StatusBadge } from "@/components/MasterDataTable";
import { Building2, ExternalLink } from "lucide-react";

interface Bank {
  id: number;
  name: string;
  short_name: string;
  code: string;
  ifsc_prefix?: string;
  micr_code?: string;
  swift_code?: string;
  is_active: boolean;
  created_at: string;
}

export default function BanksPage() {
  const router = useRouter();
  const [data, setData] = useState<Bank[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);
  const [searchQuery, setSearchQuery] = useState("");
  const pageSize = 20;

  // Fetch banks data
  const fetchBanks = async (page: number, search: string = "") => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
        ...(search && { search })
      });

      const response = await fetch(`/api/v1/masterdata/banks?${params}`, {
        headers: {
          "Content-Type": "application/json",
          // Add auth token from localStorage/cookie
          // "Authorization": `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error("Failed to fetch banks");
      }

      const result = await response.json();
      setData(result.items || []);
      setTotalRecords(result.total || 0);
    } catch (error) {
      console.error("Error fetching banks:", error);
      // Show error toast
      setData([]);
      setTotalRecords(0);
    } finally {
      setLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    fetchBanks(currentPage, searchQuery);
  }, [currentPage]);

  // Handle search
  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setCurrentPage(1);
    fetchBanks(1, query);
  };

  // Handle page change
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  // Handle add new
  const handleAdd = () => {
    console.log("Add new bank");
    // Open modal or navigate to form
  };

  // Handle edit
  const handleEdit = (row: Bank) => {
    console.log("Edit bank:", row);
    // Open modal with bank data
  };

  // Handle delete
  const handleDelete = async (row: Bank) => {
    if (!confirm(`Are you sure you want to delete ${row.name}?`)) {
      return;
    }

    try {
      const response = await fetch(`/api/v1/masterdata/banks/${row.id}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          // Add auth token
        }
      });

      if (!response.ok) {
        throw new Error("Failed to delete bank");
      }

      // Show success toast
      // Refresh data
      fetchBanks(currentPage, searchQuery);
    } catch (error) {
      console.error("Error deleting bank:", error);
      // Show error toast
    }
  };

  // Handle export
  const handleExport = () => {
    console.log("Export banks");
    // Implement export to CSV/Excel
  };

  // Handle import
  const handleImport = () => {
    console.log("Import banks");
    // Open import modal
  };

  // Table columns configuration
  const columns = [
    {
      key: "code",
      label: "Bank Code",
      render: (value: string) => (
        <span className="font-mono text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
          {value}
        </span>
      )
    },
    {
      key: "name",
      label: "Bank Name",
      render: (value: string, row: Bank) => (
        <div>
          <div className="font-medium text-gray-900">{value}</div>
          {row.short_name && (
            <div className="text-xs text-gray-500 mt-0.5">{row.short_name}</div>
          )}
        </div>
      )
    },
    {
      key: "ifsc_prefix",
      label: "IFSC Prefix",
      render: (value: string) => (
        <span className="font-mono text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
          {value || "N/A"}
        </span>
      )
    },
    {
      key: "micr_code",
      label: "MICR Code",
      render: (value: string) => (
        <span className="font-mono text-xs text-gray-600">
          {value || "-"}
        </span>
      )
    },
    {
      key: "swift_code",
      label: "SWIFT Code",
      render: (value: string) => (
        <span className="font-mono text-xs text-gray-600">
          {value || "-"}
        </span>
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
      {/* Header with Bank Count Stats */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <Building2 className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-bold">{totalRecords} Banks</div>
              <div className="text-sm text-blue-100">
                Including all major nationalized, private and scheduled banks
              </div>
            </div>
          </div>
        </div>
      </div>

      <MasterDataTable
        title="Banks"
        description="Manage banks with IFSC, MICR, and SWIFT codes"
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
