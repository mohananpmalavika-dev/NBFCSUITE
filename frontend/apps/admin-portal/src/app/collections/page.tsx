"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { 
  AlertCircle, 
  TrendingUp,
  Users,
  DollarSign,
  Clock,
  Target,
  ArrowUpRight,
  ArrowDownRight
} from "lucide-react";

interface CollectionStats {
  total_overdue_accounts: number;
  total_overdue_amount: number;
  average_dpd: number;
  collection_efficiency: number;
  bucket_0_30: { count: number; amount: number };
  bucket_31_60: { count: number; amount: number };
  bucket_61_90: { count: number; amount: number };
  bucket_91_180: { count: number; amount: number };
  bucket_180_plus: { count: number; amount: number };
}

interface TopOverdueAccount {
  id: number;
  account_number: string;
  customer_name: string;
  overdue_amount: number;
  dpd: number;
  last_payment_date: string;
}

function StatCard({ 
  title, 
  value, 
  subtitle,
  icon: Icon,
  color,
  trend
}: { 
  title: string; 
  value: string | number; 
  subtitle?: string;
  icon: any;
  color: string;
  trend?: { value: number; isPositive: boolean };
}) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">{value}</p>
          {subtitle && (
            <p className="mt-1 text-sm text-gray-500">{subtitle}</p>
          )}
          {trend && (
            <div className="mt-2 flex items-center">
              {trend.isPositive ? (
                <ArrowDownRight className="h-4 w-4 text-green-500" />
              ) : (
                <ArrowUpRight className="h-4 w-4 text-red-500" />
              )}
              <span className={`text-sm font-medium ${trend.isPositive ? 'text-green-600' : 'text-red-600'}`}>
                {Math.abs(trend.value).toFixed(1)}%
              </span>
              <span className="ml-2 text-sm text-gray-500">vs last month</span>
            </div>
          )}
        </div>
        <div className={`p-3 rounded-full ${color}`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
      </div>
    </div>
  );
}

