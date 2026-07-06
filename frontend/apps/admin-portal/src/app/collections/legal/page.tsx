"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Plus, FileText, Scale, Building2, AlertTriangle } from "lucide-react";
import { legalApi } from "@/lib/api/collection";
import { LegalNotice, LegalCase } from "@/types/collection";
import { StatusBadge, CollectionStatCard } from "@/components/collections";

export default function LegalRecoveryPage() {
  const [activeTab, setActiveTab] = useState<"notices" | "cases" | "agencies">("notices");
  const [notices, setNotices] = useState<LegalNotice[]>([]);
  const [cases, setCases] = useState<LegalCase[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    try {
      setLoading(true);
      if (activeTab === "notices") {
        const response = await legalApi.listNotices({ limit: 50 });
        setNotices(response.items);
      } else if (activeTab === "cases") {
        const response = await legalApi.listCases({ limit: 50 });
        setCases(response.items);
      }
    } catch (error) {
      console.error("Error fetching legal data:", error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric"
    });
  };

  const activeCases = cases.filter(c => ["filed", "pending", "hearing"].includes(c.case_status));
  const totalClaimAmount = cases.reduce((sum, c) => sum + c.claim_amount, 0);

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-gray-900">Legal & Recovery</h2>
            <p className="mt-1 text-sm text-gray-500">
              Manage legal notices, court cases, and recovery operations
            </p>
          </div>
          <div className="flex gap-3">
            <Link
              href="/collections/legal/agencies"
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <Building2 className="h-4 w-4 mr-2" />
              Recovery Agencies
            </Link>
            <Link
              href={`/collections/legal/${activeTab}/new`}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-orange-600 hover:bg-orange-700"
            >
              <Plus className="h-4 w-4 mr-2" />
              {activeTab === "notices" ? "New Notice" : "File Case"}
            </Link>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <CollectionStatCard
          title="Total Notices"
          value={notices.length}
          icon={FileText}
          color="bg-blue-600"
        />
        <CollectionStatCard
          title="Active Cases"
          value={activeCases.length}
          icon={Scale}
          color="bg-purple-600"
        />
        <CollectionStatCard
          title="Total Claim Amount"
          value={formatCurrency(totalClaimAmount)}
          icon={AlertTriangle}
          color="bg-red-600"
        />
        <CollectionStatCard
          title="Recovery Agencies"
          value="12"
          icon={Building2}
          color="bg-green-600"
        />
      </div>

      {/* Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab("notices")}
              className={`${
                activeTab === "notices"
                  ? "border-orange-500 text-orange-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Legal Notices
            </button>
            <button
              onClick={() => setActiveTab("cases")}
              className={`${
                activeTab === "cases"
                  ? "border-orange-500 text-orange-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Court Cases
            </button>
            <button
              onClick={() => setActiveTab("agencies")}
              className={`${
                activeTab === "agencies"
                  ? "border-orange-500 text-orange-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Recovery Agencies
            </button>
          </nav>
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">Loading...</div>
        </div>
      ) : (
        <>
          {/* Legal Notices Tab */}
          {activeTab === "notices" && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Notice Details
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                        Amount Demanded
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                        Notice Date
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                        Delivery Status
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                        Response
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {notices.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                          No legal notices found
                        </td>
                      </tr>
                    ) : (
                      notices.map((notice) => (
                        <tr key={notice.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4">
                            <div className="text-sm">
                              <div className="font-medium text-gray-900">
                                {notice.notice_number}
                              </div>
                              <div className="text-gray-500 capitalize">
                                {notice.notice_type.replace(/_/g, " ")} - {notice.notice_stage}
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right">
                            <div className="text-sm font-semibold text-gray-900">
                              {formatCurrency(notice.notice_amount_demanded)}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-center">
                            <div className="text-sm text-gray-900">
                              {formatDate(notice.notice_date)}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-center">
                            <StatusBadge status={notice.delivery_status} type="notice" />
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-center">
                            {notice.response_received ? (
                              <span className="text-green-600 text-sm">✓ Received</span>
                            ) : (
                              <span className="text-gray-400 text-sm">Pending</span>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                            <Link
                              href={`/collections/legal/notices/${notice.id}`}
                              className="text-orange-600 hover:text-orange-900 font-medium"
                            >
                              View Details
                            </Link>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Court Cases Tab */}
          {activeTab === "cases" && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Case Details
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Court
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                        Claim Amount
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                        Filing Date
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                        Status
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                        Hearings
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {cases.length === 0 ? (
                      <tr>
                        <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                          No court cases found
                        </td>
                      </tr>
                    ) : (
                      cases.map((legalCase) => (
                        <tr key={legalCase.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4">
                            <div className="text-sm">
                              <div className="font-medium text-gray-900">
                                {legalCase.case_number}
                              </div>
                              <div className="text-gray-500 capitalize">
                                {legalCase.case_type.replace(/_/g, " ")}
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <div className="text-sm text-gray-900">
                              {legalCase.court_name || "N/A"}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right">
                            <div className="text-sm font-semibold text-gray-900">
                              {formatCurrency(legalCase.claim_amount)}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-center">
                            <div className="text-sm text-gray-900">
                              {formatDate(legalCase.filing_date)}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-center">
                            <StatusBadge status={legalCase.case_status} type="case" />
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-center">
                            <div className="text-sm text-gray-900">
                              {legalCase.total_hearings}
                            </div>
                            {legalCase.next_hearing_date && (
                              <div className="text-xs text-gray-500">
                                Next: {formatDate(legalCase.next_hearing_date)}
                              </div>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                            <Link
                              href={`/collections/legal/cases/${legalCase.id}`}
                              className="text-orange-600 hover:text-orange-900 font-medium"
                            >
                              View Case
                            </Link>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Recovery Agencies Tab */}
          {activeTab === "agencies" && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
              <Building2 className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">Recovery Agencies</h3>
              <p className="mt-1 text-sm text-gray-500">
                Manage external recovery agencies and track their performance
              </p>
              <div className="mt-6">
                <Link
                  href="/collections/legal/agencies/new"
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-orange-600 hover:bg-orange-700"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Recovery Agency
                </Link>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
