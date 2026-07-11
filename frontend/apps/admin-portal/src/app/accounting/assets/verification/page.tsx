"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { 
  ClipboardCheck,
  Plus,
  CheckCircle,
  XCircle,
  AlertCircle,
  MapPin,
  Calendar,
  TrendingUp,
  Play,
  Download
} from "lucide-react";

interface VerificationCycle {
  id: number;
  cycle_number: string;
  cycle_name: string;
  financial_year: number;
  planned_start_date: string;
  planned_end_date: string;
  actual_start_date: string | null;
  actual_end_date: string | null;
  status: string;
  total_assets: number;
  verified_assets: number;
  pending_assets: number;
  found_assets: number;
  not_found_assets: number;
  discrepancy_count: number;
  completion_percentage: number;
}

export default function VerificationPage() {
  const [cycles, setCycles] = useState<VerificationCycle[]>([]);
  const [loading, setLoading] = useState(true);
  const [showNewCycleForm, setShowNewCycleForm] = useState(false);

  useEffect(() => {
    fetchVerificationCycles();
  }, []);

  const fetchVerificationCycles = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/fixed-assets/verification/cycles');
      if (response.ok) {
        const data = await response.json();
        setCycles(data.items || []);
      }
    } catch (error) {
      console.error("Error fetching verification cycles:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleStartCycle = async (cycleId: number) => {
    if (!confirm("Are you sure you want to start this verification cycle?")) return;

    try {
      const response = await fetch(`/api/v1/fixed-assets/verification/cycles/${cycleId}/start`, {
        method: 'POST',
      });

      if (response.ok) {
        fetchVerificationCycles();
      }
    } catch (error) {
      console.error("Error starting cycle:", error);
    }
  };

  const handleCompleteCycle = async (cycleId: number) => {
    if (!confirm("Are you sure you want to complete this verification cycle?")) return;

    try {
      const response = await fetch(`/api/v1/fixed-assets/verification/cycles/${cycleId}/complete`, {
        method: 'POST',
      });

      if (response.ok) {
        fetchVerificationCycles();
      }
    } catch (error) {
      console.error("Error completing cycle:", error);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { color: string; label: string }> = {
      planned: { color: "bg-blue-100 text-blue-800", label: "Planned" },
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

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Physical Verification</h2>
            <p className="mt-1 text-sm text-gray-500">
              Conduct periodic physical verification of fixed assets
            </p>
          </div>
          <button
            onClick={() => setShowNewCycleForm(true)}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus className="h-5 w-5 mr-2" />
            Create Verification Cycle
          </button>
        </div>
      </div>

      {/* Overall Stats */}
      {cycles.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Cycles</p>
                <p className="mt-1 text-2xl font-bold text-gray-900">
                  {cycles.length}
                </p>
              </div>
              <ClipboardCheck className="h-8 w-8 text-gray-400" />
            </div>
          </div>

          <div className="bg-purple-50 rounded-lg border border-purple-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-purple-700">In Progress</p>
                <p className="mt-1 text-2xl font-bold text-purple-600">
                  {cycles.filter(c => c.status === 'in_progress').length}
                </p>
              </div>
              <Play className="h-8 w-8 text-purple-400" />
            </div>
          </div>

          <div className="bg-green-50 rounded-lg border border-green-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-green-700">Completed</p>
                <p className="mt-1 text-2xl font-bold text-green-600">
                  {cycles.filter(c => c.status === 'completed').length}
                </p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-400" />
            </div>
          </div>

          <div className="bg-blue-50 rounded-lg border border-blue-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-blue-700">This Year</p>
                <p className="mt-1 text-2xl font-bold text-blue-600">
                  {cycles.filter(c => c.financial_year === new Date().getFullYear()).length}
                </p>
              </div>
              <Calendar className="h-8 w-8 text-blue-400" />
            </div>
          </div>
        </div>
      )}

      {/* Verification Cycles */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-gray-500">Loading verification cycles...</div>
          </div>
        ) : cycles.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64">
            <ClipboardCheck className="h-12 w-12 text-gray-400 mb-4" />
            <p className="text-gray-500 mb-2">No verification cycles found</p>
            <button
              onClick={() => setShowNewCycleForm(true)}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              Create your first verification cycle
            </button>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {cycles.map((cycle) => (
              <div key={cycle.id} className="p-6 hover:bg-gray-50">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center">
                      <Link
                        href={`/accounting/assets/verification/${cycle.id}`}
                        className="text-lg font-semibold text-blue-600 hover:text-blue-700"
                      >
                        {cycle.cycle_name}
                      </Link>
                      <span className="ml-3">{getStatusBadge(cycle.status)}</span>
                    </div>
                    
                    <div className="mt-2 flex items-center space-x-4 text-sm text-gray-600">
                      <div className="flex items-center">
                        <Calendar className="h-4 w-4 mr-1" />
                        FY {cycle.financial_year}
                      </div>
                      <div className="flex items-center">
                        <span className="font-medium">{cycle.cycle_number}</span>
                      </div>
                      <div className="flex items-center">
                        {new Date(cycle.planned_start_date).toLocaleDateString("en-IN", {
                          month: "short",
                          day: "numeric",
                        })} - {new Date(cycle.planned_end_date).toLocaleDateString("en-IN", {
                          month: "short",
                          day: "numeric",
                          year: "numeric",
                        })}
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="mt-4">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-medium text-gray-700">
                          Progress: {cycle.completion_percentage.toFixed(1)}%
                        </span>
                        <span className="text-xs text-gray-600">
                          {cycle.verified_assets} of {cycle.total_assets} assets
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all"
                          style={{ width: `${cycle.completion_percentage}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* Stats Grid */}
                    <div className="mt-4 grid grid-cols-4 gap-4">
                      <div className="bg-gray-50 rounded-lg p-3">
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-gray-600">Found</span>
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        </div>
                        <p className="mt-1 text-lg font-bold text-gray-900">{cycle.found_assets}</p>
                      </div>

                      <div className="bg-gray-50 rounded-lg p-3">
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-gray-600">Not Found</span>
                          <XCircle className="h-4 w-4 text-red-500" />
                        </div>
                        <p className="mt-1 text-lg font-bold text-gray-900">{cycle.not_found_assets}</p>
                      </div>

                      <div className="bg-gray-50 rounded-lg p-3">
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-gray-600">Discrepancies</span>
                          <AlertCircle className="h-4 w-4 text-orange-500" />
                        </div>
                        <p className="mt-1 text-lg font-bold text-gray-900">{cycle.discrepancy_count}</p>
                      </div>

                      <div className="bg-gray-50 rounded-lg p-3">
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-gray-600">Pending</span>
                          <TrendingUp className="h-4 w-4 text-blue-500" />
                        </div>
                        <p className="mt-1 text-lg font-bold text-gray-900">{cycle.pending_assets}</p>
                      </div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="ml-6 flex flex-col space-y-2">
                    {cycle.status === 'planned' && (
                      <button
                        onClick={() => handleStartCycle(cycle.id)}
                        className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
                      >
                        <Play className="h-4 w-4 mr-2" />
                        Start Cycle
                      </button>
                    )}
                    
                    {cycle.status === 'in_progress' && (
                      <>
                        <Link
                          href={`/accounting/assets/verification/${cycle.id}/verify`}
                          className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm font-medium"
                        >
                          <ClipboardCheck className="h-4 w-4 mr-2" />
                          Verify Assets
                        </Link>
                        <button
                          onClick={() => handleCompleteCycle(cycle.id)}
                          className="flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm font-medium"
                        >
                          <CheckCircle className="h-4 w-4 mr-2" />
                          Complete
                        </button>
                      </>
                    )}
                    
                    <Link
                      href={`/accounting/assets/verification/${cycle.id}`}
                      className="flex items-center px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 text-sm font-medium"
                    >
                      View Details
                    </Link>
                    
                    {cycle.status === 'completed' && (
                      <button
                        className="flex items-center px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 text-sm font-medium"
                      >
                        <Download className="h-4 w-4 mr-2" />
                        Report
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Verification Guidelines */}
      <div className="mt-6 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Verification Guidelines
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-3">Best Practices</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-start">
                <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5" />
                <span>Plan verification cycles at least quarterly</span>
              </li>
              <li className="flex items-start">
                <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5" />
                <span>Assign specific team members to locations</span>
              </li>
              <li className="flex items-start">
                <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5" />
                <span>Use mobile app for on-site verification</span>
              </li>
              <li className="flex items-start">
                <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5" />
                <span>Take photos and capture GPS location</span>
              </li>
              <li className="flex items-start">
                <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5" />
                <span>Report discrepancies immediately</span>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-3">What to Check</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-start">
                <MapPin className="h-4 w-4 text-blue-500 mr-2 mt-0.5" />
                <span>Physical location matches records</span>
              </li>
              <li className="flex items-start">
                <MapPin className="h-4 w-4 text-blue-500 mr-2 mt-0.5" />
                <span>Asset is in expected condition</span>
              </li>
              <li className="flex items-start">
                <MapPin className="h-4 w-4 text-blue-500 mr-2 mt-0.5" />
                <span>Custodian is correctly assigned</span>
              </li>
              <li className="flex items-start">
                <MapPin className="h-4 w-4 text-blue-500 mr-2 mt-0.5" />
                <span>Asset is functional and in use</span>
              </li>
              <li className="flex items-start">
                <MapPin className="h-4 w-4 text-blue-500 mr-2 mt-0.5" />
                <span>Barcode/QR tags are intact</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
