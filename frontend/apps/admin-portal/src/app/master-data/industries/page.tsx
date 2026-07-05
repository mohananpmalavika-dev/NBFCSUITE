"use client";

import { useState, useEffect } from "react";
import MasterDataTable, { StatusBadge } from "@/components/MasterDataTable";
import { Factory } from "lucide-react";

interface Industry {
  id: number;
  name: string;
  code: string;
  sector: string;
  description?: string;
  risk_category?: string;
  is_active: boolean;
  created_at: string;
}

export default function IndustriesPage() {
  const [data, setData] = useState<Industry[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterSector, setFilterSector] = useState<string>("");
  const pageSize = 20;

  const fetchIndustries = async (page: number, search: string = "", sector: string = "") => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
        ...(search && { search }),
        ...(sector && { sector })
      });

      const response = await fetch(`/api/v1/masterdata/industries?${params}`, {
        headers: { "Content-Type": "application/json" }
      });

      if (!response.ok) throw new Error("Failed to fetch industries");

      const result = await response.json();
      setData(result.items || []);
      setTotalRecords(result.total || 0);
    } catch (error) {
      console.error("Error fetching industries:", error);
      setData([]);
      setTotalRecords(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIndustries(currentPage, searchQuery, filterSector);
  }, [currentPage, filterSector]);

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setCurrentPage(1);
    fetchIndustries(1, query, filterSector);
  };

  const columns = [
    {
      key: "code",
      label: "Code",
      render: (value: string) => (
        <span className="font-mono text-xs bg-pink-100 text-pink-800 px-2 py-1 rounded">
          {value}
        </span>
      )
    },
    {
      key: "name",
      label: "Industry",
      render: (value: string, row: Industry) => (
        <div>
          <div className="font-medium text-gray-900">{value}</div>
          {row.description && (
            <div className="text-xs text-gray-500 mt-0.5">{row.description}</div>
          )}
        </div>
      )
    },
    {
      key: "sector",
      label: "Sector",
      render: (value: string) => <span className="text-sm text-gray-700">{value}</span>
    },
    {
      key: "risk_category",
      label: "Risk Level",
      render: (value: string) => {
        const colors = {
          low: 'bg-green-100 text-green-800',
          medium: 'bg-yellow-100 text-yellow-800',
          high: 'bg-red-100 text-red-800'
        };
        return (
          <span className={`text-xs px-2 py-1 rounded ${colors[value?.toLowerCase() as keyof typeof colors] || 'bg-gray-100 text-gray-800'}`}>
            {value || 'Not Set'}
          </span>
        );
      }
    },
    {
      key: "is_active",
      label: "Status",
      render: (value: boolean) => <StatusBadge active={value} />
    }
  ];

  return (
    <div>
      <div className="bg-gradient-to-r from-pink-600 to-pink-700 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <Factory className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-bold">{totalRecords} Industries</div>
              <div className="text-sm text-pink-100">
                Manufacturing, Services, Agriculture and more
              </div>
            </div>
          </div>
        </div>
      </div>

      <MasterDataTable
        title="Industries"
        description="Manage industry sectors with risk categorization"
        columns={columns}
        data={data}
        loading={loading}
        totalRecords={totalRecords}
        currentPage={currentPage}
        pageSize={pageSize}
        onPageChange={setCurrentPage}
        onSearch={handleSearch}
      />
    </div>
  );
}
