'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { requisitionApi } from '@/services/recruitment.service';
import {
  JobRequisitionCreate,
  EmploymentType,
  RequisitionPriority
} from '@/types/recruitment.types';

export default function NewRequisitionPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [departments, setDepartments] = useState<any[]>([]);
  const [designations, setDesignations] = useState<any[]>([]);
  const [employees, setEmployees] = useState<any[]>([]);

  const [formData, setFormData] = useState<JobRequisitionCreate>({
    title: '',
    department_id: '',
    designation_id: '',
    number_of_positions: 1,
    employment_type: EmploymentType.FULL_TIME,
    work_location: '',
    priority: RequisitionPriority.MEDIUM,
    is_replacement: false
  });

  useEffect(() => {
    // TODO: Load departments, designations, employees from API
    // For now using mock data
    setDepartments([
      { id: '1', name: 'Engineering' },
      { id: '2', name: 'Sales' },
      { id: '3', name: 'Marketing' }
    ]);
    setDesignations([
      { id: '1', title: 'Software Engineer' },
      { id: '2', title: 'Sales Manager' },
      { id: '3', title: 'Marketing Manager' }
    ]);
    setEmployees([
      { id: '1', first_name: 'John', last_name: 'Doe' },
      { id: '2', first_name: 'Jane', last_name: 'Smith' }
    ]);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      await requisitionApi.create(formData);
      alert('Requisition created successfully!');
      router.push('/recruitment/requisitions');
    } catch (error) {
      console.error('Failed to create requisition:', error);
      alert('Failed to create requisition');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: keyof JobRequisitionCreate, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.back()}
            className="text-gray-600 hover:text-gray-900"
          >
            ← Back
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">New Job Requisition</h1>
            <p className="text-gray-600 mt-1">Create a new job opening request</p>
          </div>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="max-w-4xl">
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Basic Information</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Job Title <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                value={formData.title}
                onChange={(e) => handleChange('title', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., Senior Software Engineer"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Department <span className="text-red-500">*</span>
              </label>
              <select
                required
                value={formData.department_id}
                onChange={(e) => handleChange('department_id', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select Department</option>
                {departments.map(dept => (
                  <option key={dept.id} value={dept.id}>{dept.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Designation <span className="text-red-500">*</span>
              </label>
              <select
                required
                value={formData.designation_id}
                onChange={(e) => handleChange('designation_id', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select Designation</option>
                {designations.map(des => (
                  <option key={des.id} value={des.id}>{des.title}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Number of Positions <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                required
                min="1"
                value={formData.number_of_positions}
                onChange={(e) => handleChange('number_of_positions', parseInt(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Employment Type <span className="text-red-500">*</span>
              </label>
              <select
                required
                value={formData.employment_type}
                onChange={(e) => handleChange('employment_type', e.target.value as EmploymentType)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value={EmploymentType.FULL_TIME}>Full Time</option>
                <option value={EmploymentType.PART_TIME}>Part Time</option>
                <option value={EmploymentType.CONTRACT}>Contract</option>
                <option value={EmploymentType.INTERNSHIP}>Internship</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Work Location <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                value={formData.work_location}
                onChange={(e) => handleChange('work_location', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., Bangalore, Remote, Hybrid"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Priority <span className="text-red-500">*</span>
              </label>
              <select
                required
                value={formData.priority}
                onChange={(e) => handleChange('priority', e.target.value as RequisitionPriority)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value={RequisitionPriority.LOW}>Low</option>
                <option value={RequisitionPriority.MEDIUM}>Medium</option>
                <option value={RequisitionPriority.HIGH}>High</option>
                <option value={RequisitionPriority.URGENT}>Urgent</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Required By Date
              </label>
              <input
                type="date"
                value={formData.required_by_date || ''}
                onChange={(e) => handleChange('required_by_date', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Reporting To
              </label>
              <select
                value={formData.reporting_to_employee_id || ''}
                onChange={(e) => handleChange('reporting_to_employee_id', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select Manager</option>
                {employees.map(emp => (
                  <option key={emp.id} value={emp.id}>
                    {emp.first_name} {emp.last_name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Job Description</h2>
          
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Job Description
              </label>
              <textarea
                rows={4}
                value={formData.job_description || ''}
                onChange={(e) => handleChange('job_description', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Describe the role and what the candidate will be doing..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Key Responsibilities
              </label>
              <textarea
                rows={4}
                value={formData.responsibilities || ''}
                onChange={(e) => handleChange('responsibilities', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="List the main responsibilities and duties..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Required Qualifications
              </label>
              <textarea
                rows={3}
                value={formData.required_qualifications || ''}
                onChange={(e) => handleChange('required_qualifications', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Educational qualifications, certifications, mandatory skills..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Preferred Qualifications
              </label>
              <textarea
                rows={3}
                value={formData.preferred_qualifications || ''}
                onChange={(e) => handleChange('preferred_qualifications', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Nice-to-have skills and experience..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Required Experience (Years)
              </label>
              <input
                type="number"
                step="0.5"
                min="0"
                value={formData.required_experience_years || ''}
                onChange={(e) => handleChange('required_experience_years', parseFloat(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., 3.5"
              />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Compensation & Budget</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Minimum Salary (₹/year)
              </label>
              <input
                type="number"
                step="1000"
                min="0"
                value={formData.min_salary || ''}
                onChange={(e) => handleChange('min_salary', parseFloat(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., 500000"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Maximum Salary (₹/year)
              </label>
              <input
                type="number"
                step="1000"
                min="0"
                value={formData.max_salary || ''}
                onChange={(e) => handleChange('max_salary', parseFloat(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., 800000"
              />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Additional Information</h2>
          
          <div className="space-y-6">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="is_replacement"
                checked={formData.is_replacement}
                onChange={(e) => handleChange('is_replacement', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="is_replacement" className="ml-2 block text-sm text-gray-900">
                This is a replacement position
              </label>
            </div>

            {formData.is_replacement && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Replacing Employee
                </label>
                <select
                  value={formData.replacement_for_employee_id || ''}
                  onChange={(e) => handleChange('replacement_for_employee_id', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select Employee</option>
                  {employees.map(emp => (
                    <option key={emp.id} value={emp.id}>
                      {emp.first_name} {emp.last_name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Justification
              </label>
              <textarea
                rows={4}
                value={formData.justification || ''}
                onChange={(e) => handleChange('justification', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Explain why this position is needed..."
              />
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4">
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Creating...' : 'Create Requisition'}
          </button>
          <button
            type="button"
            onClick={() => router.back()}
            className="bg-gray-200 text-gray-700 px-8 py-3 rounded-lg hover:bg-gray-300 transition-colors font-medium"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
