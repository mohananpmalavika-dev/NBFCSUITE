"use client";

import { useState } from "react";
import Link from "next/link";
import {
  FileText,
  BarChart3,
  Layout,
  Brain,
  Plus,
  TrendingUp,
  FileSpreadsheet,
  PieChart,
  Activity,
  Calendar,
  Download,
  Filter
} from "lucide-react";

export default function ReportsPage() {
  const [stats] = useState({
    totalReports: 124,
    reportsGenerated: 1847,
    dashboards: 12,
    mlModels: 8
  });

  const quickAccessReports = [
    {
      id: 1,
      name: "Portfolio Summary",
      category: "Portfolio",
      icon: PieChart,
      color: "bg-blue-500",
      lastRun: "2 hours ago"
    },
    {
      id: 2,
      name: "Collection Efficiency",
      category: "Collection",
      icon: TrendingUp,
      color: "bg-green-500",
      lastRun: "Today 9:00 AM"
    },
    {
      id: 3,
      name: "NPA Analysis",
      category: "Risk",
      icon: Activity,
      color: "bg-red-500",
      lastRun: "Yesterday"
    },
    {
      id: 4,
      name: "Disbursement Report",
      category: "Operational",
      icon: FileSpreadsheet,
      color: "bg-purple-500",
      lastRun: "3 hours ago"
    }
  ];

  const modules = [
    {
      title: "Report Templates",
      description: "Access 100+ pre-built reports across all modules",
      icon: FileText,
      href: "/reports/templates",
      color: "bg-blue-500",
      count: "124 Reports"
    },
    {
      title: "Generate Reports",
      description: "Generate reports with custom parameters and filters",
      icon: FileSpreadsheet,
      href: "/reports/generate",
      color: "bg-green-500",
      count: "Quick Access"
    },
    {
      title: "Custom Report Builder",
      description: "Build custom reports with drag-and-drop interface",
      icon: Plus,
      href: "/reports/builder",
      color: "bg-purple-500",
      count: "Drag & Drop"
    },
    {
      title: "Executive Dashboards",
      description: "Real-time dashboards with KPIs and visualizations",
      icon: Layout,
      href: "/reports/dashboards",
      color: "bg-orange-500",
      count: "12 Dashboards"
    },
    {
      title: "Predictive Analytics",
      description: "ML-powered predictions for risk, churn, and more",
      icon: Brain,
      href: "/reports/analytics",
      color: "bg-pink-500",
      count: "8 Models"
    },
    {
      title: "Scheduled Reports",
      description: "Automate report generation and delivery",
      icon: Calendar,
      href: "/reports/scheduled",
      color: "bg-indigo-500",
      count: "Automation"
    },
    {
      title: "Report History",
      description: "View and download previously generated reports",
      icon: Download,
      href: "/reports/history",
      color: "bg-gray-500",
      count: "1,847 Reports"
    },
    {
      title: "Report Analytics",
      description: "Track report usage and performance metrics",
      icon: BarChart3,
      href: "/reports/usage",
      color: "bg-teal-500",
      count: "Insights"
    }
  ];

  const reportCategories = [
    { name: "Portfolio Reports", count: 20, color: "bg-blue-100 text-blue-700" },
    { name: "Collection Reports", count: 15, color: "bg-green-100 text-green-700" },
    { name: "Risk & NPA", count: 12, color: "bg-red-100 text-red-700" },
    { name: "Financial Reports", count: 18, color: "bg-yellow-100 text-yellow-700" },
    { name: "Regulatory & Compliance", count: 15, color: "bg-purple-100 text-purple-700" },
    { name: "Operational", count: 10, color: "bg-indigo-100 text-indigo-700" },
    { name: "Customer", count: 8, color: "bg-pink-100 text-pink-700" },
    { name: "Treasury", count: 8, color: "bg-orange-100 text-orange-700" },
    { name: "Deposit", count: 6, color: "bg-teal-100 text-teal-700" },
    { name: "Branch & HR", count: 10, color: "bg-gray-100 text-gray-700" }
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Reporting & Analytics
        </h1>
        <p className="text-gray-600">
          Comprehensive reporting suite with 100+ pre-built reports, custom builder, dashboards, and AI-powered analytics
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Reports</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalReports}</p>
            </div>
            <FileText className="h-10 w-10 text-blue-500" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Reports Generated</p>
              <p className="text-2xl font-bold text-gray-900">{stats.reportsGenerated.toLocaleString()}</p>
            </div>
            <BarChart3 className="h-10 w-10 text-green-500" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Dashboards</p>
              <p className="text-2xl font-bold text-gray-900">{stats.dashboards}</p>
            </div>
            <Layout className="h-10 w-10 text-purple-500" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">ML Models</p>
              <p className="text-2xl font-bold text-gray-900">{stats.mlModels}</p>
            </div>
            <Brain className="h-10 w-10 text-pink-500" />
          </div>
        </div>
      </div>

      {/* Quick Access Reports */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Access Reports</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {quickAccessReports.map((report) => (
            <Link
              key={report.id}
              href={`/reports/templates/${report.id}`}
              className="bg-white p-4 rounded-lg shadow border border-gray-200 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-3">
                <div className={`p-2 rounded-lg ${report.color} bg-opacity-10`}>
                  <report.icon className={`h-6 w-6 ${report.color.replace('bg-', 'text-')}`} />
                </div>
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">{report.name}</h3>
              <p className="text-sm text-gray-600 mb-2">{report.category}</p>
              <p className="text-xs text-gray-500">Last run: {report.lastRun}</p>
            </Link>
          ))}
        </div>
      </div>

      {/* Main Modules */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Reporting Modules</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {modules.map((module, index) => (
            <Link
              key={index}
              href={module.href}
              className="bg-white p-6 rounded-lg shadow border border-gray-200 hover:shadow-lg transition-all hover:scale-105"
            >
              <div className={`w-12 h-12 rounded-lg ${module.color} bg-opacity-10 flex items-center justify-center mb-4`}>
                <module.icon className={`h-6 w-6 ${module.color.replace('bg-', 'text-')}`} />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {module.title}
              </h3>
              <p className="text-sm text-gray-600 mb-3">
                {module.description}
              </p>
              <span className={`inline-block text-xs font-medium px-3 py-1 rounded-full ${module.color} bg-opacity-10 ${module.color.replace('bg-', 'text-')}`}>
                {module.count}
              </span>
            </Link>
          ))}
        </div>
      </div>

      {/* Report Categories */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Report Categories</h2>
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {reportCategories.map((category, index) => (
              <Link
                key={index}
                href={`/reports/templates?category=${category.name.toLowerCase().replace(/ /g, '_')}`}
                className="flex flex-col items-center p-4 rounded-lg border border-gray-200 hover:border-blue-500 hover:shadow-md transition-all"
              >
                <span className={`text-sm font-medium px-3 py-1 rounded-full ${category.color} mb-2`}>
                  {category.count} reports
                </span>
                <p className="text-sm text-center text-gray-700">{category.name}</p>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
