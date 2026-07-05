"use client";

import { useState, useEffect } from "react";
import MasterDataTable, { StatusBadge } from "@/components/MasterDataTable";
import { Building2 } from "lucide-react";

interface BankBranch {
  id: number;
  bank_id: number;
  bank_name?: string;
  branch_name: string;
  ifsc_code: string;
  micr_code?: string;
  address?: string;
  city_name?: string;
  state_name?: string;
  pincode?: string;
  phone?: string;
  is_active: boolean;
  created_at: string;
}

export default function BankBranchesPage() {
  const [data, setData] = useState<BankBranch[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedBank, setSelectedBank] = useState<string>("");
  const pageSize = 20;

  const fetchBranches = async (page: number, search: string = "", bank: string = "") => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
        ...(search && { search }),
        ...(bank && { bank_id: bank })
      });

      const response = await fetch(`/api/v1/masterdata/bank-branches?${params}`, {
        headers: { "Content-Type": "application/json" }
      });

      if (!response.ok) throw new Error("Failed to fetch bank branches");

      const result = await response.json();
      setData(result.items || []);
      setTotalRecords(result.total || 0);
    } catch (error) {
      console.error("Error fetching bank branches:", error);
      setData([]);
      setTotalRecords(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBranches(currentPage, searchQuery, selectedBank);
  }, [currentPage, selectedBank]);

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setCurrentPage(1);
    fetchBranches(1, query, selectedBank);
  };

  const columns = [
    {
      key: "ifsc_code",
      label: "IFSC Code",
      render: (value: string) => (
        <span className="font-mono text-xs bg-green-100 text-green-800 px-2 py-1 rounded font-semibold">
          {value}
        </span>
      )
    },
    {
      key: "branch_name",
      label: "Branch",
      render: (value: string, row: BankBranch) => (
        <div>
          <div className="font-medium text-gray-900">{value}</div>
          {row.bank_name && (
            <div className="text-xs text-gray-500 mt-0.5">{row.bank_name}</div>
          )}
        </div>
      )
    },
    {
      key: "location",
      label: "Location",
      render: (_: any, row: BankBranch) => (
        <div className="text-sm">
          {row.city_name && <div className="text-gray-900">{row.city_name}</div>}
          {row.state_name && <div className="text-xs text-gray-500">{row.state_name}</div>}
        </div>
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
      key: "phone",
      label: "Contact",
      render: (value: string) => (
        <span className="text-sm text-gray-600">{value || "-"}</span>
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
      <div className="bg-gradient-to-r from-green-600 to-green-700 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <Building2 className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-bold">{totalRecords} Bank Branches</div>
              <div className="text-sm text-green-100">
                Complete branch network with IFSC and MICR codes
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex items-center gap-4">
            <label className="text-sm font-medium text-gray-700">Filter by Bank:</label>
            <select
              value={selectedBank}
              onChange={(e) => {
                setSelectedBank(e.target.value);
                setCurrentPage(1);
              }}
              className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="">All Banks</option>
              <option value="1">State Bank of India</option>
              <option value="2">HDFC Bank</option>
              <option value="3">ICICI Bank</option>
              <option value="4">Axis Bank</option>
              <option value="5">Punjab National Bank</option>
              {/* Add more banks dynamically */}
            </select>
            {selectedBank && (
              <button
                onClick={() => {
                  setSelectedBank("");
                  setCurrentPage(1);
                }}
                className="text-sm text-green-600 hover:text-green-800"
              >
                Clear filter
              </button>
            )}
          </div>
        </div>
      </div>

      <MasterDataTable
        title="Bank Branches"
        description="Browse bank branches with complete IFSC and contact details"
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
