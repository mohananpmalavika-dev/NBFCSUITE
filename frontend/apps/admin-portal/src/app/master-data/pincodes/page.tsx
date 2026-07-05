"use client";

import { useState, useEffect } from "react";
import MasterDataTable, { StatusBadge } from "@/components/MasterDataTable";
import { MapPin, Search } from "lucide-react";

interface Pincode {
  id: number;
  pincode: string;
  city_id: number;
  city_name?: string;
  state_name?: string;
  area?: string;
  district?: string;
  is_active: boolean;
  created_at: string;
}

export default function PincodesPage() {
  const [data, setData] = useState<Pincode[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);
  const [searchQuery, setSearchQuery] = useState("");
  const [pincodeSearch, setPincodeSearch] = useState("");
  const [searchResult, setSearchResult] = useState<Pincode | null>(null);
  const pageSize = 20;

  const fetchPincodes = async (page: number, search: string = "") => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
        ...(search && { search })
      });

      const response = await fetch(`/api/v1/masterdata/pincodes?${params}`, {
        headers: { "Content-Type": "application/json" }
      });

      if (!response.ok) throw new Error("Failed to fetch pincodes");

      const result = await response.json();
      setData(result.items || []);
      setTotalRecords(result.total || 0);
    } catch (error) {
      console.error("Error fetching pincodes:", error);
      setData([]);
      setTotalRecords(0);
    } finally {
      setLoading(false);
    }
  };

  const handlePincodeSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!pincodeSearch || pincodeSearch.length !== 6) {
      alert("Please enter a valid 6-digit pincode");
      return;
    }

    try {
      const response = await fetch(`/api/v1/masterdata/pincodes/search/${pincodeSearch}`, {
        headers: { "Content-Type": "application/json" }
      });

      if (!response.ok) throw new Error("Pincode not found");

      const result = await response.json();
      setSearchResult(result);
    } catch (error) {
      console.error("Error searching pincode:", error);
      alert("Pincode not found in database");
      setSearchResult(null);
    }
  };

  useEffect(() => {
    fetchPincodes(currentPage, searchQuery);
  }, [currentPage]);

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setCurrentPage(1);
    fetchPincodes(1, query);
  };

  const columns = [
    {
      key: "pincode",
      label: "Pincode",
      render: (value: string) => (
        <span className="font-mono text-lg font-bold text-blue-600">
          {value}
        </span>
      )
    },
    {
      key: "area",
      label: "Area",
      render: (value: string) => (
        <span className="font-medium text-gray-900">{value || "-"}</span>
      )
    },
    {
      key: "city_name",
      label: "City",
      render: (value: string) => (
        <span className="text-gray-700">{value || "-"}</span>
      )
    },
    {
      key: "district",
      label: "District",
      render: (value: string) => (
        <span className="text-gray-700">{value || "-"}</span>
      )
    },
    {
      key: "state_name",
      label: "State",
      render: (value: string) => (
        <span className="text-gray-700">{value || "-"}</span>
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
      <div className="bg-gradient-to-r from-indigo-600 to-indigo-700 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <MapPin className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-bold">{totalRecords} Pincodes</div>
              <div className="text-sm text-indigo-100">
                Complete pincode database for India
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Pincode Search */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <form onSubmit={handlePincodeSearch} className="flex items-center gap-4">
            <label className="text-sm font-medium text-gray-700">Quick Search:</label>
            <div className="flex-1 max-w-md flex gap-2">
              <input
                type="text"
                value={pincodeSearch}
                onChange={(e) => setPincodeSearch(e.target.value.replace(/\D/g, '').slice(0, 6))}
                placeholder="Enter 6-digit pincode"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent font-mono text-lg"
                maxLength={6}
              />
              <button
                type="submit"
                className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
              >
                <Search className="w-4 h-4" />
                Search
              </button>
            </div>
          </form>

          {/* Search Result Display */}
          {searchResult && (
            <div className="mt-4 p-4 bg-indigo-50 border border-indigo-200 rounded-lg">
              <h3 className="font-semibold text-indigo-900 mb-2">Pincode Details:</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Pincode:</span>
                  <div className="font-mono font-bold text-indigo-600 text-lg">{searchResult.pincode}</div>
                </div>
                <div>
                  <span className="text-gray-600">Area:</span>
                  <div className="font-medium text-gray-900">{searchResult.area || "-"}</div>
                </div>
                <div>
                  <span className="text-gray-600">City:</span>
                  <div className="font-medium text-gray-900">{searchResult.city_name || "-"}</div>
                </div>
                <div>
                  <span className="text-gray-600">State:</span>
                  <div className="font-medium text-gray-900">{searchResult.state_name || "-"}</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <MasterDataTable
        title="Pincodes"
        description="Browse and manage Indian postal codes"
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
