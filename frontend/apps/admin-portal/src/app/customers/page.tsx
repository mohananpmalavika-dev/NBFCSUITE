"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { 
  Users, 
  UserPlus, 
  Search, 
  Filter,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock,
  Ban
} from "lucide-react";

interface Customer {
  id: number;
  customer_code: string;
  full_name: string;
  mobile: string;
  email?: string;
  kyc_status: string;
  risk_rating: string;
  cibil_score?: number;
  is_active: boolean;
  created_at: string;
}

interface DashboardStats {
  total_customers: number;
  active_customers: number;
  kyc_pending: number;
  kyc_completed: number;
  high_risk_customers: number;
  blacklisted_customers: number;
  new_this_month: number;
  avg_cibil_score?: number;
}

export default function CustomersPage() {
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [kycFilter, setKycFilter] = useState<string>("");
  const [riskFilter, setRiskFilter] = useState<string>("");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);
  const pageSize = 20;

  useEffect(() => {
    fetchStats();
    fetchCustomers();
  }, [currentPage, kycFilter, riskFilter]);

  const fetchStats = async () => {
    try {
      const response = await fetch("/api/v1/customers/stats", {
        headers: { "Content-Type": "application/json" }
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error("Error fetching stats:", error);
    }
  };

  const fetchCustomers = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: currentPage.toString(),
        page_size: pageSize.toString(),
        ...(searchQuery && { search: searchQuery }),
        ...(kycFilter && { kyc_status: kycFilter }),
        ...(riskFilter && { risk_rating: riskFilter })
      });

      const response = await fetch(`/api/v1/customers?${params}`, {
        headers: { "Content-Type": "application/json" }
      });

      if (response.ok) {
        const data = await response.json();
        setCustomers(data.items || []);
        setTotalRecords(data.total || 0);
      }
    } catch (error) {
      console.error("Error fetching customers:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchCustomers();
  };

  const getKYCBadge = (status: string) => {
    const badges = {
      pending: "bg-yellow-100 text-yellow-800",
      in_progress: "bg-blue-100 text-blue-800",
      completed: "bg-green-100 text-green-800",
      rejected: "bg-red-100 text-red-800"
    };
    return badges[status as keyof typeof badges] || badges.pending;
  };

  const getRiskBadge = (rating: string) => {
    const badges = {
      low: "bg-green-100 text-green-800",
      medium: "bg-yellow-100 text-yellow-800",
      high: "bg-orange-100 text-orange-800",
      very_high: "bg-red-100 text-red-800"
    };
    return badges[rating as keyof typeof badges] || badges.medium;
  };

  const getCIBILColor = (score?: number) => {
    if (!score) return "text-gray-500";
    if (score >= 750) return "text-green-600 font-bold";
    if (score >= 650) return "text-yellow-600 font-semibold";
    return "text-red-600 font-bold";
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Customer Management</h1>
                <p className="text-sm text-gray-600">
                  Manage customer profiles, KYC, and documents
                </p>
              </div>
            </div>
            <button
              onClick={() => router.push("/customers/new")}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <UserPlus className="w-4 h-4" />
              Add Customer
            </button>
          </div>
        </div>
      </div>

      {/* Stats Bar */}
      {stats && (
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold">{stats.total_customers}</div>
                <div className="text-xs text-blue-100">Total</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{stats.active_customers}</div>
                <div className="text-xs text-blue-100">Active</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{stats.kyc_pending}</div>
                <div className="text-xs text-blue-100">KYC Pending</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{stats.kyc_completed}</div>
                <div className="text-xs text-blue-100">KYC Done</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{stats.high_risk_customers}</div>
                <div className="text-xs text-blue-100">High Risk</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{stats.blacklisted_customers}</div>
                <div className="text-xs text-blue-100">Blacklisted</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{stats.new_this_month}</div>
                <div className="text-xs text-blue-100">This Month</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{stats.avg_cibil_score || "N/A"}</div>
                <div className="text-xs text-blue-100">Avg CIBIL</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Search and Filters */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Search */}
            <form onSubmit={handleSearch} className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search by name, code, mobile, email, PAN..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </form>

            {/* KYC Filter */}
            <select
              value={kycFilter}
              onChange={(e) => {
                setKycFilter(e.target.value);
                setCurrentPage(1);
              }}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All KYC Status</option>
              <option value="pending">Pending</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="rejected">Rejected</option>
            </select>

            {/* Risk Filter */}
            <select
              value={riskFilter}
              onChange={(e) => {
                setRiskFilter(e.target.value);
                setCurrentPage(1);
              }}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Risk Levels</option>
              <option value="low">Low Risk</option>
              <option value="medium">Medium Risk</option>
              <option value="high">High Risk</option>
              <option value="very_high">Very High Risk</option>
            </select>
          </div>
        </div>
      </div>

      {/* Customer List */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : customers.length === 0 ? (
            <div className="text-center py-12">
              <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No customers found</h3>
              <p className="text-sm text-gray-600 mb-6">
                {searchQuery || kycFilter || riskFilter 
                  ? "Try adjusting your search or filters"
                  : "Get started by adding your first customer"}
              </p>
              <button
                onClick={() => router.push("/customers/new")}
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <UserPlus className="w-4 h-4" />
                Add First Customer
              </button>
            </div>
          ) : (
            <>
              {/* Table */}
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Customer
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Contact
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        KYC Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Risk
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        CIBIL
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Status
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {customers.map((customer) => (
                      <tr 
                        key={customer.id}
                        className="hover:bg-gray-50 cursor-pointer transition-colors"
                        onClick={() => router.push(`/customers/${customer.id}`)}
                      >
                        <td className="px-6 py-4">
                          <div>
                            <div className="font-medium text-gray-900">{customer.full_name}</div>
                            <div className="text-xs text-gray-500 font-mono">{customer.customer_code}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div>
                            <div className="text-sm text-gray-900">{customer.mobile}</div>
                            {customer.email && (
                              <div className="text-xs text-gray-500">{customer.email}</div>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getKYCBadge(customer.kyc_status)}`}>
                            {customer.kyc_status.replace('_', ' ').toUpperCase()}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getRiskBadge(customer.risk_rating)}`}>
                            {customer.risk_rating.replace('_', ' ').toUpperCase()}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`text-sm ${getCIBILColor(customer.cibil_score)}`}>
                            {customer.cibil_score || "N/A"}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          {customer.is_active ? (
                            <span className="flex items-center gap-1 text-xs text-green-700">
                              <CheckCircle className="w-3 h-3" />
                              Active
                            </span>
                          ) : (
                            <span className="flex items-center gap-1 text-xs text-red-700">
                              <Ban className="w-3 h-3" />
                              Inactive
                            </span>
                          )}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              router.push(`/customers/${customer.id}`);
                            }}
                            className="text-blue-600 hover:text-blue-900 text-sm font-medium"
                          >
                            View →
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <div className="px-6 py-4 border-t flex items-center justify-between">
                <div className="text-sm text-gray-700">
                  Showing <span className="font-medium">{(currentPage - 1) * pageSize + 1}</span> to{" "}
                  <span className="font-medium">
                    {Math.min(currentPage * pageSize, totalRecords)}
                  </span> of{" "}
                  <span className="font-medium">{totalRecords}</span> customers
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                    className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setCurrentPage(p => p + 1)}
                    disabled={currentPage * pageSize >= totalRecords}
                    className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
                  >
                    Next
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
