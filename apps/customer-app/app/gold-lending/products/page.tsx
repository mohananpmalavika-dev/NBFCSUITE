"use client";

import { useEffect, useState } from "react";
import { goldApi } from "../goldApi";

interface GoldProductSummary {
  id: string;
  product_code: string;
  product_name: string;
  product_type: string;
  is_active: boolean;
  base_rate?: number;
  ltv_percent?: number;
  min_amount?: number;
  max_amount?: number;
}

export default function GoldProductsPage() {
  const [products, setProducts] = useState<GoldProductSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterActive, setFilterActive] = useState<boolean | null>(true);

  useEffect(() => {
    loadProducts();
  }, [filterActive]);

  const loadProducts = async () => {
    try {
      setLoading(true);
      const data = await goldApi.listProducts(filterActive);
      setProducts(data);
      setError(null);
    } catch (err) {
      setError("Failed to load gold loan products");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getProductTypeBadge = (type: string) => {
    const badges: Record<string, { color: string; label: string }> = {
      jewel_loan: { color: "bg-blue-100 text-blue-800", label: "Jewel Loan" },
      bullet_loan: { color: "bg-green-100 text-green-800", label: "Bullet Loan" },
      od: { color: "bg-purple-100 text-purple-800", label: "Overdraft" },
      instant: { color: "bg-orange-100 text-orange-800", label: "Instant Loan" },
      sme: { color: "bg-indigo-100 text-indigo-800", label: "SME Loan" },
      agri: { color: "bg-emerald-100 text-emerald-800", label: "Agri Loan" },
      digital: { color: "bg-pink-100 text-pink-800", label: "Digital Loan" },
    };
    const badge = badges[type] || { color: "bg-gray-100 text-gray-800", label: type };
    return (
      <span className={`px-3 py-1 rounded-full text-sm font-medium ${badge.color}`}>
        {badge.label}
      </span>
    );
  };

  const formatCurrency = (amount?: number) => {
    if (!amount) return "N/A";
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Gold Loan Products</h1>
          <p className="text-gray-600">
            Manage and configure gold loan products with interest rates, limits, and eligibility rules
          </p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm p-4 mb-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <label className="text-sm font-medium text-gray-700">Filter by Status:</label>
            <select
              value={filterActive === null ? "all" : filterActive ? "active" : "inactive"}
              onChange={(e) =>
                setFilterActive(
                  e.target.value === "all" ? null : e.target.value === "active"
                )
              }
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Products</option>
              <option value="active">Active Only</option>
              <option value="inactive">Inactive Only</option>
            </select>
          </div>
          <button
            onClick={() => (window.location.href = "/gold-lending/products/new")}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            + Create New Product
          </button>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Products Grid */}
        {products.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <div className="text-gray-400 mb-4">
              <svg
                className="mx-auto h-16 w-16"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
                />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Products Found</h3>
            <p className="text-gray-600 mb-6">
              Get started by creating your first gold loan product
            </p>
            <button
              onClick={() => (window.location.href = "/gold-lending/products/new")}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Create Product
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {products.map((product) => (
              <div
                key={product.id}
                className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow p-6 cursor-pointer border border-gray-200"
                onClick={() =>
                  (window.location.href = `/gold-lending/products/${product.id}`)
                }
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      {product.product_name}
                    </h3>
                    <p className="text-sm text-gray-500">{product.product_code}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    {product.is_active ? (
                      <span className="flex items-center justify-center w-3 h-3 bg-green-500 rounded-full"></span>
                    ) : (
                      <span className="flex items-center justify-center w-3 h-3 bg-gray-400 rounded-full"></span>
                    )}
                  </div>
                </div>

                {/* Type Badge */}
                <div className="mb-4">{getProductTypeBadge(product.product_type)}</div>

                {/* Key Metrics */}
                <div className="space-y-3">
                  {product.base_rate && (
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Interest Rate</span>
                      <span className="text-sm font-semibold text-gray-900">
                        {product.base_rate}% p.a.
                      </span>
                    </div>
                  )}
                  {product.ltv_percent && (
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Max LTV</span>
                      <span className="text-sm font-semibold text-gray-900">
                        {product.ltv_percent}%
                      </span>
                    </div>
                  )}
                  {product.min_amount && product.max_amount && (
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Loan Range</span>
                      <span className="text-sm font-semibold text-gray-900">
                        {formatCurrency(product.min_amount)} -{" "}
                        {formatCurrency(product.max_amount)}
                      </span>
                    </div>
                  )}
                </div>

                {/* Footer */}
                <div className="mt-4 pt-4 border-t border-gray-100">
                  <button className="text-sm text-blue-600 hover:text-blue-800 font-medium">
                    View Details →
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
