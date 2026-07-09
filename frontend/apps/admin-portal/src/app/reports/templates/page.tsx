"use client";

import { useState, useEffect } from "react";
import { 
  FileText, Search, Filter, Download, Eye, Calendar,
  TrendingUp, DollarSign, Users, AlertTriangle,
  Building, PieChart, BarChart3, FileSpreadsheet
} from "lucide-react";
import Link from "next/link";

interface ReportTemplate {
  id: number;
  report_code: string;
  report_name: string;
  report_description: string;
  category: string;
  sub_category: string;
  is_active: boolean;
  is_system: boolean;
  created_at: string;
}

export default function ReportTemplatesPage() {
  const [templates, setTemplates] = useState<ReportTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  const categories = [
    { value: "all", label: "All Reports", icon: FileText, color: "gray" },
    { value: "portfolio", label: "Portfolio", icon: PieChart, color: "blue" },
    { value: "collection", label: "Collection", icon: TrendingUp, color: "green" },
    { value: "risk", label: "Risk & NPA", icon: AlertTriangle, color: "red" },
    { value: "financial", label: "Financial", icon: DollarSign, color: "yellow" },
    { value: "regulatory", label: "Regulatory", icon: FileSpreadsheet, color: "purple" },
    { value: "operational", label: "Operational", icon: BarChart3, color: "indigo" },
    { value: "customer", label: "Customer", icon: Users, color: "pink" },
    { value: "treasury", label: "Treasury", icon: Building, color: "orange" },
  ];

  useEffect(() => {
    fetchTemplates();
  }, [page, selectedCategory, searchTerm]);

  const fetchTemplates = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("token");
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: "20",
        ...(selectedCategory !== "all" && { category: selectedCategory }),
        ...(searchTerm && { search: searchTerm })
      });

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/reports/templates?${params}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const result = await response.json();
        setTemplates(result.data.items || []);
        setTotal(result.data.total || 0);
      }
    } catch (error) {
      console.error("Error fetching templates:", error);
    } finally {
      setLoading(false);
    }
  };

  const generateReport = async (templateId: number) => {
    // Navigate to generate page with template ID
    window.location.href = `/reports/generate?template=${templateId}`;
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <Link href="/reports" className="text-blue-600 hover:text-blue-700 text-sm mb-2 inline-block">
          ← Back to Reports
        </Link>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Report Templates
        </h1>
        <p className="text-gray-600">
          Choose from 100+ pre-built reports covering all aspects of NBFC operations
        </p>
      </div>

      {/* Search and Filters */}
      <div className="mb-6 flex flex-col md:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
          <input
            type="text"
            placeholder="Search reports..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      {/* Category Filters */}
      <div className="mb-6 flex overflow-x-auto gap-2 pb-2">
        {categories.map((category) => {
          const Icon = category.icon;
          const isSelected = selectedCategory === category.value;
          return (
            <button
              key={category.value}
              onClick={() => setSelectedCategory(category.value)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg whitespace-nowrap transition-all ${
                isSelected
                  ? `bg-${category.color}-500 text-white shadow-md`
                  : "bg-white text-gray-700 border border-gray-300 hover:border-gray-400"
              }`}
            >
              <Icon className="h-4 w-4" />
              <span className="text-sm font-medium">{category.label}</span>
            </button>
          );
        })}
      </div>

      {/* Templates Grid */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading templates...</p>
        </div>
      ) : templates.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No reports found</h3>
          <p className="text-gray-600">Try adjusting your search or filters</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
            {templates.map((template) => (
              <div
                key={template.id}
                className="bg-white rounded-lg shadow border border-gray-200 hover:shadow-lg transition-shadow p-6"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                        template.category === 'portfolio' ? 'bg-blue-100 text-blue-700' :
                        template.category === 'collection' ? 'bg-green-100 text-green-700' :
                        template.category === 'risk' ? 'bg-red-100 text-red-700' :
                        template.category === 'financial' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {template.category}
                      </span>
                      {template.is_system && (
                        <span className="text-xs font-medium px-2 py-1 rounded-full bg-purple-100 text-purple-700">
                          System
                        </span>
                      )}
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {template.report_name}
                    </h3>
                    <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                      {template.report_description}
                    </p>
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => generateReport(template.id)}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Download className="h-4 w-4" />
                    <span className="text-sm font-medium">Generate</span>
                  </button>
                  <Link
                    href={`/reports/templates/${template.id}`}
                    className="flex items-center justify-center px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <Eye className="h-4 w-4" />
                  </Link>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {total > 20 && (
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-600">
                Showing {((page - 1) * 20) + 1} to {Math.min(page * 20, total)} of {total} reports
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage(page + 1)}
                  disabled={page * 20 >= total}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {/* Featured Reports */}
      <div className="mt-12">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Most Popular Reports</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[
            { name: "Portfolio Summary", runs: 1234, icon: PieChart, color: "blue" },
            { name: "Collection Efficiency", runs: 987, icon: TrendingUp, color: "green" },
            { name: "NPA Analysis", runs: 756, icon: AlertTriangle, color: "red" },
            { name: "Cash Position", runs: 654, icon: DollarSign, color: "yellow" },
          ].map((report, index) => (
            <div key={index} className="bg-white p-4 rounded-lg shadow border border-gray-200">
              <div className={`w-10 h-10 rounded-lg bg-${report.color}-100 flex items-center justify-center mb-3`}>
                <report.icon className={`h-5 w-5 text-${report.color}-600`} />
              </div>
              <h4 className="font-semibold text-gray-900 mb-1">{report.name}</h4>
              <p className="text-sm text-gray-600">{report.runs.toLocaleString()} runs this month</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
