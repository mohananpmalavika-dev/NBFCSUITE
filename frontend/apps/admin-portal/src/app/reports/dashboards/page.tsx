"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  Layout, TrendingUp, DollarSign, Users, AlertTriangle,
  Building, Activity, BarChart3, PieChart, ArrowUp, ArrowDown,
  Eye, Plus, RefreshCw
} from "lucide-react";

export default function DashboardsPage() {
  const [loading, setLoading] = useState(false);
  const [executiveData, setExecutiveData] = useState<any>(null);

  useEffect(() => {
    fetchExecutiveDashboard();
  }, []);

  const fetchExecutiveDashboard = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/dashboards/executive/summary`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const result = await response.json();
        setExecutiveData(result.data);
      }
    } catch (error) {
      console.error("Error fetching dashboard:", error);
    } finally {
      setLoading(false);
    }
  };

  const dashboards = [
    {
      id: 1,
      name: "Executive Dashboard",
      description: "High-level overview for CXO",
      type: "executive",
      icon: TrendingUp,
      color: "blue",
      widgets: 8,
      isDefault: true
    },
    {
      id: 2,
      name: "Operations Dashboard",
      description: "Daily operations monitoring",
      type: "operations",
      icon: Activity,
      color: "green",
      widgets: 12,
      isDefault: false
    },
    {
      id: 3,
      name: "Risk Management",
      description: "Portfolio risk and NPA tracking",
      type: "risk",
      icon: AlertTriangle,
      color: "red",
      widgets: 10,
      isDefault: false
    },
    {
      id: 4,
      name: "Collection Dashboard",
      description: "Collection efficiency and overdue",
      type: "collection",
      icon: DollarSign,
      color: "yellow",
      widgets: 9,
      isDefault: false
    },
    {
      id: 5,
      name: "Branch Performance",
      description: "Branch-wise metrics",
      type: "branch",
      icon: Building,
      color: "purple",
      widgets: 11,
      isDefault: false
    },
    {
      id: 6,
      name: "Treasury Dashboard",
      description: "Liquidity and cash position",
      type: "treasury",
      icon: BarChart3,
      color: "indigo",
      widgets: 7,
      isDefault: false
    }
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <Link href="/reports" className="text-blue-600 hover:text-blue-700 text-sm mb-2 inline-block">
            ← Back to Reports
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Executive Dashboards
          </h1>
          <p className="text-gray-600">
            Real-time dashboards with interactive KPIs and visualizations
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          <Plus className="h-4 w-4" />
          Create Custom Dashboard
        </button>
      </div>

      {/* Executive Summary (Real-time Data) */}
      {executiveData && (
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Executive Summary</h2>
            <button 
              onClick={fetchExecutiveDashboard}
              className="flex items-center gap-2 px-3 py-1 text-sm text-gray-600 hover:text-gray-900"
            >
              <RefreshCw className="h-4 w-4" />
              Refresh
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {/* Portfolio Metrics */}
            <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center">
                  <PieChart className="h-6 w-6 text-blue-600" />
                </div>
                <span className="flex items-center text-green-600 text-sm font-medium">
                  <ArrowUp className="h-4 w-4" />
                  12%
                </span>
              </div>
              <h3 className="text-sm font-medium text-gray-600 mb-1">Total Portfolio</h3>
              <p className="text-2xl font-bold text-gray-900">
                ₹{(executiveData.portfolio?.outstanding / 10000000).toFixed(2)}Cr
              </p>
              <p className="text-xs text-gray-500 mt-2">
                {executiveData.portfolio?.total_loans} active loans
              </p>
            </div>

            {/* Collection Efficiency */}
            <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-lg bg-green-100 flex items-center justify-center">
                  <TrendingUp className="h-6 w-6 text-green-600" />
                </div>
                <span className="flex items-center text-green-600 text-sm font-medium">
                  <ArrowUp className="h-4 w-4" />
                  2.5%
                </span>
              </div>
              <h3 className="text-sm font-medium text-gray-600 mb-1">Collection Efficiency</h3>
              <p className="text-2xl font-bold text-gray-900">
                {executiveData.collections?.collection_efficiency}%
              </p>
              <p className="text-xs text-gray-500 mt-2">
                Target: 95%
              </p>
            </div>

            {/* NPA Ratio */}
            <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-lg bg-red-100 flex items-center justify-center">
                  <AlertTriangle className="h-6 w-6 text-red-600" />
                </div>
                <span className="flex items-center text-red-600 text-sm font-medium">
                  <ArrowDown className="h-4 w-4" />
                  0.3%
                </span>
              </div>
              <h3 className="text-sm font-medium text-gray-600 mb-1">NPA Ratio</h3>
              <p className="text-2xl font-bold text-gray-900">
                {executiveData.risk?.npa_ratio}%
              </p>
              <p className="text-xs text-gray-500 mt-2">
                Industry avg: 3.2%
              </p>
            </div>

            {/* Total Customers */}
            <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-lg bg-purple-100 flex items-center justify-center">
                  <Users className="h-6 w-6 text-purple-600" />
                </div>
                <span className="flex items-center text-green-600 text-sm font-medium">
                  <ArrowUp className="h-4 w-4" />
                  8%
                </span>
              </div>
              <h3 className="text-sm font-medium text-gray-600 mb-1">Total Customers</h3>
              <p className="text-2xl font-bold text-gray-900">
                {executiveData.customers?.total_customers.toLocaleString()}
              </p>
              <p className="text-xs text-gray-500 mt-2">
                {executiveData.customers?.new_this_month} new this month
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Available Dashboards */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Available Dashboards</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {dashboards.map((dashboard) => {
            const Icon = dashboard.icon;
            return (
              <div
                key={dashboard.id}
                className="bg-white rounded-lg shadow border border-gray-200 hover:shadow-lg transition-shadow p-6"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className={`w-12 h-12 rounded-lg bg-${dashboard.color}-100 flex items-center justify-center`}>
                    <Icon className={`h-6 w-6 text-${dashboard.color}-600`} />
                  </div>
                  {dashboard.isDefault && (
                    <span className="text-xs font-medium px-2 py-1 rounded-full bg-blue-100 text-blue-700">
                      Default
                    </span>
                  )}
                </div>
                
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {dashboard.name}
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  {dashboard.description}
                </p>
                
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm text-gray-500">
                    {dashboard.widgets} widgets
                  </span>
                  <span className={`text-xs font-medium px-2 py-1 rounded-full bg-${dashboard.color}-100 text-${dashboard.color}-700`}>
                    {dashboard.type}
                  </span>
                </div>

                <div className="flex gap-2">
                  <Link
                    href={`/reports/dashboards/${dashboard.id}`}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Eye className="h-4 w-4" />
                    <span className="text-sm font-medium">View Dashboard</span>
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="mt-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Dashboard Views</h2>
        <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dashboard</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Viewed By</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Duration</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {[
                { dashboard: "Executive Dashboard", user: "Rajesh Kumar", time: "5 mins ago", duration: "12 mins" },
                { dashboard: "Operations Dashboard", user: "Priya Sharma", time: "15 mins ago", duration: "8 mins" },
                { dashboard: "Risk Management", user: "Amit Patel", time: "1 hour ago", duration: "20 mins" },
                { dashboard: "Collection Dashboard", user: "Sneha Desai", time: "2 hours ago", duration: "15 mins" },
              ].map((activity, index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {activity.dashboard}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {activity.user}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {activity.time}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {activity.duration}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
