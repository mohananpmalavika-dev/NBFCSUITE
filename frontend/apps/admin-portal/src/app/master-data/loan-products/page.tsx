"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import MasterDataTable, { StatusBadge } from "@/components/MasterDataTable";
import { Wallet } from "lucide-react";

interface LoanProduct {
  id: number;
  name: string;
  code: string;
  category: string;
  description?: string;
  min_amount?: number;
  max_amount?: number;
  min_tenure_months?: number;
  max_tenure_months?: number;
  interest_rate?: number;
  is_active: boolean;
  created_at: string;
}

export default function LoanProductsPage() {
  const router = useRouter();
  const [data, setData] = useState<LoanProduct[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterCategory, setFilterCategory] = useState<string>("");
  const pageSize = 20;

  const fetchLoanProducts = async (page: number, search: string = "", category: string = "") => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
        ...(search && { search }),
        ...(category && { category })
      });

      const response = await fetch(`/api/v1/masterdata/loan-products?${params}`, {
        headers: {
          "Content-Type": "application/json",
        }
      });

      if (!response.ok) {
        throw new Error("Failed to fetch loan products");
      }

      const result = await response.json();
      setData(result.items || []);
      setTotalRecords(result.total || 0);
    } catch (error) {
      console.error("Error fetching loan products:", error);
      setData([]);
      setTotalRecords(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLoanProducts(currentPage, searchQuery, filterCategory);
  }, [currentPage, filterCategory]);

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setCurrentPage(1);
    fetchLoanProducts(1, query, filterCategory);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const handleAdd = () => {
    console.log("Add new loan product");
  };

  const handleEdit = (row: LoanProduct) => {
    console.log("Edit loan product:", row);
  };

  const handleDelete = async (row: LoanProduct) => {
    if (!confirm(`Are you sure you want to delete ${row.name}?`)) {
      return;
    }

    try {
      const response = await fetch(`/api/v1/masterdata/loan-products/${row.id}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        }
      });

      if (!response.ok) {
        throw new Error("Failed to delete loan product");
      }

      fetchLoanProducts(currentPage, searchQuery, filterCategory);
    } catch (error) {
      console.error("Error deleting loan product:", error);
    }
  };

  const handleExport = () => {
    console.log("Export loan products");
  };

  const handleImport = () => {
    console.log("Import loan products");
  };

  const formatCurrency = (amount?: number) => {
    if (!amount) return "-";
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  const columns = [
    {
      key: "code",
      label: "Code",
      render: (value: string) => (
        <span className="font-mono text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">
          {value}
        </span>
      )
    },
    {
      key: "name",
      label: "Product Name",
      render: (value: string, row: LoanProduct) => (
        <div>
          <div className="font-medium text-gray-900">{value}</div>
          {row.description && (
            <div className="text-xs text-gray-500 mt-0.5 line-clamp-1">{row.description}</div>
          )}
        </div>
      )
    },
    {
      key: "category",
      label: "Category",
      render: (value: string) => (
        <span className="text-sm text-gray-700">{value}</span>
      )
    },
    {
      key: "amount_range",
      label: "Loan Amount",
      render: (_: any, row: LoanProduct) => (
        <div className="text-sm text-gray-900">
          {formatCurrency(row.min_amount)} - {formatCurrency(row.max_amount)}
        </div>
      )
    },
    {
      key: "tenure_range",
      label: "Tenure",
      render: (_: any, row: LoanProduct) => (
        <div className="text-sm text-gray-700">
          {row.min_tenure_months || 0} - {row.max_tenure_months || 0} months
        </div>
      )
    },
    {
      key: "interest_rate",
      label: "Interest Rate",
      render: (value: number) => (
        <span className="text-sm font-medium text-blue-700">
          {value ? `${value}%` : "-"}
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
      <div className="bg-gradient-to-r from-purple-600 to-purple-700 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <Wallet className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-bold">{totalRecords} Loan Products</div>
              <div className="text-sm text-purple-100">
                Personal, Business, Gold, Vehicle and other loan products
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
              className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="">All Categories</option>
              <option value="Personal Loan">Personal Loan</option>
              <option value="Business Loan">Business Loan</option>
              <option value="Gold Loan">Gold Loan</option>
              <option value="Vehicle Loan">Vehicle Loan</option>
              <option value="Home Loan">Home Loan</option>
              <option value="Education Loan">Education Loan</option>
            </select>
            {filterCategory && (
              <button
                onClick={() => {
                  setFilterCategory("");
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
        title="Loan Products"
        description="Manage loan products with interest rates and eligibility criteria"
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
