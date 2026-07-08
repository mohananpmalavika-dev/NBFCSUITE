'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Building2, 
  TrendingUp, 
  FileText, 
  DollarSign,
  AlertCircle,
  CheckCircle,
  Clock,
  Users,
  ArrowUpRight,
  ArrowDownRight,
  Activity
} from 'lucide-react';
import { bancassuranceService } from '@/services/bancassurance.service';
import type { 
  InsurancePolicy, 
  InsurancePremium, 
  InsuranceClaim, 
  InsuranceCommission 
} from '@/types/bancassurance';
import { 
  PolicyStatus, 
  PremiumStatus, 
  ClaimStatus, 
  CommissionStatus,
  formatCurrency, 
  formatDate,
  isOverdue 
} from '@/types/bancassurance';

interface DashboardStats {
  policies: {
    total: number;
    active: number;
    lapsed: number;
    matured: number;
    totalSumAssured: number;
    recentChange: number;
  };
  premiums: {
    total: number;
    paid: number;
    pending: number;
    overdue: number;
    totalCollected: number;
    recentChange: number;
  };
  claims: {
    total: number;
    registered: number;
    assessed: number;
    approved: number;
    settled: number;
    totalAmount: number;
    recentChange: number;
  };
  commissions: {
    total: number;
    pending: number;
    approved: number;
    paid: number;
    totalAmount: number;
    recentChange: number;
  };
}

interface RecentActivity {
  id: string;
  type: 'policy' | 'premium' | 'claim' | 'commission';
  title: string;
  description: string;
  timestamp: string;
  status: string;
  amount?: number;
}

