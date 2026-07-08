'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { collectionApi } from '@/lib/api/collection';
import { ActionType } from '@/types/collection';

export default function NewStrategyPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    product_type: '',
    min_dpd: 0,
    max_dpd: 30,
    min_outstanding: 0,
    max_outstanding: 0,
    priority: 1,
    is_active: true,
    auto_assign: false,
    escalation_days: 7,
  });

  const [actions, setActions] = useState<Array<{
    action_type: string;
    trigger_day: number;
    template_id?: string;
    description: string;
  }>>([]);

  const [showActionForm, setShowActionForm] = useState(false);
  const [newAction, setNewAction] = useState({
    action_type: 'sms',
    trigger_day: 1,
    template_id: '',
    description: '',
  });

  const actionTypes = [
    'sms',
    'email',
    'call',
    'field_visit',
    'legal_notice',
    'payment_link',
  ] as const;

  const handleAddAction = () => {
    setActions([...actions, { ...newAction }]);
    setNewAction({
      action_type: 'sms',
      trigger_day: 1,
      template_id: '',
      description: '',
    });
    setShowActionForm(false);
  };

  const handleRemoveAction = (index: number) => {
    setActions(actions.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name || formData.min_dpd < 0 || formData.max_dpd <= formData.min_dpd) {
      alert('Please fill in all required fields correctly');
      return;
    }

    setLoading(true);
    try {
      const payload = {
        ...formData,
        actions,
      };

      const strategy = await collectionApi.createStrategy(payload);
      router.push(`/collections/strategies`);
    } catch (error) {
      console.error('Failed to create strategy:', error);
      alert('Failed to create collection strategy');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Create Collection Strategy</h1>
          <p className="text-gray-600 mt-1">
            Define automated collection workflows based on DPD and outstanding amount
          </p>
        </div>
        <button
          onClick={() => router.back()}
          className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          Cancel
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Information */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Strategy Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., Early Stage Personal Loan"
                required
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Describe when and how this strategy should be applied..."
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Product Type
              </label>
              <select
                value={formData.product_type}
                onChange={(e) => setFormData({ ...formData, product_type: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Products</option>
                <option value="personal_loan">Personal Loan</option>
                <option value="gold_loan">Gold Loan</option>
                <option value="vehicle_loan">Vehicle Loan</option>
                <option value="property_loan">Property Loan</option>
                <option value="business_loan">Business Loan</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Priority (1-10)
              </label>
              <input
                type="number"
                min="1"
                max="10"
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) || 1 })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">Higher number = higher priority</p>
            </div>
          </div>
        </div>

        {/* DPD Range */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">DPD Range</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Minimum DPD *
              </label>
              <input
                type="number"
                min="0"
                value={formData.min_dpd}
                onChange={(e) => setFormData({ ...formData, min_dpd: parseInt(e.target.value) || 0 })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Maximum DPD *
              </label>
              <input
                type="number"
                min="1"
                value={formData.max_dpd}
                onChange={(e) => setFormData({ ...formData, max_dpd: parseInt(e.target.value) || 30 })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
          </div>
          <div className="mt-4 p-3 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-900">
              <strong>DPD Buckets Guide:</strong>
            </p>
            <ul className="text-xs text-blue-800 mt-2 space-y-1">
              <li>• 0-30 DPD: Early Stage (friendly reminders)</li>
              <li>• 31-60 DPD: Follow-up Stage (regular calls, field visits)</li>
              <li>• 61-90 DPD: Serious Stage (intensive follow-up)</li>
              <li>• 91-180 DPD: NPA Stage (legal notices, recovery)</li>
              <li>• 181+ DPD: Write-off Stage (legal action)</li>
            </ul>
          </div>
        </div>

        {/* Outstanding Amount Range */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Outstanding Amount Range</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Minimum Outstanding (₹)
              </label>
              <input
                type="number"
                min="0"
                value={formData.min_outstanding}
                onChange={(e) => setFormData({ ...formData, min_outstanding: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">Leave 0 for no minimum</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Maximum Outstanding (₹)
              </label>
              <input
                type="number"
                min="0"
                value={formData.max_outstanding}
                onChange={(e) => setFormData({ ...formData, max_outstanding: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">Leave 0 for no maximum</p>
            </div>
          </div>
        </div>

        {/* Automation Settings */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Automation Settings</h2>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <label htmlFor="is_active" className="text-sm font-medium text-gray-900">
                Active Strategy
              </label>
            </div>
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="auto_assign"
                checked={formData.auto_assign}
                onChange={(e) => setFormData({ ...formData, auto_assign: e.target.checked })}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <label htmlFor="auto_assign" className="text-sm font-medium text-gray-900">
                Auto-assign to Field Agents
              </label>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Escalation Days
              </label>
              <input
                type="number"
                min="1"
                value={formData.escalation_days}
                onChange={(e) => setFormData({ ...formData, escalation_days: parseInt(e.target.value) || 7 })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">
                Days before escalating to next strategy level
              </p>
            </div>
          </div>
        </div>

        {/* Collection Actions */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Collection Actions</h2>
            <button
              type="button"
              onClick={() => setShowActionForm(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
            >
              + Add Action
            </button>
          </div>

          {actions.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No actions defined. Add actions to automate collection workflow.
            </div>
          ) : (
            <div className="space-y-3">
              {actions.map((action, index) => (
                <div key={index} className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium uppercase">
                        {action.action_type.replace('_', ' ')}
                      </span>
                      <span className="text-sm text-gray-600">Day {action.trigger_day}</span>
                    </div>
                    {action.description && (
                      <p className="text-sm text-gray-700 mt-2">{action.description}</p>
                    )}
                  </div>
                  <button
                    type="button"
                    onClick={() => handleRemoveAction(index)}
                    className="text-red-600 hover:text-red-700"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Add Action Form */}
          {showActionForm && (
            <div className="mt-4 p-4 border-2 border-blue-200 rounded-lg bg-blue-50">
              <h3 className="font-semibold text-gray-900 mb-3">Add New Action</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Action Type
                  </label>
                  <select
                    value={newAction.action_type}
                    onChange={(e) => setNewAction({ ...newAction, action_type: e.target.value as ActionType })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {actionTypes.map((type) => (
                      <option key={type} value={type}>
                        {type.replace('_', ' ').toUpperCase()}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Trigger Day
                  </label>
                  <input
                    type="number"
                    min="1"
                    value={newAction.trigger_day}
                    onChange={(e) => setNewAction({ ...newAction, trigger_day: parseInt(e.target.value) || 1 })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Template ID (Optional)
                  </label>
                  <input
                    type="text"
                    value={newAction.template_id}
                    onChange={(e) => setNewAction({ ...newAction, template_id: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., SMS_REMINDER_1"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    value={newAction.description}
                    onChange={(e) => setNewAction({ ...newAction, description: e.target.value })}
                    rows={2}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Describe this action..."
                  />
                </div>
              </div>
              <div className="flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowActionForm(false)}
                  className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleAddAction}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Add Action
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Submit */}
        <div className="flex justify-end gap-3">
          <button
            type="button"
            onClick={() => router.back()}
            className="px-6 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Creating...' : 'Create Strategy'}
          </button>
        </div>
      </form>
    </div>
  );
}
