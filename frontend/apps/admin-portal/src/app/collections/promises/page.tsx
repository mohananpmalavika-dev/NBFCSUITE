"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Plus, Calendar, TrendingUp, CheckCircle, XCircle, Clock } from "lucide-react";
import { promiseApi } from "@/lib/api/collection";
import { PaymentPromise, PromiseAnalytics } from "@/types/collection";
import { StatusBadge, CollectionStatCard } from "@/components/collections";

export default function PaymentPromisesPage() {
  const [promises, setPromises] = useState<PaymentPromise[]>([]);
  const [analytics, setAnalytics] = useState<PromiseAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState<string>("");

  useEffect(() => {
    fetchData();
  }, [filterStatus]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [promisesRes, analyticsRes] = await Promise.all([
        promiseApi.list({ status: filterStatus || undefined, limit: 50 }),
        promiseApi.getAnalytics()
      ]);
      setPromises(promisesRes.items);
      setAnalytics(analyticsRes);
    } catch (error) {
      console.error("Error fetching promise data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckFulfillment = async () => {
    try {
      await promiseApi.checkFulfillment();
      alert("Promise fulfillment check completed!");
      fetchData();
    } catch (error) {
      console.error("Error checking fulfillment:", error);
      alert("Failed to check fulfillment");
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

  const isPromiseOverdue = (promise: PaymentPromise) => {
    if (promise.promise_status !== "pending") return false;
    return new Date(promise.promise_date) < new Date();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading promises...</div>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-gray-900">Payment Promises</h2>
            <p className="mt-1 text-sm text-gray-500">
              Track customer payment commitments and fulfillment
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleCheckFulfillment}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <CheckCircle className="h-4 w-4 mr-2" />
              Check Fulfillment
            </button>
            <Link
              href="/collections/promises/new"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-orange-600 hover:bg-orange-700"
            >
              <Plus className="h-4 w-4 mr-2" />
              New Promise
            </Link>
          </div>
        </div>
      </div>

      {/* Analytics Summary */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <CollectionStatCard
            title="Total Promises"
            value={analytics.summary.total_promises}
            icon={Calendar}
            color="bg-blue-600"
          />
          <CollectionStatCard
            title="Promised Amount"
            value={formatCurrency(analytics.summary.total_promised_amount)}
            icon={TrendingUp}
            color="bg-purple-600"
          />
          <CollectionStatCard
            title="Collected Amount"
            value={formatCurrency(analytics.summary.total_collected_amount)}
            icon={CheckCircle}
            color="bg-green-600"
          />
          <CollectionStatCard
            title="Fulfillment Rate"
            value={`${analytics.summary.fulfillment_rate.toFixed(1)}%`}
            icon={TrendingUp}
            color="bg-orange-600"
          />
        </div>
      )}

      {/* Status Filter */}
      <div className="mb-6">
        <div className="flex gap-2">
          <button
            onClick={() => setFilterStatus("")}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filterStatus === ""
                ? "bg-orange-600 text-white"
                : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilterStatus("pending")}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filterStatus === "pending"
                ? "bg-orange-600 text-white"
                : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
            }`}
          >
            Pending
          </button>
          <button
            onClick={() => setFilterStatus("kept")}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filterStatus === "kept"
                ? "bg-orange-600 text-white"
                : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
            }`}
          >
            Kept
          </button>
          <button
            onClick={() => setFilterStatus("broken")}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filterStatus === "broken"
                ? "bg-orange-600 text-white"
                : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
            }`}
          >
            Broken
          </button>
        </div>
      </div>

      {/* Promises List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Payment Promises ({promises.length})
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Customer / Account
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Promise Amount
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                  Promise Date
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                  Source
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {promises.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                    No payment promises found
                  </td>
                </tr>
              ) : (
                promises.map((promise) => (
                  <tr
                    key={promise.id}
                    className={`hover:bg-gray-50 ${
                      isPromiseOverdue(promise) ? "bg-red-50" : ""
                    }`}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm">
                        <div className="font-medium text-gray-900">
                          Customer #{promise.customer_id}
                        </div>
                        <div className="text-gray-500">
                          Loan #{promise.loan_account_id}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <div className="text-sm font-semibold text-gray-900">
                        {formatCurrency(promise.promise_amount)}
                      </div>
                      {promise.actual_payment_amount && (
                        <div className="text-xs text-green-600">
                          Paid: {formatCurrency(promise.actual_payment_amount)}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      <div className="text-sm text-gray-900 flex items-center justify-center">
                        <Calendar className="h-3 w-3 mr-1" />
                        {formatDate(promise.promise_date)}
                      </div>
                      {isPromiseOverdue(promise) && (
                        <div className="text-xs text-red-600 mt-1">Overdue</div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      <span className="text-xs font-medium text-gray-700 capitalize">
                        {promise.promised_by.replace("_", " ")}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      <StatusBadge status={promise.promise_status} type="promise" />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm space-x-2">
                      {promise.promise_status === "pending" && (
                        <>
                          <Link
                            href={`/collections/promises/${promise.id}/reschedule`}
                            className="text-orange-600 hover:text-orange-900 font-medium"
                          >
                            Reschedule
                          </Link>
                          <Link
                            href={`/collections/promises/${promise.id}/mark-kept`}
                            className="text-green-600 hover:text-green-900 font-medium"
                          >
                            Mark Kept
                          </Link>
                        </>
                      )}
                      <Link
                        href={`/collections/promises/${promise.id}`}
                        className="text-blue-600 hover:text-blue-900 font-medium"
                      >
                        View
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Info Box */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-blue-900 mb-2">
          <Clock className="inline h-4 w-4 mr-1" />
          Automatic Promise Tracking
        </h4>
        <p className="text-sm text-blue-700">
          The system automatically checks promise fulfillment daily. Promises are marked as "kept" 
          when payment is received, or "broken" if payment is not received within 2 days of the promise date.
        </p>
      </div>
    </div>
  );
}
