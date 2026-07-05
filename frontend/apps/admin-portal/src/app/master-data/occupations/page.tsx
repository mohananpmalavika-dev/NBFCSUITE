"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import MasterDataTable, { StatusBadge } from "@/components/MasterDataTable";
import { Briefcase } from "lucide-react";

interface Occupation {
  id: number;
  name: string;
  code: string;
  category: string;
  description?: string;
  risk_category?: string;
  is_active: boolean;
  created_at: string;
}

export default function OccupationsPage() {
  const router = useRouter();
  const [data, setData] = useState<Occupation[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterCategory, setFilterCategory] = useState<string>("");
  const pageSize = 20;

  const fetchOccupations = async (page: number, search: string = "", category: string = "") => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
        ...(search && { search }),
        ...(category && { category })
      });

      const response = await fetch(`/api/v1/masterdata/occupations?${params}`, {
        headers: {
          "Content-Type": "application/json",
        }
      });

      if (!response.ok) {
        throw new Error("Failed to fetch occupations");
      }

      const result = await response.json();
      setData(result.items || []);
      setTotalRecords(result.total || 0);
    } catch (error) {
      console.error("Error fetching occupations:", error);
      setData([]);
      setTotalRecords(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOccupations(currentPage, searchQuery, filterCategory);
  }, [currentPage, filterCategory]);

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setCurrentPage(1);
    fetchOccupations(1, query, filterCategory);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const handleAdd = () => {
    console.log("Add new occupation");
  };

  const handleEdit = (row: Occupation) => {
    console.log("Edit occupation:", row);
  };

  const handleDelete = async (row: Occupation) => {
    if (!confirm(`Are you sure you want to delete ${row.name}?`)) {
      return;
    }

    try {
      const response = await fetch(`/api/v1/masterdata/occupations/${row.id}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        }
      });

      if (!response.ok) {
        throw new Error("Failed to delete occupation");
      }

      fetchOccupations(currentPage, searchQuery, filterCategory);
    } catch (error) {
      console.error("Error deleting occupation:", error);
    }
  };

  const handleExport = () => {
    console.log("Export occupations");
  };

  const handleImport = () => {
    console.log("Import occupations");
  };

  const getRiskBadgeColor = (risk?: string) => {
    switch (risk?.toLowerCase()) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const columns = [
    {
      key: "code",
      label: "Code",
      render: (value: string) => (
        <span className="font-mono text-xs bg-cyan-100 text-cyan-800 px-2 py-1 rounded">
          {value}
        </span>
      )
    },
    {
      key: "name",
      label: "Occupation",
      render: (value: string, row: Occupation) => (
        <div>
          <div className="font-medium text-gray-900">{value}</div>
          {row.description && (
            <div className="text-xs text-gray-500 mt-0.5">{row.description}</div>
          )}
        </div>
      )
    },
    {
      key: "category",
      label: "Category",
      render: (value: string) => (
        <span className="text-sm text-gray-700">
          {value}
        </span>
      )
    },
    {
      key: "risk_category",
      label: "Risk Level",
      render: (value: string) => (
        <span className={`text-xs px-2 py-1 rounded ${getRiskBadgeColor(value)}`}>
          {value || 'Not Set'}
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
      {/* Header */}
      <div className="bg-gradient-to-r from-cyan-600 to-cyan-700 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <Briefcase className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-bold">{totalRecords} Occupations</div>
              <div className="text-sm text-cyan-100">
                Salaried, Self-Employed, Business and Professional categories
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex items-center gap-4">
            <label className="text-sm font-medium text-gray-700">Category:</label>
            <select
              value={filterCategory}
              onChange={(e) => {
                setFilterCategory(e.target.value);
                setCurrentPage(1);
              }}
              className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
            >
              <option value="">All Categories</option>
              <option value="Salaried">Salaried</option>
              <option value="Self-Employed">Self-Employed</option>
              <option value="Business">Business</option>
              <option value="Professional">Professional</option>
              <option value="Pensioner">Pensioner</option>
              <option value="Other">Other</option>
            </select>
            {filterCategory && (
              <button
                onClick={() => {
                  setFilterCategory("");
                  setCurrentPage(1);
                }}
                className="text-sm text-cyan-600 hover:text-cyan-800"
              >
                Clear filter
              </button>
            )}
          </div>
        </div>
      </div>

      <MasterDataTable
        title="Occupations"
        description="Manage occupation types with risk categorization"
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
