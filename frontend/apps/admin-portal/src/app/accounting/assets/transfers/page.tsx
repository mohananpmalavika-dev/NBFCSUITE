"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { 
  ArrowRightLeft,
  Plus,
  MapPin,
  User,
  CheckCircle,
  Clock,
  XCircle,
  Truck,
  Search,
  Filter
} from "lucide-react";

interface Transfer {
  id: number;
  transfer_number: string;
  asset_id: number;
  asset_code: string;
  asset_name: string;
  transfer_date: string;
  from_location_name: string;
  to_location_name: string;
  from_custodian_name: string;
  to_custodian_name: string;
  status: string;
  transfer_type: string;
  reason: string;
}

export default function TransfersPage() {
  const [transfers, setTransfers] = useState<Transfer[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    fetchTransfers();
  }, [statusFilter]);

  const fetchTransfers = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        ...(statusFilter && { status: statusFilter }),
      });

      const response = await fetch(`/api/v1/fixed-assets/transfers?${params}`);
      if (response.ok) {
        const data = await response.json();
        setTransfers(data.items || []);
      }
    } catch (error) {
      console.error("Error fetching transfers:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (transferId: number) => {
    if (!confirm("Are you sure you want to approve this transfer?")) return;

    try {
      const response = await fetch(`/api/v1/fixed-assets/transfers/${transferId}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approve: true }),
      });

      if (response.ok) {
        fetchTransfers();
      }
    } catch (error) {
      console.error("Error approving transfer:", error);
    }
  };

  const handleReject = async (transferId: number) => {
    const reason = prompt("Enter reason for rejection:");
    if (!reason) return;

    try {
      const response = await fetch(`/api/v1/fixed-assets/transfers/${transferId}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approve: false, notes: reason }),
      });

      if (response.ok) {
        fetchTransfers();
      }
    } catch (error) {
      console.error("Error rejecting transfer:", error);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { color: string; label: string; icon: any }> = {
      initiated: { color: "bg-blue-100 text-blue-800", label: "Initiated", icon: Clock },
      approved: { color: "bg-green-100 text-green-800", label: "Approved", icon: CheckCircle },
      in_transit: { color: "bg-yellow-100 text-yellow-800", label: "In Transit", icon: Truck },
      completed: { color: "bg-emerald-100 text-emerald-800", label: "Completed", icon: CheckCircle },
      rejected: { color: "bg-red-100 text-red-800", label: "Rejected", icon: XCircle },
      cancelled: { color: "bg-gray-100 text-gray-800", label: "Cancelled", icon: XCircle },
    };

    const statusInfo = statusMap[status] || { 
      color: "bg-gray-100 text-gray-800", 
      label: status,
      icon: Clock 
    };
    const Icon = statusInfo.icon;

    return (
      <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${statusInfo.color}`}>
        <Icon className="h-3 w-3 mr-1" />
        {statusInfo.label}
      </span>
    );
  };

  const filteredTransfers = transfers.filter(transfer => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      transfer.transfer_number.toLowerCase().includes(query) ||
      transfer.asset_code.toLowerCase().includes(query) ||
      transfer.asset_name.toLowerCase().includes(query)
    );
  });

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Asset Transfers</h2>
            <p className="mt-1 text-sm text-gray-500">
              Track and manage asset movements between locations
            </p>
          </div>
          <Link
            href="/accounting/assets/transfers/new"
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus className="h-5 w-5 mr-2" />
            Initiate Transfer
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-600">Total</p>
              <p className="mt-1 text-xl font-bold text-gray-900">
                {transfers.length}
              </p>
            </div>
            <ArrowRightLeft className="h-6 w-6 text-gray-400" />
          </div>
        </div>

        <div className="bg-blue-50 rounded-lg border border-blue-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-blue-700">Pending</p>
              <p className="mt-1 text-xl font-bold text-blue-600">
                {transfers.filter(t => t.status === 'initiated').length}
              </p>
            </div>
            <Clock className="h-6 w-6 text-blue-400" />
          </div>
        </div>

        <div className="bg-green-50 rounded-lg border border-green-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-green-700">Approved</p>
              <p className="mt-1 text-xl font-bold text-green-600">
                {transfers.filter(t => t.status === 'approved').length}
              </p>
            </div>
            <CheckCircle className="h-6 w-6 text-green-400" />
          </div>
        </div>

        <div className="bg-yellow-50 rounded-lg border border-yellow-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-yellow-700">In Transit</p>
              <p className="mt-1 text-xl font-bold text-yellow-600">
                {transfers.filter(t => t.status === 'in_transit').length}
              </p>
            </div>
            <Truck className="h-6 w-6 text-yellow-400" />
          </div>
        </div>

        <div className="bg-emerald-50 rounded-lg border border-emerald-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-emerald-700">Completed</p>
              <p className="mt-1 text-xl font-bold text-emerald-600">
                {transfers.filter(t => t.status === 'completed').length}
              </p>
            </div>
            <CheckCircle className="h-6 w-6 text-emerald-400" />
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-6 bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex items-center space-x-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by transfer number, asset code, or name..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Status</option>
            <option value="initiated">Initiated</option>
            <option value="approved">Approved</option>
            <option value="in_transit">In Transit</option>
            <option value="completed">Completed</option>
            <option value="rejected">Rejected</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </div>

      {/* Transfers Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-gray-500">Loading transfers...</div>
          </div>
        ) : filteredTransfers.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64">
            <ArrowRightLeft className="h-12 w-12 text-gray-400 mb-4" />
            <p className="text-gray-500 mb-2">No transfers found</p>
            <Link
              href="/accounting/assets/transfers/new"
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              Initiate your first transfer
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Transfer #
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Asset
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    From
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    To
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Date
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
                {filteredTransfers.map((transfer) => (
                  <tr key={transfer.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Link
                        href={`/accounting/assets/transfers/${transfer.id}`}
                        className="text-sm font-medium text-blue-600 hover:text-blue-700"
                      >
                        {transfer.transfer_number}
                      </Link>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm">
                        <div className="font-medium text-gray-900">{transfer.asset_name}</div>
                        <div className="text-gray-500">{transfer.asset_code}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm">
                        <div className="flex items-center text-gray-900">
                          <MapPin className="h-3 w-3 mr-1" />
                          {transfer.from_location_name}
                        </div>
                        {transfer.from_custodian_name && (
                          <div className="flex items-center text-gray-500 mt-1">
                            <User className="h-3 w-3 mr-1" />
                            {transfer.from_custodian_name}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm">
                        <div className="flex items-center text-gray-900">
                          <MapPin className="h-3 w-3 mr-1" />
                          {transfer.to_location_name}
                        </div>
                        {transfer.to_custodian_name && (
                          <div className="flex items-center text-gray-500 mt-1">
                            <User className="h-3 w-3 mr-1" />
                            {transfer.to_custodian_name}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-900">
                        {new Date(transfer.transfer_date).toLocaleDateString("en-IN", {
                          year: "numeric",
                          month: "short",
                          day: "numeric",
                        })}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(transfer.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      {transfer.status === 'initiated' && (
                        <div className="flex items-center justify-end space-x-2">
                          <button
                            onClick={() => handleApprove(transfer.id)}
                            className="text-sm text-green-600 hover:text-green-700 font-medium"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => handleReject(transfer.id)}
                            className="text-sm text-red-600 hover:text-red-700 font-medium"
                          >
                            Reject
                          </button>
                        </div>
                      )}
                      {transfer.status === 'approved' && (
                        <Link
                          href={`/accounting/assets/transfers/${transfer.id}/mark-transit`}
                          className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                        >
                          Mark In Transit
                        </Link>
                      )}
                      {transfer.status === 'in_transit' && (
                        <Link
                          href={`/accounting/assets/transfers/${transfer.id}/complete`}
                          className="text-sm text-green-600 hover:text-green-700 font-medium"
                        >
                          Complete
                        </Link>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Transfer Flow Diagram */}
      <div className="mt-6 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Transfer Workflow</h3>
        <div className="flex items-center justify-between">
          <div className="flex flex-col items-center">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
              <Clock className="h-6 w-6 text-blue-600" />
            </div>
            <p className="mt-2 text-xs font-medium text-gray-900">Initiated</p>
            <p className="text-xs text-gray-500">Create transfer request</p>
          </div>
          
          <div className="flex-1 h-0.5 bg-gray-300 mx-4"></div>
          
          <div className="flex flex-col items-center">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
            <p className="mt-2 text-xs font-medium text-gray-900">Approved</p>
            <p className="text-xs text-gray-500">Manager approval</p>
          </div>
          
          <div className="flex-1 h-0.5 bg-gray-300 mx-4"></div>
          
          <div className="flex flex-col items-center">
            <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center">
              <Truck className="h-6 w-6 text-yellow-600" />
            </div>
            <p className="mt-2 text-xs font-medium text-gray-900">In Transit</p>
            <p className="text-xs text-gray-500">Asset in movement</p>
          </div>
          
          <div className="flex-1 h-0.5 bg-gray-300 mx-4"></div>
          
          <div className="flex flex-col items-center">
            <div className="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center">
              <CheckCircle className="h-6 w-6 text-emerald-600" />
            </div>
            <p className="mt-2 text-xs font-medium text-gray-900">Completed</p>
            <p className="text-xs text-gray-500">Asset received</p>
          </div>
        </div>
      </div>
    </div>
  );
}
