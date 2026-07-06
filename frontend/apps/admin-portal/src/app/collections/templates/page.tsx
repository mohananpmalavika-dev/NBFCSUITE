'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { collectionApi } from '@/lib/api/collection';
import { CollectionTemplate, ActionType } from '@/types/collection';

export default function TemplatesPage() {
  const router = useRouter();
  const [templates, setTemplates] = useState<CollectionTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<ActionType | 'all'>('all');

  useEffect(() => {
    loadTemplates();
  }, [filter]);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      const data = await collectionApi.getTemplates(
        filter === 'all' ? undefined : filter
      );
      setTemplates(data);
    } catch (error) {
      console.error('Failed to load templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTemplate = async (id: string) => {
    const confirmed = window.confirm('Are you sure you want to delete this template?');
    if (!confirmed) return;

    try {
      await collectionApi.deleteTemplate(id);
      loadTemplates();
    } catch (error) {
      console.error('Failed to delete template:', error);
      alert('Failed to delete template');
    }
  };

  const getActionTypeColor = (type: ActionType) => {
    const colors: Record<ActionType, string> = {
      sms: 'bg-blue-100 text-blue-800',
      email: 'bg-purple-100 text-purple-800',
      call: 'bg-green-100 text-green-800',
      field_visit: 'bg-yellow-100 text-yellow-800',
      legal_notice: 'bg-red-100 text-red-800',
      payment_link: 'bg-indigo-100 text-indigo-800',
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  const actionTypes: Array<ActionType | 'all'> = [
    'all',
    'sms',
    'email',
    'call',
    'field_visit',
    'legal_notice',
    'payment_link',
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Communication Templates</h1>
          <p className="text-gray-600 mt-1">
            Manage templates for SMS, Email, Notices and other communications
          </p>
        </div>
        <button
          onClick={() => router.push('/collections/templates/new')}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          + New Template
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center gap-4">
          <label className="text-sm font-medium text-gray-700">Filter by Type:</label>
          <div className="flex gap-2 flex-wrap">
            {actionTypes.map((type) => (
              <button
                key={type}
                onClick={() => setFilter(type)}
                className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                  filter === type
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {type === 'all' ? 'All Templates' : type.replace('_', ' ').toUpperCase()}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Templates Grid */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading templates...</div>
        ) : templates.length === 0 ? (
          <div className="p-8 text-center">
            <p className="text-gray-500 mb-4">No templates found</p>
            <button
              onClick={() => router.push('/collections/templates/new')}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              Create your first template
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-6">
            {templates.map((template) => (
              <div
                key={template.id}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => router.push(`/collections/templates/${template.id}`)}
              >
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-1">{template.name}</h3>
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getActionTypeColor(
                        template.action_type
                      )}`}
                    >
                      {template.action_type.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteTemplate(template.id);
                    }}
                    className="text-red-600 hover:text-red-700 text-sm"
                  >
                    🗑️
                  </button>
                </div>

                {template.description && (
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                    {template.description}
                  </p>
                )}

                <div className="bg-gray-50 rounded p-3 mb-3">
                  {template.action_type === 'sms' && (
                    <p className="text-xs text-gray-700 line-clamp-3 font-mono">
                      {template.sms_content}
                    </p>
                  )}
                  {template.action_type === 'email' && (
                    <div className="text-xs text-gray-700">
                      <p className="font-medium mb-1">Subject: {template.email_subject}</p>
                      <p className="line-clamp-2">{template.email_body}</p>
                    </div>
                  )}
                  {template.action_type === 'legal_notice' && (
                    <div className="text-xs text-gray-700">
                      <p className="font-medium mb-1">
                        {template.notice_type?.replace('_', ' ').toUpperCase()}
                      </p>
                      <p className="line-clamp-2">{template.notice_content}</p>
                    </div>
                  )}
                  {(template.action_type === 'call' ||
                    template.action_type === 'field_visit') && (
                    <p className="text-xs text-gray-700 line-clamp-3">
                      {template.script_content || 'No script content'}
                    </p>
                  )}
                </div>

                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>
                    {template.is_active ? (
                      <span className="text-green-600 font-medium">● Active</span>
                    ) : (
                      <span className="text-gray-400">○ Inactive</span>
                    )}
                  </span>
                  <span>Uses: {template.usage_count || 0}</span>
                </div>

                {template.variables && template.variables.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-xs text-gray-500 mb-1">Variables:</p>
                    <div className="flex flex-wrap gap-1">
                      {template.variables.map((variable, idx) => (
                        <span
                          key={idx}
                          className="inline-flex items-center px-2 py-0.5 rounded bg-blue-50 text-blue-700 text-xs font-mono"
                        >
                          {`{${variable}}`}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Template Categories Info */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="font-semibold text-blue-900 mb-3">Template Types</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <p className="font-medium text-blue-800 text-sm">SMS Templates</p>
            <p className="text-xs text-blue-700 mt-1">
              Short text messages for quick reminders and notifications
            </p>
          </div>
          <div>
            <p className="font-medium text-purple-800 text-sm">Email Templates</p>
            <p className="text-xs text-purple-700 mt-1">
              Formal email communications with rich formatting
            </p>
          </div>
          <div>
            <p className="font-medium text-green-800 text-sm">Call Scripts</p>
            <p className="text-xs text-green-700 mt-1">
              Guided scripts for collection agents during phone calls
            </p>
          </div>
          <div>
            <p className="font-medium text-yellow-800 text-sm">Field Visit Scripts</p>
            <p className="text-xs text-yellow-700 mt-1">
              Instructions and talking points for field agents
            </p>
          </div>
          <div>
            <p className="font-medium text-red-800 text-sm">Legal Notice Templates</p>
            <p className="text-xs text-red-700 mt-1">
              Formal legal notices with proper formatting and clauses
            </p>
          </div>
          <div>
            <p className="font-medium text-indigo-800 text-sm">Payment Links</p>
            <p className="text-xs text-indigo-700 mt-1">
              Message templates with embedded payment links
            </p>
          </div>
        </div>
      </div>

      {/* Variables Help */}
      <div className="bg-green-50 rounded-lg p-6">
        <h3 className="font-semibold text-green-900 mb-3">Available Variables</h3>
        <p className="text-sm text-green-800 mb-3">
          Use these variables in your templates. They will be replaced with actual values when
          sending:
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="text-xs">
            <code className="bg-white px-2 py-1 rounded text-green-700">{'{customer_name}'}</code>
            <p className="text-green-700 mt-1">Customer name</p>
          </div>
          <div className="text-xs">
            <code className="bg-white px-2 py-1 rounded text-green-700">{'{loan_account}'}</code>
            <p className="text-green-700 mt-1">Loan account ID</p>
          </div>
          <div className="text-xs">
            <code className="bg-white px-2 py-1 rounded text-green-700">{'{due_amount}'}</code>
            <p className="text-green-700 mt-1">Due amount</p>
          </div>
          <div className="text-xs">
            <code className="bg-white px-2 py-1 rounded text-green-700">{'{due_date}'}</code>
            <p className="text-green-700 mt-1">Payment due date</p>
          </div>
          <div className="text-xs">
            <code className="bg-white px-2 py-1 rounded text-green-700">{'{dpd}'}</code>
            <p className="text-green-700 mt-1">Days past due</p>
          </div>
          <div className="text-xs">
            <code className="bg-white px-2 py-1 rounded text-green-700">{'{outstanding}'}</code>
            <p className="text-green-700 mt-1">Total outstanding</p>
          </div>
          <div className="text-xs">
            <code className="bg-white px-2 py-1 rounded text-green-700">{'{payment_link}'}</code>
            <p className="text-green-700 mt-1">Payment URL</p>
          </div>
          <div className="text-xs">
            <code className="bg-white px-2 py-1 rounded text-green-700">{'{contact_number}'}</code>
            <p className="text-green-700 mt-1">Support number</p>
          </div>
        </div>
      </div>
    </div>
  );
}
