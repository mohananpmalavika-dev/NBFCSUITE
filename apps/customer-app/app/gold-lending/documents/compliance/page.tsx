'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';

export default function DocumentCompliancePage() {
  const [policies, setPolicies] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Filters
  const [categoryFilter, setCategoryFilter] = useState('');
  const [activeFilter, setActiveFilter] = useState<boolean | null>(null);
  
  // Create/Edit Modal
  const [showModal, setShowModal] = useState(false);
  const [editingPolicy, setEditingPolicy] = useState<any | null>(null);
  const [formData, setFormData] = useState({
    policy_code: '',
    policy_name: '',
    description: '',
    category_id: '',
    document_type: '',
    retention_period_days: 2555,
    retention_trigger: 'from_creation',
    archive_after_days: 1825,
    delete_after_retention: false,
    requires_legal_hold: false,
    compliance_regulation: '',
    auto_apply: false,
    priority: 100,
    is_active: true,
    effective_from: new Date().toISOString().split('T')[0],
    effective_to: ''
  });

  useEffect(() => {
    loadData();
  }, [categoryFilter, activeFilter]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [policiesData, catsData, docsData] = await Promise.all([
        goldApi.listRetentionPolicies({
          category_id: categoryFilter || undefined,
          is_active: activeFilter !== null ? activeFilter : undefined
        }),
        goldApi.listDocumentCategories({ is_active: true }),
        goldApi.listDocuments({ limit: 100 })
      ]);
      
      setPolicies(policiesData);
      setCategories(catsData);
      setDocuments(docsData);
      setError('');
    } catch (err: any) {
      setError('Failed to load compliance policies: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = (policy?: any) => {
    if (policy) {
      setEditingPolicy(policy);
      setFormData({
        policy_code: policy.policy_code,
        policy_name: policy.policy_name,
        description: policy.description || '',
        category_id: policy.category_id || '',
        document_type: policy.document_type || '',
        retention_period_days: policy.retention_period_days,
        retention_trigger: policy.retention_trigger,
        archive_after_days: policy.archive_after_days || 1825,
        delete_after_retention: policy.delete_after_retention,
        requires_legal_hold: policy.requires_legal_hold,
        compliance_regulation: policy.compliance_regulation || '',
        auto_apply: policy.auto_apply,
        priority: policy.priority,
        is_active: policy.is_active,
        effective_from: policy.effective_from,
        effective_to: policy.effective_to || ''
      });
    } else {
      setEditingPolicy(null);
      setFormData({
        policy_code: '',
        policy_name: '',
        description: '',
        category_id: '',
        document_type: '',
        retention_period_days: 2555,
        retention_trigger: 'from_creation',
        archive_after_days: 1825,
        delete_after_retention: false,
        requires_legal_hold: false,
        compliance_regulation: '',
        auto_apply: false,
        priority: 100,
        is_active: true,
        effective_from: new Date().toISOString().split('T')[0],
        effective_to: ''
      });
    }
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingPolicy(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const payload = {
        ...formData,
        effective_to: formData.effective_to || null,
        created_by: 'current-user-id' // TODO: Replace with actual user ID
      };

      if (editingPolicy) {
        await goldApi.updateRetentionPolicy(editingPolicy.policy_id, {
          ...payload,
          updated_by: 'current-user-id'
        });
      } else {
        await goldApi.createRetentionPolicy(payload);
      }

      alert(`Policy ${editingPolicy ? 'updated' : 'created'} successfully`);
      handleCloseModal();
      loadData();
    } catch (err: any) {
      alert(`Failed to ${editingPolicy ? 'update' : 'create'} policy: ` + err.message);
    }
  };

  const handleDelete = async (policy: any) => {
    if (!confirm(`Delete policy "${policy.policy_name}"?`)) return;
    
    try {
      await goldApi.deleteRetentionPolicy(policy.policy_id);
      alert('Policy deleted successfully');
      loadData();
    } catch (err: any) {
      alert('Failed to delete policy: ' + err.message);
    }
  };

  const formatDays = (days: number) => {
    if (days < 365) return `${days} days`;
    const years = Math.floor(days / 365);
    return `${years} year${years > 1 ? 's' : ''}`;
  };

  const getComplianceStatus = (doc: any) => {
    // Simple compliance check based on document age
    const docAge = Math.floor((new Date().getTime() - new Date(doc.created_at).getTime()) / (1000 * 60 * 60 * 24));
    const applicablePolicy = policies.find(p => 
      p.category_id === doc.category_id || p.document_type === doc.document_type
    );
    
    if (!applicablePolicy) return 'unknown';
    
    if (docAge > applicablePolicy.retention_period_days) return 'expired';
    if (docAge > applicablePolicy.archive_after_days) return 'archivable';
    return 'compliant';
  };

  if (loading && policies.length === 0) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
            <p className="text-gray-600">Loading compliance policies...</p>
          </div>
        </div>
      </div>
    );
  }

  // Calculate compliance statistics
  const complianceStats = {
    compliant: documents.filter(d => getComplianceStatus(d) === 'compliant').length,
    archivable: documents.filter(d => getComplianceStatus(d) === 'archivable').length,
    expired: documents.filter(d => getComplianceStatus(d) === 'expired').length,
    unknown: documents.filter(d => getComplianceStatus(d) === 'unknown').length
  };

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Compliance & Retention</h1>
          <p className="text-gray-600">Manage document retention policies and compliance regulations</p>
        </div>
        <button
          onClick={() => handleOpenModal()}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
        >
          + New Policy
        </button>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-sm font-medium text-gray-600 mb-1">Compliant</div>
          <div className="text-3xl font-bold text-green-600">{complianceStats.compliant}</div>
          <div className="text-xs text-gray-500 mt-1">Within retention period</div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-sm font-medium text-gray-600 mb-1">Archivable</div>
          <div className="text-3xl font-bold text-yellow-600">{complianceStats.archivable}</div>
          <div className="text-xs text-gray-500 mt-1">Ready for archival</div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-sm font-medium text-gray-600 mb-1">Expired</div>
          <div className="text-3xl font-bold text-red-600">{complianceStats.expired}</div>
          <div className="text-xs text-gray-500 mt-1">Past retention period</div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-sm font-medium text-gray-600 mb-1">Unknown</div>
          <div className="text-3xl font-bold text-gray-600">{complianceStats.unknown}</div>
          <div className="text-xs text-gray-500 mt-1">No policy assigned</div>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-6 bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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

      {/* Policies List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Policy
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category / Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Retention Period
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Archive After
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Regulation
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {policies.map((policy) => (
                <tr key={policy.policy_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-gray-900">{policy.policy_name}</div>
                    <div className="text-sm text-gray-500">{policy.policy_code}</div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {policy.category_id 
                      ? categories.find(c => c.category_id === policy.category_id)?.category_name || 'N/A'
                      : policy.document_type || 'All'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {formatDays(policy.retention_period_days)}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {policy.archive_after_days ? formatDays(policy.archive_after_days) : 'N/A'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {policy.compliance_regulation || 'N/A'}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-col gap-1">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        policy.is_active 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {policy.is_active ? 'Active' : 'Inactive'}
                      </span>
                      {policy.auto_apply && (
                        <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                          Auto-Apply
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right text-sm font-medium space-x-2">
                    <button
                      onClick={() => handleOpenModal(policy)}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(policy)}
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

        {policies.length === 0 && (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No policies found</h3>
            <p className="mt-1 text-sm text-gray-500">Create a retention policy to ensure compliance.</p>
            <button
              onClick={() => handleOpenModal()}
              className="mt-4 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
            >
              Create Policy
            </button>
          </div>
        )}
      </div>

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-10 mx-auto p-5 border w-full max-w-3xl shadow-lg rounded-lg bg-white mb-10">
            <div className="mb-4">
              <h3 className="text-lg font-bold text-gray-900">
                {editingPolicy ? 'Edit Retention Policy' : 'Create Retention Policy'}
              </h3>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Policy Code *
                  </label>
                  <input
                    type="text"
                    value={formData.policy_code}
                    onChange={(e) => setFormData(prev => ({ ...prev, policy_code: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                    disabled={!!editingPolicy}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Policy Name *
                  </label>
                  <input
                    type="text"
                    value={formData.policy_name}
                    onChange={(e) => setFormData(prev => ({ ...prev, policy_name: e.target.value }))}
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

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                  <select
                    value={formData.category_id}
                    onChange={(e) => setFormData(prev => ({ ...prev, category_id: e.target.value }))}
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
                  <label className="block text-sm font-medium text-gray-700 mb-1">Document Type</label>
                  <input
                    type="text"
                    value={formData.document_type}
                    onChange={(e) => setFormData(prev => ({ ...prev, document_type: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="Leave empty for all types"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Retention Period (days) *
                  </label>
                  <input
                    type="number"
                    value={formData.retention_period_days}
                    onChange={(e) => setFormData(prev => ({ ...prev, retention_period_days: parseInt(e.target.value) }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    min="1"
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">{formatDays(formData.retention_period_days)}</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Archive After (days)
                  </label>
                  <input
                    type="number"
                    value={formData.archive_after_days}
                    onChange={(e) => setFormData(prev => ({ ...prev, archive_after_days: parseInt(e.target.value) }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    min="1"
                  />
                  <p className="text-xs text-gray-500 mt-1">{formatDays(formData.archive_after_days)}</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                  <input
                    type="number"
                    value={formData.priority}
                    onChange={(e) => setFormData(prev => ({ ...prev, priority: parseInt(e.target.value) }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    min="0"
                    max="100"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Retention Trigger *
                  </label>
                  <select
                    value={formData.retention_trigger}
                    onChange={(e) => setFormData(prev => ({ ...prev, retention_trigger: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="from_creation">From Creation</option>
                    <option value="from_loan_closure">From Loan Closure</option>
                    <option value="from_last_access">From Last Access</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Compliance Regulation
                  </label>
                  <input
                    type="text"
                    value={formData.compliance_regulation}
                    onChange={(e) => setFormData(prev => ({ ...prev, compliance_regulation: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., RBI, GDPR"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Effective From *
                  </label>
                  <input
                    type="date"
                    value={formData.effective_from}
                    onChange={(e) => setFormData(prev => ({ ...prev, effective_from: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Effective To
                  </label>
                  <input
                    type="date"
                    value={formData.effective_to}
                    onChange={(e) => setFormData(prev => ({ ...prev, effective_to: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="auto_apply"
                    checked={formData.auto_apply}
                    onChange={(e) => setFormData(prev => ({ ...prev, auto_apply: e.target.checked }))}
                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="auto_apply" className="ml-2 block text-sm text-gray-700">
                    Auto-apply to matching documents
                  </label>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="delete_after_retention"
                    checked={formData.delete_after_retention}
                    onChange={(e) => setFormData(prev => ({ ...prev, delete_after_retention: e.target.checked }))}
                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="delete_after_retention" className="ml-2 block text-sm text-gray-700">
                    Delete after retention period
                  </label>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="requires_legal_hold"
                    checked={formData.requires_legal_hold}
                    onChange={(e) => setFormData(prev => ({ ...prev, requires_legal_hold: e.target.checked }))}
                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="requires_legal_hold" className="ml-2 block text-sm text-gray-700">
                    Requires legal hold
                  </label>
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
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                >
                  {editingPolicy ? 'Update Policy' : 'Create Policy'}
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
