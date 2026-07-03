'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';

export default function DocumentTemplatesPage() {
  const [templates, setTemplates] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Filters
  const [categoryFilter, setCategoryFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [activeFilter, setActiveFilter] = useState<boolean | null>(null);
  
  // Create/Edit Modal
  const [showModal, setShowModal] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<any | null>(null);
  const [formData, setFormData] = useState({
    template_code: '',
    template_name: '',
    description: '',
    category_id: '',
    template_type: 'loan_agreement',
    file_format: 'pdf',
    storage_path: '',
    template_variables: '{}',
    is_active: true
  });

  useEffect(() => {
    loadData();
  }, [categoryFilter, typeFilter, activeFilter]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [templatesData, catsData] = await Promise.all([
        goldApi.listDocumentTemplates({
          category_id: categoryFilter || undefined,
          template_type: typeFilter || undefined,
          is_active: activeFilter !== null ? activeFilter : undefined
        }),
        goldApi.listDocumentCategories({ is_active: true })
      ]);
      
      setTemplates(templatesData);
      setCategories(catsData);
      setError('');
    } catch (err: any) {
      setError('Failed to load templates: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = (template?: any) => {
    if (template) {
      setEditingTemplate(template);
      setFormData({
        template_code: template.template_code,
        template_name: template.template_name,
        description: template.description || '',
        category_id: template.category_id || '',
        template_type: template.template_type,
        file_format: template.file_format,
        storage_path: template.storage_path,
        template_variables: JSON.stringify(template.template_variables || {}, null, 2),
        is_active: template.is_active
      });
    } else {
      setEditingTemplate(null);
      setFormData({
        template_code: '',
        template_name: '',
        description: '',
        category_id: '',
        template_type: 'loan_agreement',
        file_format: 'pdf',
        storage_path: '',
        template_variables: '{}',
        is_active: true
      });
    }
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingTemplate(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      // Parse template variables JSON
      let templateVars = {};
      try {
        templateVars = JSON.parse(formData.template_variables);
      } catch {
        alert('Invalid JSON in template variables');
        return;
      }

      const payload = {
        ...formData,
        template_variables: templateVars,
        created_by: 'current-user-id' // TODO: Replace with actual user ID
      };

      if (editingTemplate) {
        await goldApi.updateDocumentTemplate(editingTemplate.template_id, {
          ...payload,
          updated_by: 'current-user-id'
        });
      } else {
        await goldApi.createDocumentTemplate(payload);
      }

      alert(`Template ${editingTemplate ? 'updated' : 'created'} successfully`);
      handleCloseModal();
      loadData();
    } catch (err: any) {
      alert(`Failed to ${editingTemplate ? 'update' : 'create'} template: ` + err.message);
    }
  };

  const handleDelete = async (template: any) => {
    if (!confirm(`Delete template "${template.template_name}"?`)) return;
    
    try {
      await goldApi.deleteDocumentTemplate(template.template_id);
      alert('Template deleted successfully');
      loadData();
    } catch (err: any) {
      alert('Failed to delete template: ' + err.message);
    }
  };

  if (loading && templates.length === 0) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
            <p className="text-gray-600">Loading templates...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Document Templates</h1>
          <p className="text-gray-600">Manage document templates for automatic generation</p>
        </div>
        <button
          onClick={() => handleOpenModal()}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
        >
          + New Template
        </button>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Filters */}
      <div className="mb-6 bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Categories</option>
              {categories.map(cat => (
                <option key={cat.category_id} value={cat.category_id}>
                  {cat.category_name}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Template Type</label>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Types</option>
              <option value="loan_agreement">Loan Agreement</option>
              <option value="receipt">Receipt</option>
              <option value="report">Report</option>
              <option value="notice">Notice</option>
              <option value="certificate">Certificate</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={activeFilter === null ? '' : String(activeFilter)}
              onChange={(e) => setActiveFilter(e.target.value === '' ? null : e.target.value === 'true')}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Status</option>
              <option value="true">Active</option>
              <option value="false">Inactive</option>
            </select>
          </div>
        </div>
      </div>

      {/* Templates Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {templates.map((template) => (
          <div key={template.template_id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 mb-1">
                  {template.template_name}
                </h3>
                <p className="text-sm text-gray-500">{template.template_code}</p>
              </div>
              <span className={`px-2 py-1 text-xs font-medium rounded ${
                template.is_active 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {template.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>

            {template.description && (
              <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                {template.description}
              </p>
            )}

            <div className="space-y-2 mb-4">
              <div className="flex items-center text-sm">
                <svg className="w-4 h-4 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
                <span className="text-gray-600">
                  {categories.find(c => c.category_id === template.category_id)?.category_name || 'No Category'}
                </span>
              </div>
              
              <div className="flex items-center text-sm">
                <svg className="w-4 h-4 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span className="text-gray-600 capitalize">{template.template_type.replace('_', ' ')}</span>
              </div>
              
              <div className="flex items-center text-sm">
                <svg className="w-4 h-4 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span className="text-gray-600 uppercase">{template.file_format}</span>
              </div>
            </div>

            <div className="flex gap-2 pt-4 border-t border-gray-200">
              <button
                onClick={() => handleOpenModal(template)}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
              >
                Edit
              </button>
              <button
                onClick={() => handleDelete(template)}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm font-medium"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {templates.length === 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <svg className="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Templates Found</h3>
          <p className="text-gray-600 mb-4">Create your first document template to get started.</p>
          <button
            onClick={() => handleOpenModal()}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
          >
            Create Template
          </button>
        </div>
      )}

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-10 mx-auto p-5 border w-full max-w-3xl shadow-lg rounded-lg bg-white mb-10">
            <div className="mb-4">
              <h3 className="text-lg font-bold text-gray-900">
                {editingTemplate ? 'Edit Template' : 'Create Template'}
              </h3>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Template Code *
                  </label>
                  <input
                    type="text"
                    value={formData.template_code}
                    onChange={(e) => setFormData(prev => ({ ...prev, template_code: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                    disabled={!!editingTemplate}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Template Name *
                  </label>
                  <input
                    type="text"
                    value={formData.template_name}
                    onChange={(e) => setFormData(prev => ({ ...prev, template_name: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                  <select
                    value={formData.category_id}
                    onChange={(e) => setFormData(prev => ({ ...prev, category_id: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select Category</option>
                    {categories.map(cat => (
                      <option key={cat.category_id} value={cat.category_id}>
                        {cat.category_name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Template Type *</label>
                  <select
                    value={formData.template_type}
                    onChange={(e) => setFormData(prev => ({ ...prev, template_type: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="loan_agreement">Loan Agreement</option>
                    <option value="receipt">Receipt</option>
                    <option value="report">Report</option>
                    <option value="notice">Notice</option>
                    <option value="certificate">Certificate</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">File Format *</label>
                  <select
                    value={formData.file_format}
                    onChange={(e) => setFormData(prev => ({ ...prev, file_format: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="pdf">PDF</option>
                    <option value="docx">DOCX</option>
                    <option value="xlsx">XLSX</option>
                    <option value="html">HTML</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Storage Path *</label>
                <input
                  type="text"
                  value={formData.storage_path}
                  onChange={(e) => setFormData(prev => ({ ...prev, storage_path: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="/templates/template_name.pdf"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Template Variables (JSON)
                </label>
                <textarea
                  value={formData.template_variables}
                  onChange={(e) => setFormData(prev => ({ ...prev, template_variables: e.target.value }))}
                  rows={6}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                  placeholder='{"fields": [{"name": "field_name", "type": "string", "required": true}]}'
                />
                <p className="mt-1 text-xs text-gray-500">Define template variables in JSON format</p>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={formData.is_active}
                  onChange={(e) => setFormData(prev => ({ ...prev, is_active: e.target.checked }))}
                  className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <label htmlFor="is_active" className="ml-2 block text-sm text-gray-700">
                  Active
                </label>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                >
                  {editingTemplate ? 'Update Template' : 'Create Template'}
                </button>
                <button
                  type="button"
                  onClick={handleCloseModal}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 font-medium"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
