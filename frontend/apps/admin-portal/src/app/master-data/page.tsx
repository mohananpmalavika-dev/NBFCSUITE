"use client";

import { useState } from "react";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { 
  Database, 
  Globe, 
  Building2, 
  MapPin, 
  FileText,
  Briefcase,
  Factory,
  ChevronRight,
  Home
} from "lucide-react";
import Link from "next/link";

export default function MasterDataPage() {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const categories = [
    {
      id: "geography",
      name: "Geography",
      icon: Globe,
      description: "Countries, States, Cities, Pincodes",
      count: "36+ States, 130+ Cities",
      color: "bg-blue-500",
      items: [
        { name: "States & UTs", count: 36, route: "/master-data/states" },
        { name: "Cities", count: 130, route: "/master-data/cities" },
        { name: "Pincodes", count: "Sample", route: "/master-data/pincodes" }
      ]
    },
    {
      id: "banking",
      name: "Banking",
      icon: Building2,
      description: "Banks, Branches, IFSC Codes",
      count: "25+ Banks, IFSC Database",
      color: "bg-green-500",
      items: [
        { name: "Banks", count: 25, route: "/master-data/banks" },
        { name: "Bank Branches", count: "Sample", route: "/master-data/bank-branches" },
        { name: "IFSC Lookup", count: "-", route: "/master-data/ifsc-lookup" }
      ]
    },
    {
      id: "financial",
      name: "Financial",
      icon: Database,
      description: "Loan Products, Interest Rates, Currency",
      count: "10+ Loan Products",
      color: "bg-purple-500",
      items: [
        { name: "Loan Products", count: 10, route: "/master-data/loan-products" }
      ]
    },
    {
      id: "documents",
      name: "Documents",
      icon: FileText,
      description: "Document Types, Templates",
      count: "20+ Document Types",
      color: "bg-orange-500",
      items: [
        { name: "Document Types", count: 20, route: "/master-data/documents" },
        { name: "Mandatory Docs", count: 8, route: "/master-data/documents?mandatory=true" }
      ]
    },
    {
      id: "occupations",
      name: "Occupations",
      icon: Briefcase,
      description: "Occupation Types, Categories",
      count: "17 Occupations",
      color: "bg-cyan-500",
      items: [
        { name: "All Occupations", count: 17, route: "/master-data/occupations" },
        { name: "Salaried", count: 5, route: "/master-data/occupations?category=Salaried" },
        { name: "Self-Employed", count: 6, route: "/master-data/occupations?category=Self-Employed" }
      ]
    },
    {
      id: "industries",
      name: "Industries",
      icon: Factory,
      description: "Industry Categories, Sectors",
      count: "15 Industries",
      color: "bg-pink-500",
      items: [
        { name: "All Industries", count: 15, route: "/master-data/industries" },
        { name: "Manufacturing", count: 4, route: "/master-data/industries?sector=Manufacturing" },
        { name: "Services", count: 6, route: "/master-data/industries?sector=Services" }
      ]
    },
    {
      id: "others",
      name: "Others",
      icon: MapPin,
      description: "Holidays, Loan Purposes, Relationships",
      count: "Multiple Categories",
      color: "bg-indigo-500",
      items: [
        { name: "Holidays (2026)", count: 19, route: "/master-data/holidays" }
      ]
    }
  ];

  return (
    <DashboardLayout>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            {/* Breadcrumb */}
            <div className="flex items-center gap-2 text-sm text-gray-600 mb-4">
              <Link href="/dashboard" className="hover:text-blue-600 flex items-center gap-1">
                <Home className="w-4 h-4" />
                Dashboard
              </Link>
              <ChevronRight className="w-4 h-4" />
              <span className="text-gray-900 font-medium">Master Data</span>
            </div>
            
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Database className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Master Data Management</h1>
                <p className="text-sm text-gray-600">
                  Manage reference data for your NBFC operations
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Bar */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold">36+</div>
              <div className="text-sm text-blue-100">States & UTs</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold">25+</div>
              <div className="text-sm text-blue-100">Banks</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold">130+</div>
              <div className="text-sm text-blue-100">Cities</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold">500+</div>
              <div className="text-sm text-blue-100">Total Records</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Category Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {categories.map((category) => {
            const Icon = category.icon;
            const isExpanded = selectedCategory === category.id;

            return (
              <div
                key={category.id}
                className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
              >
                {/* Category Header */}
                <button
                  onClick={() => setSelectedCategory(isExpanded ? null : category.id)}
                  className="w-full p-6 text-left hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start gap-4">
                    <div className={`w-12 h-12 ${category.color} rounded-lg flex items-center justify-center flex-shrink-0`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {category.name}
                        </h3>
                        <ChevronRight 
                          className={`w-5 h-5 text-gray-400 transition-transform ${
                            isExpanded ? 'rotate-90' : ''
                          }`}
                        />
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        {category.description}
                      </p>
                      <p className="text-xs text-gray-500 mt-2 font-medium">
                        {category.count}
                      </p>
                    </div>
                  </div>
                </button>

                {/* Expanded Items */}
                {isExpanded && (
                  <div className="border-t border-gray-200 bg-gray-50">
                    <div className="p-4 space-y-2">
                      {category.items.map((item) => (
                        <a
                          key={item.name}
                          href={item.route}
                          className="flex items-center justify-between p-3 bg-white rounded-lg hover:bg-blue-50 hover:border-blue-200 border border-transparent transition-colors"
                        >
                          <span className="text-sm font-medium text-gray-700">
                            {item.name}
                          </span>
                          <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                            {item.count}
                          </span>
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Quick Actions */}
        <div className="mt-8 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="flex items-center gap-3 p-4 border border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors">
              <Database className="w-5 h-5 text-blue-600" />
              <span className="text-sm font-medium text-gray-700">View All Data</span>
            </button>
            <button className="flex items-center gap-3 p-4 border border-gray-300 rounded-lg hover:border-green-500 hover:bg-green-50 transition-colors">
              <FileText className="w-5 h-5 text-green-600" />
              <span className="text-sm font-medium text-gray-700">Import Data</span>
            </button>
            <button className="flex items-center gap-3 p-4 border border-gray-300 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-colors">
              <MapPin className="w-5 h-5 text-purple-600" />
              <span className="text-sm font-medium text-gray-700">Export Data</span>
            </button>
          </div>
        </div>

        {/* Info Box */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex gap-3">
            <div className="flex-shrink-0">
              <svg className="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h3 className="text-sm font-medium text-blue-900">Master Data Information</h3>
              <p className="mt-1 text-sm text-blue-700">
                Master data is pre-loaded for India including all states, major banks with IFSC codes, 
                loan products, document types, and more. You can add, edit, or import additional data as needed.
              </p>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
