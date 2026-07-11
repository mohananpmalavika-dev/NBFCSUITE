"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { 
  Search,
  Filter,
  Plus,
  Edit,
  Trash2,
  Eye,
  Download,
  ChevronLeft,
  ChevronRight,
  Package,
  MapPin,
  User,
  Calendar,
  TrendingDown,
  MoreVertical
} from "lucide-react";

interface Asset {
  id: number;
  asset_code: string;
  asset_name: string;
  asset_category: string;
  asset_status: string;
  purchase_cost: number;
  total_cost: number;
  accumulated_depreciation: number;
  net_book_value: number;
  location_name: string;
  custodian_name: string;
  acquisition_date: string;
  depreciation_method: string;
  last_verification_date: string;
}

export default function AssetListPage() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [pageSize] = useState(20);
  
  // Filters
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [locationFilter, setLocationFilter] = useState("");
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    fetchAssets();
  }, [page, searchQuery, categoryFilter, statusFilter, locationFilter]);

  const fetchAssets = async () => {
    try {
      setLoading(true);
      
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
        ...(searchQuery && { search_query: searchQuery }),
        ...(categoryFilter && { category: categoryFilter }),
        ...(statusFilter && { status: statusFilter }),
        ...(locationFilter && { location_id: locationFilter }),
      });

      const response = await fetch(`/api/v1/fixed-assets/assets?${params}`);
      
      if (response.ok) {
        const data = await response.json();
        setAssets(data.items || []);
        setTotalPages(data.total_pages || 1);
      }
    } catch (error) {
      console.error("Error fetching assets:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (assetId: number) => {
    if (!confirm("Are you sure you want to delete this asset?")) return;

    try {
      const response = await fetch(`/api/v1/fixed-assets/assets/${assetId}`, {
        method: "DELETE",
      });

      if (response.ok) {
        fetchAssets();
      }
    } catch (error) {
      console.error("Error deleting asset:", error);
    }
  };

  const formatCurrency = (value: number) => {
    return `₹${value.toLocaleString("en-IN", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  };

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { color: string; label: string }> = {
      active: { color: "bg-green-100 text-green-800", label: "Active" },
      in_maintenance: { color: "bg-orange-100 text-orange-800", label: "In Maintenance" },
      under_repair: { color: "bg-red-100 text-red-800", label: "Under Repair" },
      idle: { color: "bg-gray-100 text-gray-800", label: "Idle" },
      disposed: { color: "bg-purple-100 text-purple-800", label: "Disposed" },
      transferred: { color: "bg-blue-100 text-blue-800", label: "Transferred" },
    };

    const statusInfo = statusMap[status] || { color: "bg-gray-100 text-gray-800", label: status };

    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusInfo.color}`}>
        {statusInfo.label}
      </span>
    );
  };

  const getCategoryLabel = (category: string) => {
    return category.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Asset Register</h2>
            <p className="mt-1 text-sm text-gray-500">
              Complete list of all fixed assets
            </p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={() => {/* Export functionality */}}
              className="flex items-center px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              <Download className="h-5 w-5 mr-2" />
              Export
            </button>
            <Link
              href="/accounting/assets/new"
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Plus className="h-5 w-5 mr-2" />
              Add Asset
            </Link>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="mb-6 bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex items-center space-x-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by asset code, name, serial number, barcode..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Filter Toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`flex items-center px-4 py-2 border rounded-lg ${
              showFilters ? "bg-blue-50 border-blue-300 text-blue-700" : "border-gray-300 text-gray-700 hover:bg-gray-50"
            }`}
          >
            <Filter className="h-5 w-5 mr-2" />
            Filters
          </button>
        </div>

        {/* Expanded Filters */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Category Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category
                </label>
                <select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Categories</option>
                  <option value="land">Land</option>
                  <option value="building">Building</option>
                  <option value="plant_machinery">Plant & Machinery</option>
                  <option value="furniture_fixtures">Furniture & Fixtures</option>
                  <option value="vehicles">Vehicles</option>
                  <option value="computer_equipment">Computer Equipment</option>
                  <option value="office_equipment">Office Equipment</option>
                  <option value="leasehold_improvements">Leasehold Improvements</option>
                  <option value="intangible_assets">Intangible Assets</option>
                  <option value="other">Other</option>
                </select>
              </div>

              {/* Status Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status
                </label>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Status</option>
                  <option value="active">Active</option>
                  <option value="in_maintenance">In Maintenance</option>
                  <option value="under_repair">Under Repair</option>
                  <option value="idle">Idle</option>
                  <option value="disposed">Disposed</option>
                  <option value="transferred">Transferred</option>
                </select>
              </div>

              {/* Location Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Location
                </label>
                <select
                  value={locationFilter}
                  onChange={(e) => setLocationFilter(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Locations</option>
                  {/* Populate from API */}
                </select>
              </div>
            </div>

            <div className="mt-4 flex items-center justify-between">
              <button
                onClick={() => {
                  setCategoryFilter("");
                  setStatusFilter("");
                  setLocationFilter("");
                  setSearchQuery("");
                }}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                Clear All Filters
              </button>
              <div className="text-sm text-gray-500">
                Showing {assets.length} of {totalPages * pageSize} assets
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Assets Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-gray-500">Loading assets...</div>
          </div>
        ) : assets.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64">
            <Package className="h-12 w-12 text-gray-400 mb-4" />
            <p className="text-gray-500 mb-2">No assets found</p>
            <Link
              href="/accounting/assets/new"
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              Add your first asset
            </Link>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Asset Code
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Asset Details
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Category
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Purchase Cost
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Net Book Value
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Location
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {assets.map((asset) => (
                    <tr key={asset.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Link
                          href={`/accounting/assets/${asset.id}`}
                          className="text-sm font-medium text-blue-600 hover:text-blue-700"
                        >
                          {asset.asset_code}
                        </Link>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm">
                          <div className="font-medium text-gray-900">{asset.asset_name}</div>
                          <div className="text-gray-500 flex items-center mt-1">
                            <Calendar className="h-3 w-3 mr-1" />
                            {new Date(asset.acquisition_date).toLocaleDateString("en-IN", {
                              year: "numeric",
                              month: "short",
                              day: "numeric",
                            })}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-900">
                          {getCategoryLabel(asset.asset_category)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(asset.asset_status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <span className="text-sm font-medium text-gray-900">
                          {formatCurrency(asset.purchase_cost)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <div className="text-sm">
                          <div className="font-medium text-gray-900">
                            {formatCurrency(asset.net_book_value)}
                          </div>
                          <div className="text-xs text-gray-500 flex items-center justify-end">
                            <TrendingDown className="h-3 w-3 mr-1" />
                            {formatCurrency(asset.accumulated_depreciation)}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm">
                          {asset.location_name && (
                            <div className="flex items-center text-gray-900">
                              <MapPin className="h-3 w-3 mr-1" />
                              {asset.location_name}
                            </div>
                          )}
                          {asset.custodian_name && (
                            <div className="flex items-center text-gray-500 mt-1">
                              <User className="h-3 w-3 mr-1" />
                              {asset.custodian_name}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center justify-end space-x-2">
                          <Link
                            href={`/accounting/assets/${asset.id}`}
                            className="text-blue-600 hover:text-blue-700"
                            title="View Details"
                          >
                            <Eye className="h-4 w-4" />
                          </Link>
                          <Link
                            href={`/accounting/assets/${asset.id}/edit`}
                            className="text-green-600 hover:text-green-700"
                            title="Edit"
                          >
                            <Edit className="h-4 w-4" />
                          </Link>
                          <button
                            onClick={() => handleDelete(asset.id)}
                            className="text-red-600 hover:text-red-700"
                            title="Delete"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
              <div className="text-sm text-gray-500">
                Page {page} of {totalPages}
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setPage(page - 1)}
                  disabled={page === 1}
                  className="px-3 py-1 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="h-4 w-4" />
                </button>
                <button
                  onClick={() => setPage(page + 1)}
                  disabled={page === totalPages}
                  className="px-3 py-1 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
