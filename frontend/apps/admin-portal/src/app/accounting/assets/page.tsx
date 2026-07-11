"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { 
  Package,
  TrendingDown,
  Wrench,
  ArrowRightLeft,
  ClipboardCheck,
  Plus,
  DollarSign,
  BarChart3,
  AlertCircle,
  CheckCircle,
  Clock,
  MapPin
} from "lucide-react";

interface AssetStats {
  total_assets: number;
  active_assets: number;
  total_cost: number;
  total_depreciation: number;
  total_net_book_value: number;
  assets_by_category: Array<{
    category: string;
    count: number;
    total_cost: number;
  }>;
  assets_by_status: Array<{
    status: string;
    count: number;
  }>;
}

interface RecentActivity {
  id: number;
  type: string;
  asset_code: string;
  asset_name: string;
  description: string;
  date: string;
  status: string;
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
  trend?: string;
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
            <p className="mt-2 text-xs text-green-600 font-medium">{trend}</p>
          )}
        </div>
        <div className={`p-3 rounded-full ${color}`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
      </div>
    </div>
  );
}

function QuickActionCard({ 
  title, 
  description,
  icon: Icon,
  color,
  href
}: {
  title: string;
  description: string;
  icon: any;
  color: string;
  href: string;
}) {
  return (
    <Link
      href={href}
      className="block bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
    >
      <div className="flex items-start">
        <div className={`p-3 rounded-lg ${color}`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
        <div className="ml-4 flex-1">
          <h3 className="text-base font-semibold text-gray-900">{title}</h3>
          <p className="mt-1 text-sm text-gray-600">{description}</p>
        </div>
      </div>
    </Link>
  );
}

export default function FixedAssetsDashboard() {
  const [stats, setStats] = useState<AssetStats | null>(null);
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch asset summary
      const response = await fetch('/api/v1/fixed-assets/assets/summary/statistics');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }

      // Mock recent activity
      const mockActivity: RecentActivity[] = [
        {
          id: 1,
          type: "depreciation",
          asset_code: "AST000123",
          asset_name: "Dell Laptop - i7",
          description: "Monthly depreciation posted",
          date: "2024-01-05",
          status: "completed"
        },
        {
          id: 2,
          type: "maintenance",
          asset_code: "AST000045",
          asset_name: "Toyota Innova",
          description: "Preventive maintenance scheduled",
          date: "2024-01-04",
          status: "scheduled"
        },
        {
          id: 3,
          type: "transfer",
          asset_code: "AST000098",
          asset_name: "HP Printer",
          description: "Transfer to Mumbai Branch approved",
          date: "2024-01-03",
          status: "in-transit"
        },
        {
          id: 4,
          type: "verification",
          asset_code: "AST000234",
          asset_name: "Office Furniture Set",
          description: "Physical verification completed",
          date: "2024-01-02",
          status: "found"
        }
      ];
      setRecentActivity(mockActivity);

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

  const formatCurrency = (value: number) => {
    return `₹${value.toLocaleString("en-IN", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-gray-900">Fixed Asset Management</h2>
            <p className="mt-1 text-sm text-gray-500">
              Complete asset lifecycle management with depreciation, maintenance & verification
            </p>
          </div>
          <Link
            href="/accounting/assets/new"
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="h-5 w-5 mr-2" />
            Add New Asset
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Assets"
          value={stats?.total_assets || 0}
          subtitle={`${stats?.active_assets || 0} active`}
          icon={Package}
          color="bg-blue-600"
        />
        <StatCard
          title="Gross Book Value"
          value={formatCurrency(stats?.total_cost || 0)}
          icon={DollarSign}
          color="bg-green-600"
        />
        <StatCard
          title="Accumulated Depreciation"
          value={formatCurrency(stats?.total_depreciation || 0)}
          icon={TrendingDown}
          color="bg-red-600"
        />
        <StatCard
          title="Net Book Value"
          value={formatCurrency(stats?.total_net_book_value || 0)}
          subtitle="Current asset value"
          icon={BarChart3}
          color="bg-purple-600"
        />
      </div>

      {/* Quick Actions Grid */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <QuickActionCard
            title="Asset Register"
            description="View and manage all fixed assets"
            icon={Package}
            color="bg-blue-600"
            href="/accounting/assets/list"
          />
          <QuickActionCard
            title="Run Depreciation"
            description="Calculate and post depreciation"
            icon={TrendingDown}
            color="bg-purple-600"
            href="/accounting/assets/depreciation"
          />
          <QuickActionCard
            title="Maintenance"
            description="Track asset maintenance & repairs"
            icon={Wrench}
            color="bg-orange-600"
            href="/accounting/assets/maintenance"
          />
          <QuickActionCard
            title="Transfers"
            description="Manage asset transfers & movements"
            icon={ArrowRightLeft}
            color="bg-teal-600"
            href="/accounting/assets/transfers"
          />
          <QuickActionCard
            title="Physical Verification"
            description="Conduct physical asset verification"
            icon={ClipboardCheck}
            color="bg-green-600"
            href="/accounting/assets/verification"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
          </div>
          <div className="divide-y divide-gray-200">
            {recentActivity.map((activity) => (
              <div key={activity.id} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    {activity.type === "depreciation" && (
                      <div className="p-2 bg-purple-100 rounded-lg">
                        <TrendingDown className="h-5 w-5 text-purple-600" />
                      </div>
                    )}
                    {activity.type === "maintenance" && (
                      <div className="p-2 bg-orange-100 rounded-lg">
                        <Wrench className="h-5 w-5 text-orange-600" />
                      </div>
                    )}
                    {activity.type === "transfer" && (
                      <div className="p-2 bg-teal-100 rounded-lg">
                        <ArrowRightLeft className="h-5 w-5 text-teal-600" />
                      </div>
                    )}
                    {activity.type === "verification" && (
                      <div className="p-2 bg-green-100 rounded-lg">
                        <ClipboardCheck className="h-5 w-5 text-green-600" />
                      </div>
                    )}
                  </div>
                  <div className="ml-4 flex-1">
                    <div className="flex items-center">
                      <p className="text-sm font-medium text-gray-900">
                        {activity.asset_code}
                      </p>
                      <span className="ml-2 text-sm text-gray-500">•</span>
                      <p className="ml-2 text-sm text-gray-600">{activity.asset_name}</p>
                    </div>
                    <p className="mt-1 text-sm text-gray-600">{activity.description}</p>
                    <div className="mt-2 flex items-center">
                      <Clock className="h-4 w-4 text-gray-400" />
                      <span className="ml-1 text-xs text-gray-500">
                        {new Date(activity.date).toLocaleDateString("en-IN", {
                          year: "numeric",
                          month: "short",
                          day: "numeric",
                        })}
                      </span>
                      <span className={`ml-3 px-2 py-0.5 text-xs rounded-full ${
                        activity.status === "completed" ? "bg-green-100 text-green-800" :
                        activity.status === "scheduled" ? "bg-blue-100 text-blue-800" :
                        activity.status === "in-transit" ? "bg-yellow-100 text-yellow-800" :
                        "bg-gray-100 text-gray-800"
                      }`}>
                        {activity.status}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="px-6 py-4 border-t border-gray-200">
            <Link
              href="/accounting/assets/activity"
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              View All Activity →
            </Link>
          </div>
        </div>

        {/* Assets by Category */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Assets by Category</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {stats?.assets_by_category?.slice(0, 6).map((category, index) => (
                <div key={index}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700 capitalize">
                      {category.category.replace(/_/g, " ")}
                    </span>
                    <span className="text-sm text-gray-600">{category.count}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{
                        width: `${(category.count / (stats?.total_assets || 1)) * 100}%`,
                      }}
                    ></div>
                  </div>
                  <div className="mt-1 text-xs text-gray-500">
                    {formatCurrency(category.total_cost)}
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Assets by Status */}
          <div className="px-6 py-4 border-t border-gray-200">
            <h4 className="text-sm font-semibold text-gray-900 mb-3">By Status</h4>
            <div className="space-y-2">
              {stats?.assets_by_status?.map((status, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center">
                    {status.status === "active" && (
                      <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    )}
                    {status.status === "in_maintenance" && (
                      <Wrench className="h-4 w-4 text-orange-500 mr-2" />
                    )}
                    {status.status === "disposed" && (
                      <AlertCircle className="h-4 w-4 text-red-500 mr-2" />
                    )}
                    <span className="text-sm text-gray-700 capitalize">
                      {status.status.replace(/_/g, " ")}
                    </span>
                  </div>
                  <span className="text-sm font-medium text-gray-900">{status.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Upcoming Tasks */}
      <div className="mt-8 bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Upcoming Tasks</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-start p-4 bg-blue-50 rounded-lg">
              <Clock className="h-5 w-5 text-blue-600 mt-0.5" />
              <div className="ml-3">
                <p className="text-sm font-medium text-blue-900">
                  Monthly Depreciation Due
                </p>
                <p className="mt-1 text-xs text-blue-700">
                  Calculate depreciation for January 2024
                </p>
                <Link
                  href="/accounting/assets/depreciation"
                  className="mt-2 text-xs text-blue-600 hover:text-blue-700 font-medium inline-block"
                >
                  Run Now →
                </Link>
              </div>
            </div>

            <div className="flex items-start p-4 bg-orange-50 rounded-lg">
              <Wrench className="h-5 w-5 text-orange-600 mt-0.5" />
              <div className="ml-3">
                <p className="text-sm font-medium text-orange-900">
                  5 Maintenance Scheduled
                </p>
                <p className="mt-1 text-xs text-orange-700">
                  Preventive maintenance due this week
                </p>
                <Link
                  href="/accounting/assets/maintenance"
                  className="mt-2 text-xs text-orange-600 hover:text-orange-700 font-medium inline-block"
                >
                  View Schedule →
                </Link>
              </div>
            </div>

            <div className="flex items-start p-4 bg-green-50 rounded-lg">
              <ClipboardCheck className="h-5 w-5 text-green-600 mt-0.5" />
              <div className="ml-3">
                <p className="text-sm font-medium text-green-900">
                  Annual Verification Pending
                </p>
                <p className="mt-1 text-xs text-green-700">
                  45 assets pending verification
                </p>
                <Link
                  href="/accounting/assets/verification"
                  className="mt-2 text-xs text-green-600 hover:text-green-700 font-medium inline-block"
                >
                  Start Verification →
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