function DPDBucketCard({
  title,
  count,
  amount,
  color,
  percentage
}: {
  title: string;
  count: number;
  amount: number;
  color: string;
  percentage: number;
}) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-700">{title}</h3>
        <span className={`px-2 py-1 text-xs font-medium rounded-full ${color}`}>
          {count} accounts
        </span>
      </div>
      <p className="text-2xl font-bold text-gray-900">
        ₹{amount.toLocaleString("en-IN")}
      </p>
      <div className="mt-4">
        <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
          <span>Portfolio %</span>
          <span>{percentage.toFixed(1)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full ${color.replace('text', 'bg')}`}
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>
    </div>
  );
}

export default function CollectionDashboard() {
  const [stats, setStats] = useState<CollectionStats | null>(null);
  const [topOverdue, setTopOverdue] = useState<TopOverdueAccount[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCollectionData();
  }, []);

  const fetchCollectionData = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API calls
      const mockStats: CollectionStats = {
        total_overdue_accounts: 127,
        total_overdue_amount: 3850000.00,
        average_dpd: 45,
        collection_efficiency: 87.5,
        bucket_0_30: { count: 45, amount: 850000.00 },
        bucket_31_60: { count: 32, amount: 1200000.00 },
        bucket_61_90: { count: 25, amount: 950000.00 },
        bucket_91_180: { count: 18, amount: 650000.00 },
        bucket_180_plus: { count: 7, amount: 200000.00 },
      };

      const mockTopOverdue: TopOverdueAccount[] = [
        {
          id: 1,
          account_number: "LA-202512-0045",
          customer_name: "Rajesh Kumar",
          overdue_amount: 125000.00,
          dpd: 95,
          last_payment_date: "2025-10-02",
        },
        {
          id: 2,
          account_number: "LA-202511-0123",
          customer_name: "Priya Sharma",
          overdue_amount: 98000.00,
          dpd: 87,
          last_payment_date: "2025-10-10",
        },
        {
          id: 3,
          account_number: "LA-202510-0234",
          customer_name: "Amit Patel",
          overdue_amount: 87500.00,
          dpd: 112,
          last_payment_date: "2025-09-15",
        },
        {
          id: 4,
          account_number: "LA-202512-0089",
          customer_name: "Sneha Reddy",
          overdue_amount: 75000.00,
          dpd: 68,
          last_payment_date: "2025-10-29",
        },
        {
          id: 5,
          account_number: "LA-202511-0201",
          customer_name: "Vijay Singh",
          overdue_amount: 72000.00,
          dpd: 73,
          last_payment_date: "2025-10-24",
        },
      ];

      setStats(mockStats);
      setTopOverdue(mockTopOverdue);
    } catch (error) {
      console.error("Error fetching collection data:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading collection dashboard...</div>
      </div>
    );
  }

  const totalOverdueAmount = stats?.total_overdue_amount || 0;

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900">Collection Dashboard</h2>
        <p className="mt-1 text-sm text-gray-500">
          Monitor overdue accounts and collection performance
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Overdue Accounts"
          value={stats?.total_overdue_accounts || 0}
          subtitle="Active overdue"
          icon={Users}
          color="bg-red-600"
          trend={{ value: 5.2, isPositive: false }}
        />
        <StatCard
          title="Total Overdue Amount"
          value={`₹${(stats?.total_overdue_amount || 0).toLocaleString("en-IN", {
            maximumFractionDigits: 0,
          })}`}
          icon={DollarSign}
          color="bg-orange-600"
          trend={{ value: 3.8, isPositive: false }}
        />
        <StatCard
          title="Average DPD"
          value={`${stats?.average_dpd || 0} days`}
          subtitle="Days Past Due"
          icon={Clock}
          color="bg-yellow-600"
        />
        <StatCard
          title="Collection Efficiency"
          value={`${stats?.collection_efficiency || 0}%`}
          subtitle="This month"
          icon={Target}
          color="bg-green-600"
          trend={{ value: 2.1, isPositive: true }}
        />
      </div>

      {/* DPD Buckets */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">DPD Bucket Analysis</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <DPDBucketCard
            title="0-30 Days"
            count={stats?.bucket_0_30.count || 0}
            amount={stats?.bucket_0_30.amount || 0}
            color="bg-yellow-100 text-yellow-800"
            percentage={(stats?.bucket_0_30.amount || 0) / totalOverdueAmount * 100}
          />
          <DPDBucketCard
            title="31-60 Days"
            count={stats?.bucket_31_60.count || 0}
            amount={stats?.bucket_31_60.amount || 0}
            color="bg-orange-100 text-orange-800"
            percentage={(stats?.bucket_31_60.amount || 0) / totalOverdueAmount * 100}
          />
          <DPDBucketCard
            title="61-90 Days"
            count={stats?.bucket_61_90.count || 0}
            amount={stats?.bucket_61_90.amount || 0}
            color="bg-red-100 text-red-800"
            percentage={(stats?.bucket_61_90.amount || 0) / totalOverdueAmount * 100}
          />
          <DPDBucketCard
            title="91-180 Days"
            count={stats?.bucket_91_180.count || 0}
            amount={stats?.bucket_91_180.amount || 0}
            color="bg-purple-100 text-purple-800"
            percentage={(stats?.bucket_91_180.amount || 0) / totalOverdueAmount * 100}
          />
          <DPDBucketCard
            title="180+ Days (NPA)"
            count={stats?.bucket_180_plus.count || 0}
            amount={stats?.bucket_180_plus.amount || 0}
            color="bg-gray-100 text-gray-800"
            percentage={(stats?.bucket_180_plus.amount || 0) / totalOverdueAmount * 100}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Overdue Accounts */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Top Overdue Accounts</h3>
              <Link
                href="/collections/overdue"
                className="text-sm text-orange-600 hover:text-orange-700 font-medium"
              >
                View All
              </Link>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Account
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Customer
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                    Overdue Amount
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                    DPD
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {topOverdue.map((account) => (
                  <tr key={account.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {account.account_number}
                      </div>
                      <div className="text-xs text-gray-500">
                        Last payment: {new Date(account.last_payment_date).toLocaleDateString("en-IN")}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{account.customer_name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <div className="text-sm font-semibold text-red-600">
                        ₹{account.overdue_amount.toLocaleString("en-IN")}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        account.dpd > 90 
                          ? 'bg-red-100 text-red-800'
                          : account.dpd > 60
                          ? 'bg-orange-100 text-orange-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {account.dpd} days
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                      <button className="text-orange-600 hover:text-orange-900 font-medium">
                        Follow Up
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <Link
              href="/collections/overdue"
              className="flex items-center p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
            >
              <AlertCircle className="h-5 w-5 text-red-600" />
              <span className="ml-3 text-sm font-medium text-gray-900">
                View Overdue Accounts
              </span>
            </Link>
            <Link
              href="/collections/queue"
              className="flex items-center p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
            >
              <Users className="h-5 w-5 text-orange-600" />
              <span className="ml-3 text-sm font-medium text-gray-900">
                Collection Queue
              </span>
            </Link>
            <button
              onClick={() => {/* TODO: Update overdue status */}}
              className="w-full flex items-center p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
            >
              <TrendingUp className="h-5 w-5 text-blue-600" />
              <span className="ml-3 text-sm font-medium text-gray-900">
                Update Overdue Status
              </span>
            </button>
          </div>

          {/* Priority Alerts */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h4 className="text-sm font-semibold text-gray-900 mb-3">Priority Alerts</h4>
            <div className="space-y-2">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <div className="h-2 w-2 mt-1.5 rounded-full bg-red-500"></div>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-gray-900">{stats?.bucket_180_plus.count} accounts in NPA</p>
                  <p className="text-xs text-gray-500">Immediate action required</p>
                </div>
              </div>
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <div className="h-2 w-2 mt-1.5 rounded-full bg-orange-500"></div>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-gray-900">{stats?.bucket_91_180.count} accounts 90+ DPD</p>
                  <p className="text-xs text-gray-500">High priority follow-up</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
