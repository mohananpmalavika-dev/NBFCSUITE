"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { 
  TrendingUp, 
  TrendingDown,
  DollarSign,
  FileText,
  PieChart,
  BarChart3,
  ArrowUpRight,
  ArrowDownRight
} from "lucide-react";

interface DashboardStats {
  total_assets: number;
  total_liabilities: number;
  total_equity: number;
  total_income: number;
  total_expenses: number;
  net_profit: number;
  total_accounts: number;
  posted_entries: number;
}

interface RecentTransaction {
  id: number;
  entry_number: string;
  entry_date: string;
  narration: string;
  amount: number;
  status: string;
}

function MetricCard({ 
  title, 
  value, 
  change, 
  icon: Icon,
  trend,
  color 
}: { 
  title: string; 
  value: number; 
  change?: number;
  icon: any;
  trend?: 'up' | 'down';
  color: string;
}) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">
            ₹{value.toLocaleString("en-IN", {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}
          </p>
          {change !== undefined && (
            <div className="mt-2 flex items-center">
              {trend === 'up' ? (
                <ArrowUpRight className="h-4 w-4 text-green-500" />
              ) : (
                <ArrowDownRight className="h-4 w-4 text-red-500" />
              )}
              <span className={`text-sm font-medium ${trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                {Math.abs(change).toFixed(1)}%
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

export default function AccountingDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentTransactions, setRecentTransactions] = useState<RecentTransaction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API calls
      const mockStats: DashboardStats = {
        total_assets: 15000000.00,
        total_liabilities: 8000000.00,
        total_equity: 5000000.00,
        total_income: 2500000.00,
        total_expenses: 1200000.00,
        net_profit: 1300000.00,
        total_accounts: 45,
        posted_entries: 1250,
      };

      const mockTransactions: RecentTransaction[] = [
        {
          id: 1,
          entry_number: "JE-202601-0125",
          entry_date: "2026-01-05",
          narration: "Loan disbursement - Account #1023",
          amount: 100000.00,
          status: "posted",
        },
        {
          id: 2,
          entry_number: "JE-202601-0124",
          entry_date: "2026-01-05",
          narration: "Loan repayment received",
          amount: 15000.00,
          status: "posted",
        },
        {
          id: 3,
          entry_number: "JE-202601-0123",
          entry_date: "2026-01-04",
          narration: "Office rent payment",
          amount: 50000.00,
          status: "posted",
        },
        {
          id: 4,
          entry_number: "JE-202601-0122",
          entry_date: "2026-01-04",
          narration: "Interest accrual",
          amount: 25000.00,
          status: "posted",
        },
      ];

      setStats(mockStats);
      setRecentTransactions(mockTransactions);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900">Accounting Dashboard</h2>
        <p className="mt-1 text-sm text-gray-500">
          Overview of your financial position and recent activity
        </p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <MetricCard
          title="Total Assets"
          value={stats?.total_assets || 0}
          change={12.5}
          trend="up"
          icon={TrendingUp}
          color="bg-blue-600"
        />
        <MetricCard
          title="Total Liabilities"
          value={stats?.total_liabilities || 0}
          change={8.3}
          trend="up"
          icon={TrendingDown}
          color="bg-red-600"
        />
        <MetricCard
          title="Total Equity"
          value={stats?.total_equity || 0}
          change={5.2}
          trend="up"
          icon={DollarSign}
          color="bg-purple-600"
        />
        <MetricCard
          title="Total Income"
          value={stats?.total_income || 0}
          change={18.7}
          trend="up"
          icon={TrendingUp}
          color="bg-green-600"
        />
        <MetricCard
          title="Total Expenses"
          value={stats?.total_expenses || 0}
          change={3.4}
          trend="up"
          icon={TrendingDown}
          color="bg-orange-600"
        />
        <MetricCard
          title="Net Profit"
          value={stats?.net_profit || 0}
          change={22.1}
          trend="up"
          icon={BarChart3}
          color="bg-emerald-600"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Transactions */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Recent Transactions</h3>
              <Link
                href="/accounting/journal-entries"
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                View All
              </Link>
            </div>
          </div>
          <div className="divide-y divide-gray-200">
            {recentTransactions.map((transaction) => (
              <div key={transaction.id} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center">
                      <p className="text-sm font-medium text-gray-900">
                        {transaction.entry_number}
                      </p>
                      <span className="ml-2 px-2 py-0.5 text-xs bg-green-100 text-green-800 rounded-full">
                        {transaction.status}
                      </span>
                    </div>
                    <p className="mt-1 text-sm text-gray-600">{transaction.narration}</p>
                    <p className="mt-1 text-xs text-gray-500">
                      {new Date(transaction.entry_date).toLocaleDateString("en-IN", {
                        year: "numeric",
                        month: "short",
                        day: "numeric",
                      })}
                    </p>
                  </div>
                  <div className="ml-4 text-right">
                    <p className="text-sm font-semibold text-gray-900">
                      ₹{transaction.amount.toLocaleString("en-IN")}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <Link
              href="/accounting/journal-entries/new"
              className="flex items-center p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
            >
              <FileText className="h-5 w-5 text-blue-600" />
              <span className="ml-3 text-sm font-medium text-gray-900">
                New Journal Entry
              </span>
            </Link>
            <Link
              href="/accounting/reports/trial-balance"
              className="flex items-center p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
            >
              <PieChart className="h-5 w-5 text-purple-600" />
              <span className="ml-3 text-sm font-medium text-gray-900">
                Trial Balance
              </span>
            </Link>
            <Link
              href="/accounting/reports/profit-loss"
              className="flex items-center p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
            >
              <BarChart3 className="h-5 w-5 text-green-600" />
              <span className="ml-3 text-sm font-medium text-gray-900">
                P&L Statement
              </span>
            </Link>
            <Link
              href="/accounting/reports/balance-sheet"
              className="flex items-center p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
            >
              <BarChart3 className="h-5 w-5 text-orange-600" />
              <span className="ml-3 text-sm font-medium text-gray-900">
                Balance Sheet
              </span>
            </Link>
          </div>

          {/* Summary Stats */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Total Accounts</span>
                <span className="text-sm font-semibold text-gray-900">{stats?.total_accounts}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Posted Entries</span>
                <span className="text-sm font-semibold text-gray-900">{stats?.posted_entries}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Current Period</span>
                <span className="text-sm font-semibold text-gray-900">Jan 2026</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
