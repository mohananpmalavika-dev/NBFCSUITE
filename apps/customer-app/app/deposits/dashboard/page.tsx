/**
 * Deposits Dashboard - Analytics & Metrics
 * Comprehensive overview of deposit operations
 */

'use client';

import { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  TrendingDown,
  Users,
  PiggyBank,
  Calendar,
  AlertTriangle,
  ArrowUpRight,
  ArrowDownRight,
  DollarSign,
  BarChart3,
  Clock,
  RefreshCw
} from 'lucide-react';
import Link from 'next/link';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface DashboardData {
  total_deposits: number;
  total_accounts: number;
  active_accounts: number;
  total_interest_liability: number;
  avg_interest_rate: number;
  deposits_today: number;
  maturities_next_30_days: number;
  maturity_amount_next_30_days: number;
  renewals_this_month: number;
  premature_closures_this_month: number;
}

export default function DepositsDashboard() {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [treasury, setTreasury] = useState<any>(null);
  const [trends, setTrends] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('30');

  useEffect(() => {
    fetchDashboardData();
    fetchTreasuryData();
    fetchTrends();
  }, [timeRange]);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('http://localhost:8007/api/v1/dashboard/summary');
      const data = await response.json();
      setDashboard(data);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTreasuryData = async () => {
    try {
      const response = await fetch('http://localhost:8007/api/v1/dashboard/treasury');
      const data = await response.json();
      setTreasury(data);
    } catch (error) {
      console.error('Error fetching treasury:', error);
    }
  };

  const fetchTrends = async () => {
    try {
      const response = await fetch(`http://localhost:8007/api/v1/dashboard/analytics/trends?days=${timeRange}`);
      const data = await response.json();
      setTrends(data.trends || []);
    } catch (error) {
      console.error('Error fetching trends:', error);
    }
  };

  if (loading || !dashboard) {
    return <LoadingDashboard />;
  }

  // Calculate growth metrics
  const growthRate = ((dashboard.deposits_today / dashboard.total_deposits) * 100 * 30).toFixed(2);
  const renewalRate = ((dashboard.renewals_this_month / (dashboard.renewals_this_month + dashboard.premature_closures_this_month)) * 100).toFixed(0);

  // Prepare chart data
  const productDistribution = treasury?.product_wise_deposits ? 
    Object.entries(treasury.product_wise_deposits).map(([name, value]: any) => ({
      name: name.replace(/_/g, ' '),
      value: value
    })) : [];

  const branchDistribution = treasury?.branch_wise_deposits ?
    Object.entries(treasury.branch_wise_deposits).map(([name, value]: any) => ({
      name,
      value
    })) : [];

  const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-slate-900">Deposits Dashboard</h1>
            <p className="text-slate-600 mt-2">Real-time analytics and insights</p>
          </div>
          
          <div className="flex gap-3">
            <select 
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="7">Last 7 Days</option>
              <option value="30">Last 30 Days</option>
              <option value="90">Last 90 Days</option>
            </select>
            <button 
              onClick={() => {
                fetchDashboardData();
                fetchTreasuryData();
                fetchTrends();
              }}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            title="Total Deposits"
            value={`₹${(dashboard.total_deposits / 10000000).toFixed(2)} Cr`}
            change={`+${growthRate}%`}
            trend="up"
            icon={<PiggyBank className="w-6 h-6 text-blue-600" />}
            color="blue"
          />
          
          <MetricCard
            title="Active Accounts"
            value={dashboard.active_accounts.toLocaleString()}
            change={`${dashboard.total_accounts} total`}
            trend="neutral"
            icon={<Users className="w-6 h-6 text-green-600" />}
            color="green"
          />
          
          <MetricCard
            title="Avg. Interest Rate"
            value={`${dashboard.avg_interest_rate.toFixed(2)}%`}
            change="p.a."
            trend="neutral"
            icon={<TrendingUp className="w-6 h-6 text-purple-600" />}
            color="purple"
          />
          
          <MetricCard
            title="Maturing (30d)"
            value={`₹${(dashboard.maturity_amount_next_30_days / 10000000).toFixed(2)} Cr`}
            change={`${dashboard.maturities_next_30_days} accounts`}
            trend="neutral"
            icon={<Calendar className="w-6 h-6 text-orange-600" />}
            color="orange"
          />
        </div>

        {/* Secondary Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <SmallMetricCard
            title="Today's Deposits"
            value={`₹${(dashboard.deposits_today / 100000).toFixed(2)} L`}
            icon={<DollarSign className="w-5 h-5" />}
            color="blue"
          />
          
          <SmallMetricCard
            title="Renewals (This Month)"
            value={dashboard.renewals_this_month}
            subtitle={`${renewalRate}% renewal rate`}
            icon={<RefreshCw className="w-5 h-5" />}
            color="green"
          />
          
          <SmallMetricCard
            title="Premature Closures"
            value={dashboard.premature_closures_this_month}
            icon={<AlertTriangle className="w-5 h-5" />}
            color="orange"
          />
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Growth Trend */}
          <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-6">
            <h3 className="text-xl font-bold text-slate-900 mb-4">Deposit Growth Trend</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="amount" stroke="#3b82f6" strokeWidth={2} name="Amount (₹)" />
                <Line type="monotone" dataKey="count" stroke="#8b5cf6" strokeWidth={2} name="Accounts" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Product Distribution */}
          <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-6">
            <h3 className="text-xl font-bold text-slate-900 mb-4">Product Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={productDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {productDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Treasury Metrics */}
        {treasury && (
          <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-6">
            <h3 className="text-xl font-bold text-slate-900 mb-6">Treasury Analytics</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-6">
              <TreasuryMetric
                label="Total Base"
                value={`₹${(treasury.total_deposit_base / 10000000).toFixed(2)} Cr`}
              />
              <TreasuryMetric
                label="Cost of Funds"
                value={`${treasury.cost_of_funds.toFixed(2)}%`}
              />
              <TreasuryMetric
                label="Liquidity"
                value={`₹${(treasury.liquidity_position / 10000000).toFixed(2)} Cr`}
              />
              <TreasuryMetric
                label="Pipeline (7d)"
                value={`₹${(treasury.maturity_pipeline_7_days / 10000000).toFixed(2)} Cr`}
              />
              <TreasuryMetric
                label="Pipeline (30d)"
                value={`₹${(treasury.maturity_pipeline_30_days / 10000000).toFixed(2)} Cr`}
              />
              <TreasuryMetric
                label="Pipeline (90d)"
                value={`₹${(treasury.maturity_pipeline_90_days / 10000000).toFixed(2)} Cr`}
              />
            </div>
          </div>
        )}

        {/* Branch Performance */}
        {branchDistribution.length > 0 && (
          <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-6">
            <h3 className="text-xl font-bold text-slate-900 mb-4">Branch-wise Performance</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={branchDistribution}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#3b82f6" name="Deposits (₹)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <ActionCard
            title="Maturity Pipeline"
            description="View upcoming maturities"
            count={dashboard.maturities_next_30_days}
            href="/deposits/maturity/pipeline"
            color="purple"
          />
          <ActionCard
            title="Pending Approvals"
            description="Review pending accounts"
            count={0}
            href="/deposits/approvals"
            color="orange"
          />
          <ActionCard
            title="AI Insights"
            description="View predictions"
            count={null}
            href="/deposits/ai/insights"
            color="pink"
          />
        </div>
      </div>
    </div>
  );
}

// Components

function MetricCard({ 
  title, 
  value, 
  change, 
  trend, 
  icon, 
  color 
}: {
  title: string;
  value: string;
  change: string;
  trend: 'up' | 'down' | 'neutral';
  icon: React.ReactNode;
  color: string;
}) {
  const colorClasses = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600',
    purple: 'from-purple-500 to-purple-600',
    orange: 'from-orange-500 to-orange-600'
  }[color];

  return (
    <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-6 hover:shadow-xl transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 bg-gradient-to-br ${colorClasses} rounded-xl`}>
          <div className="text-white">{icon}</div>
        </div>
        {trend !== 'neutral' && (
          <div className={`flex items-center gap-1 ${
            trend === 'up' ? 'text-green-600' : 'text-red-600'
          }`}>
            {trend === 'up' ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
            <span className="text-sm font-medium">{change}</span>
          </div>
        )}
      </div>
      <p className="text-slate-600 text-sm mb-1">{title}</p>
      <p className="text-3xl font-bold text-slate-900">{value}</p>
      {trend === 'neutral' && (
        <p className="text-slate-500 text-sm mt-1">{change}</p>
      )}
    </div>
  );
}

function SmallMetricCard({ 
  title, 
  value, 
  subtitle, 
  icon, 
  color 
}: {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  color: string;
}) {
  const bgColor = {
    blue: 'bg-blue-100',
    green: 'bg-green-100',
    orange: 'bg-orange-100'
  }[color];

  return (
    <div className="bg-white rounded-xl shadow border border-slate-200 p-4">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-slate-600 text-sm mb-2">{title}</p>
          <p className="text-2xl font-bold text-slate-900">{value}</p>
          {subtitle && <p className="text-slate-500 text-xs mt-1">{subtitle}</p>}
        </div>
        <div className={`p-2 ${bgColor} rounded-lg`}>
          {icon}
        </div>
      </div>
    </div>
  );
}

function TreasuryMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="text-center">
      <p className="text-slate-600 text-sm mb-1">{label}</p>
      <p className="text-xl font-bold text-slate-900">{value}</p>
    </div>
  );
}

function ActionCard({ 
  title, 
  description, 
  count, 
  href, 
  color 
}: {
  title: string;
  description: string;
  count: number | null;
  href: string;
  color: string;
}) {
  const colorClasses = {
    purple: 'from-purple-500 to-purple-600',
    orange: 'from-orange-500 to-orange-600',
    pink: 'from-pink-500 to-pink-600'
  }[color];

  return (
    <Link href={href}>
      <div className="group bg-white rounded-xl shadow-lg border border-slate-200 p-6 hover:shadow-xl transition-all cursor-pointer">
        <div className="flex items-start justify-between mb-3">
          <div className={`p-3 bg-gradient-to-br ${colorClasses} rounded-xl text-white`}>
            {count !== null ? (
              <span className="text-2xl font-bold">{count}</span>
            ) : (
              <BarChart3 className="w-6 h-6" />
            )}
          </div>
        </div>
        <h3 className="font-bold text-slate-900 mb-1">{title}</h3>
        <p className="text-slate-600 text-sm">{description}</p>
      </div>
    </Link>
  );
}

function LoadingDashboard() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 p-8 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-slate-600">Loading dashboard...</p>
      </div>
    </div>
  );
}
