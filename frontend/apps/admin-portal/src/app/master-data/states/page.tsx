"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import MasterDataTable, { StatusBadge } from "@/components/MasterDataTable";
import { Globe, Home, ChevronRight } from "lucide-react";
import Link from "next/link";
import { listStates, deleteMasterData } from "@/services/masterdata.service";

interface State {
  id: number;
  name: string;
  code: string;
  country_id: number;
  country_name?: string;
  is_active: boolean;
  created_at: string;
}

export default function StatesPage() {
  const router = useRouter();
  const [data, setData] = useState<State[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);
  const [searchQuery, setSearchQuery] = useState("");
  const pageSize = 20;

  // Fetch states data
  const fetchStates = async (page: number, search: string = "") => {
    setLoading(true);
    try {
      const result = await listStates({
        page,
        page_size: pageSize,
        ...(search && { search })
      });

      if (result.success && result.data) {
        setData(result.data.items || []);
        setTotalRecords(result.data.total || 0);
      }
    } catch (error) {
      console.error("Error fetching states:", error);
      setData([]);
      setTotalRecords(0);
    } finally {
      setLoading(false);
    }
  };
    } catch (error) {
      console.error("Error fetching states:", error);
      // Show error toast
      setData([]);
      setTotalRecords(0);
    } finally {
      setLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    fetchStates(currentPage, searchQuery);
  }, [currentPage]);

  // Handle search
  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setCurrentPage(1);
    fetchStates(1, query);
  };

  // Handle page change
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  // Handle add new
  const handleAdd = () => {
    // Open modal or navigate to form
    console.log("Add new state");
  };

  // Handle edit
  const handleEdit = (row: State) => {
    console.log("Edit state:", row);
    // Open modal with state data
  };

  // Handle delete
  const handleDelete = async (row: State) => {
    if (!confirm(`Are you sure you want to delete ${row.name}?`)) {
      return;
    }

    try {
      await deleteMasterData('states', row.id);
      // Refresh data
      fetchStates(currentPage, searchQuery);
    } catch (error) {
      console.error("Error deleting state:", error);
      alert("Failed to delete state");
    }
  };

  // Handle export
  const handleExport = () => {
    console.log("Export states");
    // Implement export to CSV/Excel
  };

  // Handle import
  const handleImport = () => {
    console.log("Import states");
    // Open import modal
  };

  // Table columns configuration
  const columns = [
    {
      key: "code",
      label: "State Code",
      render: (value: string) => (
        <span className="font-mono text-xs bg-gray-100 px-2 py-1 rounded">
          {value}
        </span>
      )
    },
    {
      key: "name",
      label: "State Name",
      render: (value: string) => (
        <span className="font-medium">{value}</span>
      )
    },
    {
      key: "country_name",
      label: "Country",
      render: (_: any, row: State) => (
        <span className="text-gray-600">India</span>
      )
    },
    {
      key: "is_active",
      label: "Status",
      render: (value: boolean) => <StatusBadge active={value} />
    },
    {
      key: "created_at",
      label: "Created At",
      render: (value: string) => (
        <span className="text-gray-600 text-sm">
          {new Date(value).toLocaleDateString('en-IN')}
        </span>
      )
    }
  ];

  return (
    <DashboardLayout>
      <div className="mb-6">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-sm text-gray-600 mb-4">
          <Link href="/dashboard" className="hover:text-blue-600 flex items-center gap-1">
            <Home className="w-4 h-4" />
            Dashboard
          </Link>
          <ChevronRight className="w-4 h-4" />
          <Link href="/master-data" className="hover:text-blue-600">
            Master Data
          </Link>
          <ChevronRight className="w-4 h-4" />
          <span className="text-gray-900 font-medium">States</span>
        </div>
      </div>
      
      <MasterDataTable
        title="States & Union Territories"
        description="Manage states and union territories of India"
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
    </DashboardLayout>
  );
}