export default function BancassuranceDashboard() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch all data in parallel
      const [policies, premiums, claims, commissions] = await Promise.all([
        bancassuranceService.listPolicies(),
        bancassuranceService.listPremiums(),
        bancassuranceService.listClaims(),
        bancassuranceService.listCommissions()
      ]);

      // Calculate policy stats
      const policyStats = {
        total: policies.length,
        active: policies.filter(p => p.status === PolicyStatus.ACTIVE).length,
        lapsed: policies.filter(p => p.status === PolicyStatus.LAPSED).length,
        matured: policies.filter(p => p.status === PolicyStatus.MATURED).length,
        totalSumAssured: policies.reduce((sum, p) => sum + (p.sum_assured || 0), 0),
        recentChange: 12.5 // Placeholder for month-over-month growth
      };

      // Calculate premium stats
      const premiumStats = {
        total: premiums.length,
        paid: premiums.filter(p => p.status === PremiumStatus.PAID).length,
        pending: premiums.filter(p => p.status === PremiumStatus.PENDING).length,
        overdue: premiums.filter(p => isOverdue(p.due_date, p.status)).length,
        totalCollected: premiums
          .filter(p => p.status === PremiumStatus.PAID)
          .reduce((sum, p) => sum + (p.amount || 0), 0),
        recentChange: 8.3
      };

      // Calculate claim stats
      const claimStats = {
        total: claims.length,
        registered: claims.filter(c => c.status === ClaimStatus.REGISTERED).length,
        assessed: claims.filter(c => c.status === ClaimStatus.ASSESSED).length,
        approved: claims.filter(c => c.status === ClaimStatus.APPROVED).length,
        settled: claims.filter(c => c.status === ClaimStatus.SETTLED).length,
        totalAmount: claims
          .filter(c => c.status === ClaimStatus.SETTLED)
          .reduce((sum, c) => sum + (c.settled_amount || 0), 0),
        recentChange: -3.2
      };

      // Calculate commission stats
      const commissionStats = {
        total: commissions.length,
        pending: commissions.filter(c => c.status === CommissionStatus.PENDING).length,
        approved: commissions.filter(c => c.status === CommissionStatus.APPROVED).length,
        paid: commissions.filter(c => c.status === CommissionStatus.PAID).length,
        totalAmount: commissions
          .filter(c => c.status === CommissionStatus.PAID)
          .reduce((sum, c) => sum + (c.amount || 0), 0),
        recentChange: 15.7
      };

      setStats({
        policies: policyStats,
        premiums: premiumStats,
        claims: claimStats,
        commissions: commissionStats
      });

      // Build recent activity feed
      const activities: RecentActivity[] = [];

      // Add recent policies
      policies.slice(0, 3).forEach(p => {
        activities.push({
          id: `policy-${p.id}`,
          type: 'policy',
          title: `Policy ${p.policy_number}`,
          description: `${p.policy_type} policy ${p.status.toLowerCase()}`,
          timestamp: p.updated_at || p.created_at,
          status: p.status,
          amount: p.sum_assured
        });
      });

      // Add recent premiums
      premiums
        .filter(p => p.status === PremiumStatus.PAID)
        .slice(0, 3)
        .forEach(p => {
          activities.push({
            id: `premium-${p.id}`,
            type: 'premium',
            title: `Premium Payment`,
            description: `Policy ${p.policy_id} premium paid`,
            timestamp: p.paid_date || p.created_at,
            status: p.status,
            amount: p.amount
          });
        });

      // Add recent claims
      claims.slice(0, 3).forEach(c => {
        activities.push({
          id: `claim-${c.id}`,
          type: 'claim',
          title: `Claim ${c.claim_number}`,
          description: `${c.claim_type} claim ${c.status.toLowerCase()}`,
          timestamp: c.updated_at || c.created_at,
          status: c.status,
          amount: c.claimed_amount
        });
      });

      // Add recent commissions
      commissions.slice(0, 3).forEach(c => {
        activities.push({
          id: `commission-${c.id}`,
          type: 'commission',
          title: 'Commission',
          description: `Agent ${c.agent_id} commission ${c.status.toLowerCase()}`,
          timestamp: c.updated_at || c.created_at,
          status: c.status,
          amount: c.amount
        });
      });

      // Sort by timestamp and take top 10
      activities.sort((a, b) => 
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      );
      setRecentActivity(activities.slice(0, 10));

    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError('Failed to load dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center gap-3">
          <AlertCircle className="h-5 w-5 text-red-600" />
          <div>
            <h3 className="font-semibold text-red-900">Error</h3>
            <p className="text-red-700">{error}</p>
          </div>
        </div>
        <button
          onClick={loadDashboardData}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!stats) {
    return <div className="text-center text-gray-500">No data available</div>;
  }

  const getActivityIcon = (type: RecentActivity['type']) => {
    switch (type) {
      case 'policy': return <Building2 className="h-4 w-4" />;
      case 'premium': return <DollarSign className="h-4 w-4" />;
      case 'claim': return <FileText className="h-4 w-4" />;
      case 'commission': return <TrendingUp className="h-4 w-4" />;
    }
  };

  const getActivityColor = (type: RecentActivity['type']) => {
    switch (type) {
      case 'policy': return 'bg-blue-100 text-blue-600';
      case 'premium': return 'bg-green-100 text-green-600';
      case 'claim': return 'bg-orange-100 text-orange-600';
      case 'commission': return 'bg-purple-100 text-purple-600';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Insurance & Bancassurance</h1>
          <p className="text-gray-600 mt-1">
            Comprehensive dashboard for policy management, premiums, claims, and commissions
          </p>
        </div>
        <button
          onClick={loadDashboardData}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <Activity className="h-4 w-4" />
          Refresh
        </button>
      </div>

      {/* Quick Action Buttons */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <button
          onClick={() => router.push('/bancassurance/policies')}
          className="p-4 bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all shadow-lg hover:shadow-xl"
        >
          <Building2 className="h-6 w-6 mb-2" />
          <h3 className="font-semibold">Policies</h3>
          <p className="text-sm opacity-90">Manage insurance policies</p>
        </button>

        <button
          onClick={() => router.push('/bancassurance/premiums')}
          className="p-4 bg-gradient-to-br from-green-500 to-green-600 text-white rounded-lg hover:from-green-600 hover:to-green-700 transition-all shadow-lg hover:shadow-xl"
        >
          <DollarSign className="h-6 w-6 mb-2" />
          <h3 className="font-semibold">Premiums</h3>
          <p className="text-sm opacity-90">Track premium collection</p>
        </button>

        <button
          onClick={() => router.push('/bancassurance/claims')}
          className="p-4 bg-gradient-to-br from-orange-500 to-orange-600 text-white rounded-lg hover:from-orange-600 hover:to-orange-700 transition-all shadow-lg hover:shadow-xl"
        >
          <FileText className="h-6 w-6 mb-2" />
          <h3 className="font-semibold">Claims</h3>
          <p className="text-sm opacity-90">Process insurance claims</p>
        </button>

        <button
          onClick={() => router.push('/bancassurance/commissions')}
          className="p-4 bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-lg hover:from-purple-600 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl"
        >
          <TrendingUp className="h-6 w-6 mb-2" />
          <h3 className="font-semibold">Commissions</h3>
          <p className="text-sm opacity-90">Track agent commissions</p>
        </button>
      </div>

      {/* Policy Statistics */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Building2 className="h-5 w-5 text-blue-600" />
            <h2 className="text-xl font-semibold">Policy Overview</h2>
          </div>
          <span className={`flex items-center gap-1 text-sm font-medium ${stats.policies.recentChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {stats.policies.recentChange >= 0 ? <ArrowUpRight className="h-4 w-4" /> : <ArrowDownRight className="h-4 w-4" />}
            {Math.abs(stats.policies.recentChange)}%
          </span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <p className="text-2xl font-bold text-gray-900">{stats.policies.total}</p>
            <p className="text-sm text-gray-600">Total Policies</p>
          </div>
          <div className="text-center p-3 bg-green-50 rounded-lg">
            <p className="text-2xl font-bold text-green-600">{stats.policies.active}</p>
            <p className="text-sm text-gray-600">Active</p>
          </div>
          <div className="text-center p-3 bg-orange-50 rounded-lg">
            <p className="text-2xl font-bold text-orange-600">{stats.policies.lapsed}</p>
            <p className="text-sm text-gray-600">Lapsed</p>
          </div>
          <div className="text-center p-3 bg-blue-50 rounded-lg">
            <p className="text-2xl font-bold text-blue-600">{stats.policies.matured}</p>
            <p className="text-sm text-gray-600">Matured</p>
          </div>
          <div className="text-center p-3 bg-purple-50 rounded-lg">
            <p className="text-2xl font-bold text-purple-600">{formatCurrency(stats.policies.totalSumAssured)}</p>
            <p className="text-sm text-gray-600">Sum Assured</p>
          </div>
        </div>
      </div>

      {/* Premium Statistics */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <DollarSign className="h-5 w-5 text-green-600" />
            <h2 className="text-xl font-semibold">Premium Collection</h2>
          </div>
          <span className={`flex items-center gap-1 text-sm font-medium ${stats.premiums.recentChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {stats.premiums.recentChange >= 0 ? <ArrowUpRight className="h-4 w-4" /> : <ArrowDownRight className="h-4 w-4" />}
            {Math.abs(stats.premiums.recentChange)}%
          </span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <p className="text-2xl font-bold text-gray-900">{stats.premiums.total}</p>
            <p className="text-sm text-gray-600">Total Premiums</p>
          </div>
          <div className="text-center p-3 bg-green-50 rounded-lg">
            <p className="text-2xl font-bold text-green-600">{stats.premiums.paid}</p>
            <p className="text-sm text-gray-600">Paid</p>
          </div>
          <div className="text-center p-3 bg-yellow-50 rounded-lg">
            <p className="text-2xl font-bold text-yellow-600">{stats.premiums.pending}</p>
            <p className="text-sm text-gray-600">Pending</p>
          </div>
          <div className="text-center p-3 bg-red-50 rounded-lg">
            <p className="text-2xl font-bold text-red-600">{stats.premiums.overdue}</p>
            <p className="text-sm text-gray-600">Overdue</p>
          </div>
          <div className="text-center p-3 bg-purple-50 rounded-lg">
            <p className="text-2xl font-bold text-purple-600">{formatCurrency(stats.premiums.totalCollected)}</p>
            <p className="text-sm text-gray-600">Collected</p>
          </div>
        </div>
      </div>

      {/* Claims & Commissions Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Claims Statistics */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-orange-600" />
              <h2 className="text-xl font-semibold">Claims Processing</h2>
            </div>
            <span className={`flex items-center gap-1 text-sm font-medium ${stats.claims.recentChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {stats.claims.recentChange >= 0 ? <ArrowUpRight className="h-4 w-4" /> : <ArrowDownRight className="h-4 w-4" />}
              {Math.abs(stats.claims.recentChange)}%
            </span>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
              <span className="text-gray-600">Total Claims</span>
              <span className="font-bold text-gray-900">{stats.claims.total}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-yellow-50 rounded-lg">
              <span className="text-gray-600">Registered</span>
              <span className="font-bold text-yellow-600">{stats.claims.registered}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
              <span className="text-gray-600">In Process</span>
              <span className="font-bold text-blue-600">{stats.claims.assessed + stats.claims.approved}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
              <span className="text-gray-600">Settled</span>
              <span className="font-bold text-green-600">{stats.claims.settled}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
              <span className="text-gray-600">Total Paid</span>
              <span className="font-bold text-purple-600">{formatCurrency(stats.claims.totalAmount)}</span>
            </div>
          </div>
        </div>

        {/* Commission Statistics */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-purple-600" />
              <h2 className="text-xl font-semibold">Commission Tracking</h2>
            </div>
            <span className={`flex items-center gap-1 text-sm font-medium ${stats.commissions.recentChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {stats.commissions.recentChange >= 0 ? <ArrowUpRight className="h-4 w-4" /> : <ArrowDownRight className="h-4 w-4" />}
              {Math.abs(stats.commissions.recentChange)}%
            </span>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
              <span className="text-gray-600">Total Commissions</span>
              <span className="font-bold text-gray-900">{stats.commissions.total}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-yellow-50 rounded-lg">
              <span className="text-gray-600">Pending</span>
              <span className="font-bold text-yellow-600">{stats.commissions.pending}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
              <span className="text-gray-600">Approved</span>
              <span className="font-bold text-blue-600">{stats.commissions.approved}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
              <span className="text-gray-600">Paid</span>
              <span className="font-bold text-green-600">{stats.commissions.paid}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
              <span className="text-gray-600">Total Paid</span>
              <span className="font-bold text-purple-600">{formatCurrency(stats.commissions.totalAmount)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center gap-2 mb-4">
          <Clock className="h-5 w-5 text-gray-600" />
          <h2 className="text-xl font-semibold">Recent Activity</h2>
        </div>
        <div className="space-y-3">
          {recentActivity.length === 0 ? (
            <p className="text-center text-gray-500 py-8">No recent activity</p>
          ) : (
            recentActivity.map((activity) => (
              <div key={activity.id} className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div className={`p-2 rounded-lg ${getActivityColor(activity.type)}`}>
                  {getActivityIcon(activity.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-900 truncate">{activity.title}</p>
                  <p className="text-sm text-gray-600 truncate">{activity.description}</p>
                </div>
                <div className="text-right">
                  {activity.amount && (
                    <p className="font-semibold text-gray-900">{formatCurrency(activity.amount)}</p>
                  )}
                  <p className="text-xs text-gray-500">{formatDate(activity.timestamp)}</p>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Alert Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="h-5 w-5 text-red-600" />
            <h3 className="font-semibold text-red-900">Overdue Premiums</h3>
          </div>
          <p className="text-2xl font-bold text-red-600">{stats.premiums.overdue}</p>
          <p className="text-sm text-red-700">Require immediate attention</p>
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Clock className="h-5 w-5 text-yellow-600" />
            <h3 className="font-semibold text-yellow-900">Pending Claims</h3>
          </div>
          <p className="text-2xl font-bold text-yellow-600">{stats.claims.registered}</p>
          <p className="text-sm text-yellow-700">Awaiting assessment</p>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle className="h-5 w-5 text-blue-600" />
            <h3 className="font-semibold text-blue-900">Pending Commissions</h3>
          </div>
          <p className="text-2xl font-bold text-blue-600">{stats.commissions.pending}</p>
          <p className="text-sm text-blue-700">Awaiting approval</p>
        </div>
      </div>
    </div>
  );
}
