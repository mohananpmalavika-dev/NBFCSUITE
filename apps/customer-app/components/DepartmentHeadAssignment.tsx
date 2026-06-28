// Department Head Assignment Component
// Manages department head assignment workflow with employee selection

'use client';

import React, { useState, useEffect } from 'react';

interface Employee {
  id: string;
  employee_number: string;
  first_name: string;
  last_name: string;
  email: string;
  department_id?: string | null;
}

interface Department {
  id: string;
  department_code: string;
  department_name: string;
  department_head_employee_id?: string | null;
  parent_department_id?: string | null;
}

interface DepartmentHeadAssignmentProps {
  department: Department;
  employees: Employee[];
  isLoading: boolean;
  onAssignHead: (departmentId: string, employeeId: string) => Promise<void>;
  onUnassignHead: (departmentId: string) => Promise<void>;
}

export function DepartmentHeadAssignment({
  department,
  employees,
  isLoading,
  onAssignHead,
  onUnassignHead,
}: DepartmentHeadAssignmentProps) {
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<string>(department.department_head_employee_id || '');
  const [isAssigning, setIsAssigning] = useState(false);

  useEffect(() => {
    setSelectedEmployeeId(department.department_head_employee_id || '');
  }, [department.department_head_employee_id]);

  const currentHead = employees.find((e) => e.id === selectedEmployeeId);
  const availableEmployees = employees.filter(
    (e) =>
      !selectedEmployeeId ||
      e.id === selectedEmployeeId ||
      e.department_id === department.id ||
      !e.department_id,
  );

  const handleAssign = async () => {
    if (!selectedEmployeeId) return;
    setIsAssigning(true);
    try {
      await onAssignHead(department.id, selectedEmployeeId);
    } catch (error) {
      console.error('Failed to assign department head:', error);
    } finally {
      setIsAssigning(false);
    }
  };

  const handleUnassign = async () => {
    setIsAssigning(true);
    try {
      await onUnassignHead(department.id);
      setSelectedEmployeeId('');
    } catch (error) {
      console.error('Failed to unassign department head:', error);
    } finally {
      setIsAssigning(false);
    }
  };

  return (
    <div className="border border-slate-300 rounded-md p-4 bg-white">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="font-semibold text-sm">{department.department_name}</h3>
          <p className="text-xs text-slate-600">{department.department_code}</p>
        </div>
        {currentHead && (
          <div className="bg-blue-50 px-2 py-1 rounded text-xs">
            <strong>Current Head:</strong> {currentHead.first_name} {currentHead.last_name}
          </div>
        )}
      </div>

      <div className="space-y-3">
        <div>
          <label className="block text-xs font-medium text-slate-700 mb-1">
            Select Employee
          </label>
          <select
            value={selectedEmployeeId}
            onChange={(e) => setSelectedEmployeeId(e.target.value)}
            disabled={isLoading || isAssigning}
            className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm bg-white hover:border-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100"
          >
            <option value="">-- No Head Selected --</option>
            {availableEmployees.map((emp) => (
              <option key={emp.id} value={emp.id}>
                {emp.employee_number} - {emp.first_name} {emp.last_name} ({emp.email})
              </option>
            ))}
          </select>
        </div>

        <div className="flex gap-2">
          <button
            onClick={handleAssign}
            disabled={!selectedEmployeeId || isLoading || isAssigning}
            className="flex-1 px-3 py-2 bg-green-600 text-white rounded-md text-sm font-medium hover:bg-green-700 disabled:bg-slate-400 transition"
          >
            {isAssigning ? '⏳ Assigning...' : '✓ Assign Head'}
          </button>
          {currentHead && (
            <button
              onClick={handleUnassign}
              disabled={isLoading || isAssigning}
              className="flex-1 px-3 py-2 bg-red-600 text-white rounded-md text-sm font-medium hover:bg-red-700 disabled:bg-slate-400 transition"
            >
              {isAssigning ? '⏳ Removing...' : '✗ Remove Head'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export function DepartmentHeadPanel({
  departments,
  employees,
  isLoading,
  onAssignHead,
  onUnassignHead,
}: {
  departments: Department[];
  employees: Employee[];
  isLoading: boolean;
  onAssignHead: (departmentId: string, employeeId: string) => Promise<void>;
  onUnassignHead: (departmentId: string) => Promise<void>;
}) {
  const rootDepts = departments.filter((d) => !d.parent_department_id);

  return (
    <div className="space-y-4">
      <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3">
        <p className="text-xs text-yellow-800">
          💡 <strong>Tip:</strong> Assign department heads to establish organizational reporting hierarchy.
        </p>
      </div>

      <div className="grid gap-4">
        {rootDepts.length > 0 ? (
          rootDepts.map((dept) => (
            <DepartmentHeadAssignment
              key={dept.id}
              department={dept}
              employees={employees}
              isLoading={isLoading}
              onAssignHead={onAssignHead}
              onUnassignHead={onUnassignHead}
            />
          ))
        ) : (
          <div className="p-4 text-center text-slate-600 border border-slate-300 rounded-md">
            No departments to assign heads to. Seed departments first.
          </div>
        )}
      </div>
    </div>
  );
}
