"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { 
  Wrench,
  Plus,
  Calendar,
  Clock,
  DollarSign,
  CheckCircle,
  AlertCircle,
  Filter,
  Search
} from "lucide-react";

interface MaintenanceRecord {
  id: number;
  maintenance_number: string;
  asset_id: number;
  asset_code: string;
  asset_name: string;
  maintenance_type: string;
  status: string;
  scheduled_date: string;
  actual_start_date: string | null;
  actual_end_date: string | null;
  priority: string;
  total_cost: number;
  downtime_hours: number | null;
  problem_description: string;
}

export default function MaintenancePage() {
  const [maintenanceRecords, setMaintenanceRecords] = useState<MaintenanceRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [showNewForm, setShowNewForm] = useState(false);

  useEffect(() => {
    fetchMaintenanceRecords();
  }, [statusFilter, typeFilter]);

  const fetchMaintenanceRecords = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        ...(statusFilter && { status: statusFilter }),
        ...(typeFilter && { maintenance_type: typeFilter }),
      });

      const response = await fetch(`/api/v1/fixed-assets/maintenance?${params}`);
      if (response.ok) {
        const data = await response.json();
        setMaintenanceRecords(data.items || []);
      }
    } catch (error) {
      console.error("Error fetching maintenance records:", error);
    } finally {
      setLoading(false);
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
      pending: { color: "bg-yellow-100 text-yellow-800", label: "Pending" },
      scheduled: { color: "bg-blue-100 text-blue-800", label: "Scheduled" },
      in_progress: { color: "bg-purple-100 text-purple-800", label: "In Progress" },
      completed: { color: "bg-green-100 text-green-800", label: "Completed" },
      cancelled: { color: "bg-gray-100 text-gray-800", label: "Cancelled" },
    };

    const statusInfo = statusMap[status] || { color: "bg-gray-100 text-gray-800", label: status };

    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusInfo.color}`}>
        {statusInfo.label}
      </span>
    );
  };

  const getPriorityBadge = (priority: string) => {
    const priorityMap: Record<string, { color: string; icon: any }> = {
      low: { color: "text-gray-500", icon: Clock },
      medium: { color: "text-blue-500", icon: Clock },
      high: { color: "text-orange-500", icon: AlertCircle },
      critical: { color: "text-red-500", icon: AlertCircle },
    };

    const priorityInfo = priorityMap[priority] || { color: "text-gray-500", icon: Clock };
    const Icon = priorityInfo.icon;

    return (
      <div className="flex items-center">
        <Icon className={`h-4 w-4 ${priorityInfo.color}`} />
        <span className={`ml-1 text-xs font-medium capitalize ${priorityInfo.color}`}>
          {priority}
        </span>
      </div>
    );
  };

  const getTypeLabel = (type: string) => {
    return type.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
  };

  const filteredRecords = maintenanceRecords.filter(record => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      record.maintenance_number.toLowerCase().includes(query) ||
      record.asset_code.toLowerCase().includes(query) ||
      record.asset_name.toLowerCase().includes(query)
    );
  });

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Asset Maintenance</h2>
            <p className="mt-1 text-sm text-gray-500">
              Track and manage asset maintenance, repairs, and servicing
            </p>
          </div>
          <button
            onClick={() => setShowNewForm(true)}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus className="h-5 w-5 mr-2" />
            Schedule Maintenance
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Requests</p>
              <p className="mt-1 text-2xl font-bold text-gray-900">
                {maintenanceRecords.length}
              </p>
            </div>
            <Wrench className="h-8 w-8 text-gray-400" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Scheduled</p>
              <p className="mt-1 text-2xl font-bold text-blue-600">
                {maintenanceRecords.filter(r => r.status === 'scheduled').length}
              </p>
            </div>
            <Calendar className="h-8 w-8 text-blue-400" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">In Progress</p>
              <p className="mt-1 text-2xl font-bold text-purple-600">
                {maintenanceRecords.filter(r => r.status === 'in_progress').length}
              </p>
            </div>
            <Clock className="h-8 w-8 text-purple-400" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Cost</p>
              <p className="mt-1 text-lg font-bold text-green-600">
                {formatCurrency(maintenanceRecords.reduce((sum, r) => sum + r.total_cost, 0))}
              </p>
            </div>
            <DollarSign className="h-8 w-8 text-green-400" />
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-6 bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="md:col-span-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by maintenance number, asset code, or name..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Status Filter */}
          <div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="scheduled">Scheduled</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>

          {/* Type Filter */}
          <div>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Types</option>
              <option value="preventive">Preventive</option>
              <option value="corrective">Corrective</option>
              <option value="breakdown">Breakdown</option>
              <option value="scheduled">Scheduled</option>
              <option value="inspection">Inspection</option>
            </select>
          </div>
        </div>
      </div>

      {/* Maintenance Records Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-gray-500">Loading maintenance records...</div>
          </div>
        ) : filteredRecords.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64">
            <Wrench className="h-12 w-12 text-gray-400 mb-4" />
            <p className="text-gray-500 mb-2">No maintenance records found</p>
            <button
              onClick={() => setShowNewForm(true)}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              Schedule your first maintenance
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Maintenance #
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Asset Details
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Priority
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Scheduled Date
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                    Cost
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                    Downtime
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredRecords.map((record) => (
                  <tr key={record.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Link
                        href={`/accounting/assets/maintenance/${record.id}`}
                        className="text-sm font-medium text-blue-600 hover:text-blue-700"
                      >
                        {record.maintenance_number}
                      </Link>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm">
                        <div className="font-medium text-gray-900">{record.asset_name}</div>
                        <div className="text-gray-500">{record.asset_code}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-900">
                        {getTypeLabel(record.maintenance_type)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(record.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getPriorityBadge(record.priority)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {new Date(record.scheduled_date).toLocaleDateString("en-IN", {
                          year: "numeric",
                          month: "short",
                          day: "numeric",
                        })}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <span className="text-sm font-medium text-gray-900">
                        {formatCurrency(record.total_cost)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      {record.downtime_hours ? (
                        <span className="text-sm text-gray-900">
                          {record.downtime_hours}h
                        </span>
                      ) : (
                        <span className="text-sm text-gray-400">-</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Upcoming Maintenance */}
      <div className="mt-6 bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Upcoming This Week</h3>
        </div>
        <div className="p-6">
          <div className="space-y-3">
            {maintenanceRecords
              .filter(r => r.status === 'scheduled' || r.status === 'pending')
              .slice(0, 5)
              .map((record) => (
                <div key={record.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center flex-1">
                    <Calendar className="h-5 w-5 text-blue-500 mr-3" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{record.asset_name}</p>
                      <p className="text-xs text-gray-500">{record.asset_code}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-900">
                      {new Date(record.scheduled_date).toLocaleDateString("en-IN", {
                        month: "short",
                        day: "numeric",
                      })}
                    </p>
                    <p className="text-xs text-gray-500">{getTypeLabel(record.maintenance_type)}</p>
                  </div>
                </div>
              ))}
          </div>
        </div>
      </div>
    </div>
  );
}
