// HRMS Department Management Component
// Displays department hierarchy and provides seeding functionality for Phase 1

'use client';

import React, { useState } from 'react';

interface DepartmentUIProps {
  departments: Array<{
    id: string;
    department_code: string;
    department_name: string;
    parent_department_id?: string | null;
    cost_center_code?: string | null;
    profit_center_code?: string | null;
    annual_budget: number;
    status: string;
  }>;
  isLoading: boolean;
  onSeed: () => Promise<void>;
  onCreateDepartment: (dept: any) => Promise<void>;
}

export function DepartmentHierarchyTree({ departments }: { departments: DepartmentUIProps['departments'] }) {
  const byId = new Map(departments.map((d) => [d.id, d]));
  const byCode = new Map(departments.map((d) => [d.department_code, d]));
  const children = new Map<string | null, DepartmentUIProps['departments'][0][]>();

  // Build hierarchy
  for (const dept of departments) {
    const parentKey = dept.parent_department_id || null;
    if (!children.has(parentKey)) {
      children.set(parentKey, []);
    }
    children.get(parentKey)!.push(dept);
  }

  const renderNode = (node: DepartmentUIProps['departments'][0], level = 0) => {
    const childNodes = children.get(node.id) || [];
    const indent = level * 24;
    return (
      <div key={node.id}>
        <div
          style={{ paddingLeft: `${indent}px` }}
          className="py-2 px-3 border-b border-slate-200 hover:bg-slate-50 transition"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {childNodes.length > 0 && (
                <span className="text-xs text-slate-500">▶</span>
              )}
              <span className="font-semibold text-sm">{node.department_code}</span>
              <span className="text-slate-700">{node.department_name}</span>
            </div>
            <div className="flex gap-2 text-xs text-slate-600">
              {node.cost_center_code && <span>CC: {node.cost_center_code}</span>}
              {node.profit_center_code && <span>PC: {node.profit_center_code}</span>}
              <span>₹{(node.annual_budget / 1000000).toFixed(1)}M</span>
            </div>
          </div>
        </div>
        {childNodes.map((child) => renderNode(child, level + 1))}
      </div>
    );
  };

  const roots = children.get(null) || [];

  return (
    <div className="border border-slate-300 rounded-md overflow-hidden bg-white">
      <div className="bg-slate-100 px-4 py-2 font-semibold text-sm">
        Department Hierarchy ({departments.length} total)
      </div>
      {roots.length > 0 ? (
        <div>{roots.map((root) => renderNode(root, 0))}</div>
      ) : (
        <div className="p-4 text-center text-slate-600">No departments configured</div>
      )}
    </div>
  );
}

export function DepartmentSeedButton({
  isLoading,
  onSeed,
}: {
  isLoading: boolean;
  onSeed: () => Promise<void>;
}) {
  const [isSeeding, setIsSeeding] = useState(false);

  const handleSeed = async () => {
    setIsSeeding(true);
    try {
      await onSeed();
    } catch (error) {
      console.error('Failed to seed departments:', error);
    } finally {
      setIsSeeding(false);
    }
  };

  return (
    <button
      onClick={handleSeed}
      disabled={isLoading || isSeeding}
      className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:bg-slate-400 transition"
    >
      {isSeeding ? '🌱 Seeding...' : '🌱 Seed 16 Departments'}
    </button>
  );
}

export function DepartmentStats({
  departments,
}: {
  departments: DepartmentUIProps['departments'];
}) {
  const totalBudget = departments.reduce((sum, d) => sum + (d.annual_budget || 0), 0);
  const rootDepts = departments.filter((d) => !d.parent_department_id).length;

  return (
    <div className="grid grid-cols-3 gap-4">
      <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
        <div className="text-sm text-blue-700 font-medium">Total Departments</div>
        <div className="text-2xl font-bold text-blue-900">{departments.length}</div>
      </div>
      <div className="bg-green-50 border border-green-200 rounded-md p-4">
        <div className="text-sm text-green-700 font-medium">Root Departments</div>
        <div className="text-2xl font-bold text-green-900">{rootDepts}</div>
      </div>
      <div className="bg-purple-50 border border-purple-200 rounded-md p-4">
        <div className="text-sm text-purple-700 font-medium">Total Budget</div>
        <div className="text-2xl font-bold text-purple-900">₹{(totalBudget / 10000000).toFixed(0)}Cr</div>
      </div>
    </div>
  );
}
