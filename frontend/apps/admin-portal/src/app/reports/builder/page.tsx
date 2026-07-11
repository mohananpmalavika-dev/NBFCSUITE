"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  Database, Plus, Filter, BarChart3, Table, PieChart,
  LineChart, Settings, Save, Play, X
} from "lucide-react";

interface DataSource {
  table: string;
  label: string;
  fields: Array<{
    name: string;
    label: string;
    type: string;
  }>;
}

export default function ReportBuilderPage() {
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [selectedDataSource, setSelectedDataSource] = useState<string>("");
  const [selectedFields, setSelectedFields] = useState<string[]>([]);
  const [filters, setFilters] = useState<any[]>([]);
  const [groupBy, setGroupBy] = useState<string[]>([]);
  const [aggregations, setAggregations] = useState<any[]>([]);
  const [visualizationType, setVisualizationType] = useState<string>("table");
  const [reportName, setReportName] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchDataSources();
  }, []);

  const fetchDataSources = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/reports/builder/datasources`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const result = await response.json();
        setDataSources(result.data || []);
      }
    } catch (error) {
      console.error("Error fetching data sources:", error);
    }
  };

  const selectedDataSourceObj = dataSources.find(ds => ds.table === selectedDataSource);

  const toggleField = (fieldName: string) => {
    setSelectedFields(prev =>
      prev.includes(fieldName)
        ? prev.filter(f => f !== fieldName)
        : [...prev, fieldName]
    );
  };

  const addFilter = () => {
    setFilters([...filters, { field: "", operator: "equals", value: "" }]);
  };

  const removeFilter = (index: number) => {
    setFilters(filters.filter((_, i) => i !== index));
  };

  const addAggregation = () => {
    setAggregations([...aggregations, { field: "", function: "COUNT" }]);
  };

  const saveReport = async () => {
    if (!reportName || !selectedDataSource || selectedFields.length === 0) {
      alert("Please provide report name, select data source and at least one field");
      return;
    }

    setSaving(true);
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/reports/builder`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            report_name: reportName,
            data_sources: { table: selectedDataSource },
            selected_fields: selectedFields.reduce((acc, field) => {
              acc[field] = { label: field };
              return acc;
            }, {} as any),
            filters: filters.length > 0 ? filters : null,
            grouping: groupBy.length > 0 ? groupBy : null,
            aggregations: aggregations.length > 0 ? aggregations : null,
            visualization_type: visualizationType,
            is_public: false
          }),
        }
      );

      if (response.ok) {
        alert("Report saved successfully!");
        // Reset form or redirect
        setReportName("");
        setSelectedFields([]);
        setFilters([]);
        setGroupBy([]);
        setAggregations([]);
      } else {
        const error = await response.json();
        alert(`Error: ${error.error?.message || "Failed to save report"}`);
      }
    } catch (error) {
      console.error("Error saving report:", error);
      alert("Failed to save report");
    } finally {
      setSaving(false);
    }
  };

  const visualizations = [
    { value: "table", label: "Table", icon: Table },
    { value: "bar_chart", label: "Bar Chart", icon: BarChart3 },
    { value: "line_chart", label: "Line Chart", icon: LineChart },
    { value: "pie_chart", label: "Pie Chart", icon: PieChart },
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
            Custom Report Builder
          </h1>
          <p className="text-gray-600">
            Build custom reports with drag-and-drop interface - no SQL required
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={saveReport}
            disabled={saving}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            <Save className="h-4 w-4" />
            {saving ? "Saving..." : "Save Report"}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Panel - Configuration */}
        <div className="lg:col-span-2 space-y-6">
          {/* Report Name */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Report Details</h3>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Report Name *
              </label>
              <input
                type="text"
                value={reportName}
                onChange={(e) => setReportName(e.target.value)}
                placeholder="Enter report name..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          {/* Data Source Selection */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Database className="h-5 w-5" />
              1. Select Data Source
            </h3>
            <select
              value={selectedDataSource}
              onChange={(e) => {
                setSelectedDataSource(e.target.value);
                setSelectedFields([]);
              }}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Choose a data source...</option>
              {dataSources.map((ds) => (
                <option key={ds.table} value={ds.table}>
                  {ds.label}
                </option>
              ))}
            </select>
          </div>

          {/* Field Selection */}
          {selectedDataSourceObj && (
            <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                2. Select Fields
              </h3>
              <div className="grid grid-cols-2 gap-2">
                {selectedDataSourceObj.fields.map((field) => (
                  <label
                    key={field.name}
                    className="flex items-center gap-2 p-3 rounded border border-gray-200 hover:bg-gray-50 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={selectedFields.includes(field.name)}
                      onChange={() => toggleField(field.name)}
                      className="rounded text-blue-600"
                    />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{field.label}</p>
                      <p className="text-xs text-gray-500">{field.type}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Filters */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <Filter className="h-5 w-5" />
                3. Add Filters (Optional)
              </h3>
              <button
                onClick={addFilter}
                className="flex items-center gap-1 px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded"
              >
                <Plus className="h-4 w-4" />
                Add Filter
              </button>
            </div>
            {filters.length === 0 ? (
              <p className="text-sm text-gray-500">No filters added</p>
            ) : (
              <div className="space-y-2">
                {filters.map((filter, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <select className="flex-1 px-3 py-2 border border-gray-300 rounded text-sm">
                      <option>Select field...</option>
                      {selectedFields.map(field => (
                        <option key={field} value={field}>{field}</option>
                      ))}
                    </select>
                    <select className="px-3 py-2 border border-gray-300 rounded text-sm">
                      <option value="equals">Equals</option>
                      <option value="contains">Contains</option>
                      <option value="greater">Greater than</option>
                      <option value="less">Less than</option>
                    </select>
                    <input
                      type="text"
                      placeholder="Value..."
                      className="flex-1 px-3 py-2 border border-gray-300 rounded text-sm"
                    />
                    <button
                      onClick={() => removeFilter(index)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Visualization */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              4. Choose Visualization
            </h3>
            <div className="grid grid-cols-4 gap-4">
              {visualizations.map((viz) => {
                const Icon = viz.icon;
                return (
                  <button
                    key={viz.value}
                    onClick={() => setVisualizationType(viz.value)}
                    className={`flex flex-col items-center gap-2 p-4 rounded-lg border-2 transition-all ${
                      visualizationType === viz.value
                        ? "border-blue-500 bg-blue-50"
                        : "border-gray-200 hover:border-gray-300"
                    }`}
                  >
                    <Icon className="h-6 w-6" />
                    <span className="text-sm font-medium">{viz.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Panel - Preview */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6 sticky top-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Preview</h3>
            
            {!reportName ? (
              <p className="text-sm text-gray-500">Enter report name to start</p>
            ) : !selectedDataSource ? (
              <p className="text-sm text-gray-500">Select a data source</p>
            ) : selectedFields.length === 0 ? (
              <p className="text-sm text-gray-500">Select at least one field</p>
            ) : (
              <div className="space-y-4">
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-1">Report Name</p>
                  <p className="text-sm text-gray-900">{reportName}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-1">Data Source</p>
                  <p className="text-sm text-gray-900">
                    {selectedDataSourceObj?.label}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-1">Selected Fields ({selectedFields.length})</p>
                  <div className="flex flex-wrap gap-1">
                    {selectedFields.map(field => (
                      <span key={field} className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded">
                        {field}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-1">Filters</p>
                  <p className="text-sm text-gray-900">
                    {filters.length > 0 ? `${filters.length} filters applied` : "No filters"}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-1">Visualization</p>
                  <p className="text-sm text-gray-900">
                    {visualizations.find(v => v.value === visualizationType)?.label}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
