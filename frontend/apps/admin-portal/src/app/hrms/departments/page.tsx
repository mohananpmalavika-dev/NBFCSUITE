"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  getDepartments,
  getDepartmentStats,
  deleteDepartment,
  getDepartmentTree,
} from "@/services/hrms.service";
import type {
  DepartmentListItem,
  DepartmentStats,
  DepartmentTreeNode,
  DepartmentFilters,
} from "@/types/hrms.types";
import { DepartmentTypeLabels } from "@/types/hrms.types";

export default function DepartmentsPage() {
  const router = useRouter();
  const [departments, setDepartments] = useState<DepartmentListItem[]>([]);
  const [stats, setStats] = useState<DepartmentStats | null>(null);
  const [tree, setTree] = useState<DepartmentTreeNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<"list" | "tree">("list");
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [filters, setFilters] = useState<DepartmentFilters>({});
  const [search, setSearch] = useState("");

  useEffect(() => {
    loadDepartments();
    loadStats();
    if (view === "tree") {
      loadTree();
    }
  }, [page, filters, view]);

  const loadDepartments = async () => {
    try {
      setLoading(true);
      const response = await getDepartments({
        page,
        page_size: pageSize,
        ...filters,
      });
      setDepartments(response.items);
      setTotal(response.total);
    } catch (error) {
      console.error("Failed to load departments:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const data = await getDepartmentStats();
      setStats(data);
    } catch (error) {
      console.error("Failed to load stats:", error);
    }
  };

  const loadTree = async () => {
    try {
      const data = await getDepartmentTree();
      setTree(data);
    } catch (error) {
      console.error("Failed to load tree:", error);
    }
  };

  const handleSearch = () => {
    setFilters({ ...filters, search });
    setPage(1);
  };

  const handleDelete = async (id: number) => {
    if (confirm("Are you sure you want to delete this department?")) {
      try {
        await deleteDepartment(id);
        loadDepartments();
        loadStats();
      } catch (error: any) {
        console.error("Failed to delete department:", error);
        alert(error.response?.data?.detail || "Failed to delete department");
      }
    }
  };

  const renderTreeNode = (node: DepartmentTreeNode, level: number = 0) => (
    <div key={node.id} className={`${level > 0 ? "ml-6" : ""} mb-2`}>
      <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
        <div className="flex justify-between items-start">
          <div>
            <div className="font-semibold text-gray-900">
              {node.department_name}
            </div>
            <div className="text-sm text-gray-600">
              {node.department_code} • {DepartmentTypeLabels[node.department_type]}
            </div>
            {node.hod_name && (
              <div className="text-sm text-gray-600 mt-1">
                HOD: {node.hod_name}
              </div>
            )}
            <div className="text-sm text-gray-600">
              {node.employee_count} employees
            </div>
          </div>
          <button
            onClick={() => router.push(`/hrms/departments/${node.id}`)}
            className="text-blue-600 hover:text-blue-900 text-sm"
          >
            View
          </button>
        </div>
      </div>
      {node.children.length > 0 && (
        <div className="mt-2">
          {node.children.map((child) => renderTreeNode(child, level + 1))}
        </div>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Department Management
            </h1>
            <p className="text-gray-600 mt-1">
              Manage departments and organizational hierarchy
            </p>
          </div>
          <div className="flex gap-4">
            <button
              onClick={() => setView(view === "list" ? "tree" : "list")}
              className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg"
            >
              {view === "list" ? "Tree View" : "List View"}
            </button>
            <button
              onClick={() => router.push("/hrms/departments/new")}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
            >
              <span>+</span>
              <span>Add Department</span>
            </button>
          </div>
        </div>

        {/* Statistics */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-600">Total Departments</div>
              <div className="text-2xl font-bold text-gray-900">
                {stats.total_departments}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-600">Active</div>
              <div className="text-2xl font-bold text-green-600">
                {stats.active_departments}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-600">With Employees</div>
              <div className="text-2xl font-bold text-blue-600">
                {stats.employees_by_department.length}
              </div>
            </div>
          </div>
        )}

        {view === "list" ? (
          <>
            {/* Search */}
            <div className="bg-white rounded-lg shadow p-4 mb-6">
              <div className="flex gap-4">
                <input
                  type="text"
                  placeholder="Search departments..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleSearch()}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={handleSearch}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
                >
                  Search
                </button>
              </div>
            </div>

            {/* Department Table */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
              {loading ? (
                <div className="p-8 text-center text-gray-500">
                  Loading departments...
                </div>
              ) : departments.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  No departments found
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Department
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Type
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          HOD
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Employees
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Status
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {departments.map((dept) => (
                        <tr key={dept.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">
                              {dept.department_name}
                            </div>
                            <div className="text-sm text-gray-500">
                              {dept.department_code}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {DepartmentTypeLabels[dept.department_type]}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {dept.hod_name || "-"}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {dept.employee_count}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span
                              className={`px-2 py-1 text-xs font-semibold rounded-full ${
                                dept.is_active
                                  ? "bg-green-100 text-green-800"
                                  : "bg-gray-100 text-gray-800"
                              }`}
                            >
                              {dept.is_active ? "Active" : "Inactive"}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <button
                              onClick={() =>
                                router.push(`/hrms/departments/${dept.id}`)
                              }
                              className="text-blue-600 hover:text-blue-900 mr-4"
                            >
                              View
                            </button>
                            <button
                              onClick={() => handleDelete(dept.id)}
                              className="text-red-600 hover:text-red-900"
                            >
                              Delete
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Department Hierarchy
            </h2>
            {tree.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                No departments found
              </div>
            ) : (
              <div className="space-y-4">
                {tree.map((node) => renderTreeNode(node))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
