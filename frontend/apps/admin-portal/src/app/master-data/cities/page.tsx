"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import MasterDataTable, { StatusBadge } from "@/components/MasterDataTable";
import { MapPin } from "lucide-react";

interface City {
  id: number;
  name: string;
  state_id: number;
  state_name?: string;
  state_code?: string;
  is_active: boolean;
  created_at: string;
}

export default function CitiesPage() {
  const router = useRouter();
  const [data, setData] = useState<City[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedState, setSelectedState] = useState<string>("");
  const pageSize = 20;

  // Fetch cities data
  const fetchCities = async (page: number, search: string = "", state: string = "") => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
        ...(search && { search }),
        ...(state && { state_id: state })
      });

      const response = await fetch(`/api/v1/masterdata/cities?${params}`, {
        headers: {
          "Content-Type": "application/json",
          // Add auth token from localStorage/cookie
          // "Authorization": `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error("Failed to fetch cities");
      }

      const result = await response.json();
      setData(result.items || []);
      setTotalRecords(result.total || 0);
    } catch (error) {
      console.error("Error fetching cities:", error);
      // Show error toast
      setData([]);
      setTotalRecords(0);
    } finally {
      setLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    fetchCities(currentPage, searchQuery, selectedState);
  }, [currentPage, selectedState]);

  // Handle search
  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setCurrentPage(1);
    fetchCities(1, query, selectedState);
  };

  // Handle page change
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  // Handle add new
  const handleAdd = () => {
    console.log("Add new city");
    // Open modal or navigate to form
  };

  // Handle edit
  const handleEdit = (row: City) => {
    console.log("Edit city:", row);
    // Open modal with city data
  };

  // Handle delete
  const handleDelete = async (row: City) => {
    if (!confirm(`Are you sure you want to delete ${row.name}?`)) {
      return;
    }

    try {
      const response = await fetch(`/api/v1/masterdata/cities/${row.id}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          // Add auth token
        }
      });

      if (!response.ok) {
        throw new Error("Failed to delete city");
      }

      // Show success toast
      // Refresh data
      fetchCities(currentPage, searchQuery, selectedState);
    } catch (error) {
      console.error("Error deleting city:", error);
      // Show error toast
    }
  };

  // Handle export
  const handleExport = () => {
    console.log("Export cities");
    // Implement export to CSV/Excel
  };

  // Handle import
  const handleImport = () => {
    console.log("Import cities");
    // Open import modal
  };

  // Table columns configuration
  const columns = [
    {
      key: "name",
      label: "City Name",
      render: (value: string) => (
        <span className="font-medium">{value}</span>
      )
    },
    {
      key: "state_name",
      label: "State",
      render: (value: string, row: City) => (
        <div>
          <div className="text-gray-900">{value || "-"}</div>
          {row.state_code && (
            <span className="text-xs text-gray-500 font-mono">({row.state_code})</span>
          )}
        </div>
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
    <div>
      {/* Header with City Stats */}
      <div className="bg-gradient-to-r from-purple-600 to-purple-700 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <MapPin className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-bold">{totalRecords} Cities</div>
              <div className="text-sm text-purple-100">
                Kerala focus with major cities across India
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex items-center gap-4">
            <label className="text-sm font-medium text-gray-700">Filter by State:</label>
            <select
              value={selectedState}
              onChange={(e) => {
                setSelectedState(e.target.value);
                setCurrentPage(1);
              }}
              className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="">All States</option>
              <option value="1">Kerala</option>
              <option value="2">Tamil Nadu</option>
              <option value="3">Karnataka</option>
              <option value="4">Maharashtra</option>
              <option value="5">Delhi</option>
              {/* Add more states dynamically */}
            </select>
            {selectedState && (
              <button
                onClick={() => {
                  setSelectedState("");
                  setCurrentPage(1);
                }}
                className="text-sm text-purple-600 hover:text-purple-800"
              >
                Clear filter
              </button>
            )}
          </div>
        </div>
      </div>

      <MasterDataTable
        title="Cities"
        description="Manage cities across India with state mapping"
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
