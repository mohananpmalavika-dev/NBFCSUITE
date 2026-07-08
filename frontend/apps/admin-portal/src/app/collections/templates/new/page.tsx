'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { templateApi } from '@/lib/api/collection';
import { ActionType } from '@/types/collection';

export default function NewTemplatePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    action_type: 'sms',
    is_active: true,
    // SMS fields
    sms_content: '',
    // Email fields
    email_subject: '',
    email_body: '',
    // Call/Visit script
    script_content: '',
    // Legal notice fields
    notice_type: 'demand_notice',
    notice_content: '',
    legal_grounds: '',
  });

  const actionTypes = [
    'sms',
    'email',
    'call',
    'field_visit',
    'legal_notice',
    'payment_link',
  ] as const;

  const noticeTypes = [
    { value: 'demand_notice', label: 'Demand Notice' },
    { value: 'legal_notice_138', label: 'Legal Notice (Sec 138)' },
    { value: 'arbitration_notice', label: 'Arbitration Notice' },
    { value: 'possession_notice', label: 'Possession Notice' },
    { value: 'auction_notice', label: 'Auction Notice' },
    { value: 'recall_notice', label: 'Recall Notice' },
  ];

  const sampleVariables = [
    'customer_name',
    'loan_account',
    'due_amount',
    'due_date',
    'dpd',
    'outstanding',
    'payment_link',
    'contact_number',
  ];

  const insertVariable = (variable: string, field: 'sms' | 'email_subject' | 'email_body' | 'script' | 'notice') => {
    const placeholder = `{${variable}}`;
    
    if (field === 'sms') {
      setFormData({ ...formData, sms_content: formData.sms_content + placeholder });
    } else if (field === 'email_subject') {
      setFormData({ ...formData, email_subject: formData.email_subject + placeholder });
    } else if (field === 'email_body') {
      setFormData({ ...formData, email_body: formData.email_body + placeholder });
    } else if (field === 'script') {
      setFormData({ ...formData, script_content: formData.script_content + placeholder });
    } else if (field === 'notice') {
      setFormData({ ...formData, notice_content: formData.notice_content + placeholder });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name) {
      alert('Please provide a template name');
      return;
    }

    // Validate content based on action type
    if (formData.action_type === 'sms' && !formData.sms_content) {
      alert('Please provide SMS content');
      return;
    }
    if (formData.action_type === 'email' && (!formData.email_subject || !formData.email_body)) {
      alert('Please provide email subject and body');
      return;
    }
    if ((formData.action_type === 'call' || formData.action_type === 'field_visit') && !formData.script_content) {
      alert('Please provide script content');
      return;
    }
    if (formData.action_type === 'legal_notice' && !formData.notice_content) {
      alert('Please provide notice content');
      return;
    }

    setLoading(true);
    try {
      const template = await templateApi.create(formData);
      router.push('/collections/templates');
    } catch (error) {
      console.error('Failed to create template:', error);
      alert('Failed to create template');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Create Communication Template</h1>
          <p className="text-gray-600 mt-1">
            Create reusable templates for collection communications
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
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Template Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., Early Stage SMS Reminder"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Brief description of when to use this template..."
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Template Type *
              </label>
              <select
                value={formData.action_type}
                onChange={(e) =>
                  setFormData({ ...formData, action_type: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {actionTypes.map((type) => (
                  <option key={type} value={type}>
                    {type.replace('_', ' ').toUpperCase()}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <label htmlFor="is_active" className="text-sm font-medium text-gray-900">
                Active Template
              </label>
            </div>
          </div>
        </div>

        {/* SMS Content */}
        {formData.action_type === 'sms' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">SMS Content</h2>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="block text-sm font-medium text-gray-700">
                    Message Text *
                  </label>
                  <span className="text-xs text-gray-500">
                    {formData.sms_content.length}/160 characters
                  </span>
                </div>
                <textarea
                  value={formData.sms_content}
                  onChange={(e) => setFormData({ ...formData, sms_content: e.target.value })}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                  placeholder="Dear {customer_name}, your payment of {due_amount} is due on {due_date}..."
                />
              </div>
              <div>
                <p className="text-xs text-gray-600 mb-2">Insert variables:</p>
                <div className="flex flex-wrap gap-2">
                  {sampleVariables.map((variable) => (
                    <button
                      key={variable}
                      type="button"
                      onClick={() => insertVariable(variable, 'sms')}
                      className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs hover:bg-blue-100"
                    >
                      {`{${variable}}`}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Email Content */}
        {formData.action_type === 'email' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Email Content</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Subject Line *
                </label>
                <input
                  type="text"
                  value={formData.email_subject}
                  onChange={(e) => setFormData({ ...formData, email_subject: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Payment Reminder - Loan Account {loan_account}"
                />
                <div className="flex flex-wrap gap-2 mt-2">
                  {sampleVariables.map((variable) => (
                    <button
                      key={variable}
                      type="button"
                      onClick={() => insertVariable(variable, 'email_subject')}
                      className="px-2 py-1 bg-purple-50 text-purple-700 rounded text-xs hover:bg-purple-100"
                    >
                      {`{${variable}}`}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email Body *
                </label>
                <textarea
                  value={formData.email_body}
                  onChange={(e) => setFormData({ ...formData, email_body: e.target.value })}
                  rows={8}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Dear {customer_name},&#10;&#10;This is a reminder that your payment..."
                />
                <div className="flex flex-wrap gap-2 mt-2">
                  {sampleVariables.map((variable) => (
                    <button
                      key={variable}
                      type="button"
                      onClick={() => insertVariable(variable, 'email_body')}
                      className="px-2 py-1 bg-purple-50 text-purple-700 rounded text-xs hover:bg-purple-100"
                    >
                      {`{${variable}}`}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Call/Visit Script */}
        {(formData.action_type === 'call' || formData.action_type === 'field_visit') && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              {formData.action_type === 'call' ? 'Call Script' : 'Field Visit Script'}
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Script Content *
                </label>
                <textarea
                  value={formData.script_content}
                  onChange={(e) => setFormData({ ...formData, script_content: e.target.value })}
                  rows={10}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="1. Greet the customer&#10;2. Verify identity&#10;3. Mention loan account and due amount&#10;4. Listen to concerns&#10;5. Offer solutions..."
                />
                <div className="flex flex-wrap gap-2 mt-2">
                  {sampleVariables.map((variable) => (
                    <button
                      key={variable}
                      type="button"
                      onClick={() => insertVariable(variable, 'script')}
                      className="px-2 py-1 bg-green-50 text-green-700 rounded text-xs hover:bg-green-100"
                    >
                      {`{${variable}}`}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Legal Notice Content */}
        {formData.action_type === 'legal_notice' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Legal Notice Content</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Notice Type
                </label>
                <select
                  value={formData.notice_type}
                  onChange={(e) => setFormData({ ...formData, notice_type: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {noticeTypes.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Notice Content *
                </label>
                <textarea
                  value={formData.notice_content}
                  onChange={(e) => setFormData({ ...formData, notice_content: e.target.value })}
                  rows={12}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                  placeholder="To,&#10;{customer_name}&#10;&#10;Subject: Demand Notice under Section 138...&#10;&#10;Dear Sir/Madam,&#10;&#10;This is to inform you..."
                />
                <div className="flex flex-wrap gap-2 mt-2">
                  {sampleVariables.map((variable) => (
                    <button
                      key={variable}
                      type="button"
                      onClick={() => insertVariable(variable, 'notice')}
                      className="px-2 py-1 bg-red-50 text-red-700 rounded text-xs hover:bg-red-100"
                    >
                      {`{${variable}}`}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Legal Grounds
                </label>
                <textarea
                  value={formData.legal_grounds}
                  onChange={(e) => setFormData({ ...formData, legal_grounds: e.target.value })}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Legal sections and grounds for the notice..."
                />
              </div>
            </div>
          </div>
        )}

        {/* Payment Link */}
        {formData.action_type === 'payment_link' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Payment Link Message</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Message with Payment Link *
                </label>
                <textarea
                  value={formData.sms_content}
                  onChange={(e) => setFormData({ ...formData, sms_content: e.target.value })}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Dear {customer_name}, click here to pay {due_amount}: {payment_link}"
                />
                <div className="flex flex-wrap gap-2 mt-2">
                  {sampleVariables.map((variable) => (
                    <button
                      key={variable}
                      type="button"
                      onClick={() => insertVariable(variable, 'sms')}
                      className="px-2 py-1 bg-indigo-50 text-indigo-700 rounded text-xs hover:bg-indigo-100"
                    >
                      {`{${variable}}`}
                    </button>
                  ))}
                </div>
              </div>
              <div className="p-3 bg-blue-50 rounded-lg">
                <p className="text-sm text-blue-800">
                  <strong>Note:</strong> Use {`{payment_link}`} variable to insert the payment URL.
                  The system will automatically generate a secure payment link for each customer.
                </p>
              </div>
            </div>
          </div>
        )}

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
            {loading ? 'Creating...' : 'Create Template'}
          </button>
        </div>
      </form>
    </div>
  );
}
