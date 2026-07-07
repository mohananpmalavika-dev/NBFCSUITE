"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getOrgChart } from "@/services/hrms.service";
import type { OrgChartNode } from "@/types/hrms.types";

export default function OrgChartPage() {
  const router = useRouter();
  const [orgChart, setOrgChart] = useState<OrgChartNode | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadOrgChart();
  }, []);

  const loadOrgChart = async () => {
    try {
      setLoading(true);
      const data = await getOrgChart();
      setOrgChart(data);
    } catch (error) {
      console.error("Failed to load org chart:", error);
    } finally {
      setLoading(false);
    }
  };

  const renderNode = (node: OrgChartNode, level: number = 0) => (
    <div key={node.id} className="flex flex-col items-center">
      {/* Employee Card */}
      <div
        className="bg-white rounded-lg shadow-lg p-4 mb-4 cursor-pointer hover:shadow-xl transition-shadow border-2 border-blue-500"
        style={{ width: "280px" }}
        onClick={() => router.push(`/hrms/employees/${node.id}`)}
      >
        <div className="flex items-center gap-3">
          {node.photo_url ? (
            <img
              src={node.photo_url}
              alt={node.full_name}
              className="w-16 h-16 rounded-full object-cover"
            />
          ) : (
            <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-xl">
              {node.full_name
                .split(" ")
                .map((n) => n[0])
                .join("")
                .toUpperCase()
                .slice(0, 2)}
            </div>
          )}
          <div className="flex-1 min-w-0">
            <div className="font-semibold text-gray-900 truncate">
              {node.full_name}
            </div>
            <div className="text-sm text-gray-600 truncate">
              {node.employee_code}
            </div>
            {node.designation_name && (
              <div className="text-sm text-blue-600 truncate">
                {node.designation_name}
              </div>
            )}
            {node.department_name && (
              <div className="text-xs text-gray-500 truncate">
                {node.department_name}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Subordinates */}
      {node.subordinates && node.subordinates.length > 0 && (
        <>
          {/* Connector Line */}
          <div className="w-0.5 h-8 bg-gray-300"></div>

          {/* Horizontal Line for Multiple Subordinates */}
          {node.subordinates.length > 1 && (
            <div className="relative w-full flex justify-center">
              <div
                className="h-0.5 bg-gray-300"
                style={{
                  width: `${Math.min(node.subordinates.length * 300, 1200)}px`,
                }}
              ></div>
            </div>
          )}

          {/* Subordinates Container */}
          <div className="flex gap-8 pt-8">
            {node.subordinates.map((subordinate) => (
              <div key={subordinate.id} className="flex flex-col items-center">
                {/* Vertical connector to parent */}
                {node.subordinates.length > 1 && (
                  <div className="w-0.5 h-8 bg-gray-300 -mt-8"></div>
                )}
                {renderNode(subordinate, level + 1)}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-full mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Organization Chart
            </h1>
            <p className="text-gray-600 mt-1">
              Visualize your organizational hierarchy
            </p>
          </div>
          <button
            onClick={() => router.push("/hrms/employees")}
            className="text-gray-600 hover:text-gray-900"
          >
            ← Back to Employees
          </button>
        </div>

        {/* Org Chart */}
        <div className="bg-white rounded-lg shadow p-8 overflow-x-auto">
          {loading ? (
            <div className="text-center text-gray-500 py-12">
              Loading organization chart...
            </div>
          ) : !orgChart ? (
            <div className="text-center text-gray-500 py-12">
              No organization chart data available
            </div>
          ) : (
            <div className="flex justify-center min-w-max">
              {renderNode(orgChart)}
            </div>
          )}
        </div>

        {/* Legend */}
        <div className="mt-6 bg-white rounded-lg shadow p-4">
          <h3 className="font-semibold text-gray-900 mb-2">Legend</h3>
          <div className="flex gap-6 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-blue-500 rounded"></div>
              <span>Active Employee</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-0.5 bg-gray-300"></div>
              <span>Reporting Line</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
