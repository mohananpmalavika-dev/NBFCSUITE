'use client';

import { useState, useEffect } from 'react';
import { SalaryComponentService } from '@/services/payroll.service';
import type { 
  SalaryComponent, 
  SalaryComponentCreate
} from '@/types/payroll.types';
import { ComponentType, CalculationType } from '@/types/payroll.types';

export default function SalaryComponentsPage() {
  const [components, setComponents] = useState<SalaryComponent[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingComponent, setEditingComponent] = useState<SalaryComponent | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<ComponentType | ''>('');
  const [filterActive, setFilterActive] = useState<boolean | ''>('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const [formData, setFormData] = useState<SalaryComponentCreate>({
    component_name: '',
    component_code: '',
    component_type: ComponentType.EARNING,
    calculation_type: CalculationType.FIXED,
    default_value: 0,
    is_statutory: false,
    is_taxable: true,
    is_active: true,
    display_order: 1,
    description: ''
  });

  useEffect(() => {
    loadComponents();
  }, [currentPage, searchTerm, filterType, filterActive]);

  const loadComponents = async () => {
    try {
      setLoading(true);
      const response = await SalaryComponentService.list({
        page: currentPage,
        page_size: 20,
        search: searchTerm || undefined,
        component_type: filterType || undefined,
        is_active: filterActive === '' ? undefined : filterActive
      });
      setComponents(response.items);
      setTotalPages(response.pages);
    } catch (error) {
      console.error('Failed to load components:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingComponent) {
        await SalaryComponentService.update(editingComponent.id, formData);
      } else {
        await SalaryComponentService.create(formData);
      }
      setShowModal(false);
      resetForm();
      loadComponents();
    } catch (error) {
      console.error('Failed to save component:', error);
    }
  };

  const handleEdit = (component: SalaryComponent) => {
    setEditingComponent(component);
    setFormData({
      component_name: component.component_name,
      component_code: component.component_code,
      component_type: component.component_type,
      calculation_type: component.calculation_type,
      default_value: component.default_value,
      is_statutory: component.is_statutory,
      is_taxable: component.is_taxable,
      is_active: component.is_active,
      display_order: component.display_order,
      description: component.description || ''
    });
    setShowModal(true);
  };

  const handleDelete = async (id: number) => {
    if (confirm('Are you sure you want to delete this component?')) {
      try {
        await SalaryComponentService.delete(id);
        loadComponents();
      } catch (error) {
        console.error('Failed to delete component:', error);
      }
    }
  };

  const resetForm = () => {
    setEditingComponent(null);
    setFormData({
      component_name: '',
      component_code: '',
      component_type: ComponentType.EARNING,
      calculation_type: CalculationType.FIXED,
      default_value: 0,
      is_statutory: false,
      is_taxable: true,
      is_active: true,
      display_order: 1,
      description: ''
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Salary Components</h1>
          <p className="text-sm text-gray-600 mt-1">Manage earnings and deduction components</p>
        </div>
        <button
          onClick={() => {
            resetForm();
            setShowModal(true);
          }}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          + Add Component
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <input
            type="text"
            placeholder="Search components..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          />
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value as ComponentType | '')}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          >
            <option value="">All Types</option>
            <option value="EARNING">Earnings</option>
            <option value="DEDUCTION">Deductions</option>
          </select>
          <select
            value={filterActive === '' ? '' : filterActive ? 'true' : 'false'}
            onChange={(e) => setFilterActive(e.target.value === '' ? '' : e.target.value === 'true')}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          >
            <option value="">All Status</option>
            <option value="true">Active</option>
            <option value="false">Inactive</option>
          </select>
          <button
            onClick={() => {
              setSearchTerm('');
              setFilterType('');
              setFilterActive('');
            }}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Components Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Calculation</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Value</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan={7} className="px-6 py-4 text-center text-gray-500">Loading...</td>
              </tr>
            ) : components.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-6 py-4 text-center text-gray-500">No components found</td>
              </tr>
            ) : (
              components.map((component) => (
                <tr key={component.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {component.component_code}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {component.component_name}
                    {component.is_statutory && (
                      <span className="ml-2 px-2 py-1 text-xs bg-purple-100 text-purple-700 rounded">Statutory</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <span className={`px-2 py-1 rounded text-xs ${
                      component.component_type === 'EARNING' 
                        ? 'bg-green-100 text-green-700' 
                        : 'bg-red-100 text-red-700'
                    }`}>
                      {component.component_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {component.calculation_type.replace(/_/g, ' ')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {component.calculation_type.includes('PERCENTAGE') 
                      ? `${component.default_value}%` 
                      : `₹${component.default_value}`
                    }
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`px-2 py-1 rounded text-xs ${
                      component.is_active 
                        ? 'bg-green-100 text-green-700' 
                        : 'bg-gray-100 text-gray-700'
                    }`}>
                      {component.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                    <button
                      onClick={() => handleEdit(component)}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(component.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center gap-2">
          <button
            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50"
          >
            Previous
          </button>
          <span className="px-4 py-2">
            Page {currentPage} of {totalPages}
          </span>
          <button
            onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50"
          >
            Next
          </button>
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                {editingComponent ? 'Edit Component' : 'Add New Component'}
              </h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Component Name *
                    </label>
                    <input
                      type="text"
                      value={formData.component_name}
                      onChange={(e) => setFormData({...formData, component_name: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Component Code *
                    </label>
                    <input
                      type="text"
                      value={formData.component_code}
                      onChange={(e) => setFormData({...formData, component_code: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Type *
                    </label>
                    <select
                      value={formData.component_type}
                      onChange={(e) => setFormData({...formData, component_type: e.target.value as ComponentType})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                      required
                    >
                      <option value="EARNING">Earning</option>
                      <option value="DEDUCTION">Deduction</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Calculation Type *
                    </label>
                    <select
                      value={formData.calculation_type}
                      onChange={(e) => setFormData({...formData, calculation_type: e.target.value as CalculationType})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                      required
                    >
                      <option value="FIXED">Fixed</option>
                      <option value="PERCENTAGE_OF_BASIC">Percentage of Basic</option>
                      <option value="PERCENTAGE_OF_GROSS">Percentage of Gross</option>
                      <option value="PERCENTAGE_OF_CTC">Percentage of CTC</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Value *
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.default_value}
                      onChange={(e) => setFormData({...formData, default_value: parseFloat(e.target.value)})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Display Order
                    </label>
                    <input
                      type="number"
                      value={formData.display_order}
                      onChange={(e) => setFormData({...formData, display_order: parseInt(e.target.value)})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                    rows={3}
                  />
                </div>

                <div className="flex gap-4">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.is_statutory}
                      onChange={(e) => setFormData({...formData, is_statutory: e.target.checked})}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">Statutory Component</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.is_taxable}
                      onChange={(e) => setFormData({...formData, is_taxable: e.target.checked})}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">Taxable</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.is_active}
                      onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">Active</span>
                  </label>
                </div>

                <div className="flex justify-end gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setShowModal(false);
                      resetForm();
                    }}
                    className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    {editingComponent ? 'Update' : 'Create'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
