'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { legalApi } from '@/lib/api/collection';
import { LegalCase } from '@/types/collection';

export default function LegalCaseDetailPage() {
  const router = useRouter();
  const params = useParams();
  const caseId = params.id as string;

  const [legalCase, setLegalCase] = useState<LegalCase | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCaseDetails();
  }, [caseId]);

  const loadCaseDetails = async () => {
    try {
      setLoading(true);
      const data = await legalApi.getCase(parseInt(caseId));
      setLegalCase(data);
    } catch (error) {
      console.error('Failed to load case details:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      filed: 'bg-blue-100 text-blue-800',
      pending: 'bg-yellow-100 text-yellow-800',
      in_progress: 'bg-purple-100 text-purple-800',
      decree_obtained: 'bg-green-100 text-green-800',
      dismissed: 'bg-red-100 text-red-800',
      settled: 'bg-green-100 text-green-800',
      withdrawn: 'bg-gray-100 text-gray-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getCaseTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      civil: 'Civil Case',
      criminal: 'Criminal Case',
      arbitration: 'Arbitration',
      drt: 'DRT (Debt Recovery Tribunal)',
      sarfaesi: 'SARFAESI',
    };
    return labels[type] || type;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-500">Loading case details...</div>
      </div>
    );
  }

  if (!legalCase) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-gray-500 mb-4">Case not found</p>
          <button
            onClick={() => router.push('/collections/legal')}
            className="text-blue-600 hover:text-blue-700"
          >
            Back to Legal & Recovery
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <button
            onClick={() => router.push('/collections/legal')}
            className="text-blue-600 hover:text-blue-700 mb-2 flex items-center gap-1"
          >
            ← Back to Legal & Recovery
          </button>
          <h1 className="text-2xl font-bold text-gray-900">{legalCase.case_number}</h1>
          <p className="text-gray-600 mt-1">{getCaseTypeLabel(legalCase.case_type)}</p>
        </div>
        <div className="flex gap-3">
          <span className={`px-4 py-2 rounded-lg text-sm font-medium ${getStatusColor(legalCase.status)}`}>
            {legalCase.status.replace('_', ' ').toUpperCase()}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Case Details */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Case Information</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Case Number</p>
                <p className="font-medium text-gray-900">{legalCase.case_number}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Case Type</p>
                <p className="font-medium text-gray-900">{getCaseTypeLabel(legalCase.case_type)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Loan Account</p>
                <p className="font-medium text-gray-900">{legalCase.loan_account_id}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Customer Name</p>
                <p className="font-medium text-gray-900">{legalCase.customer_name || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Claim Amount</p>
                <p className="text-xl font-bold text-red-600">{formatCurrency(legalCase.claim_amount)}</p>
              </div>
              {legalCase.recovery_amount > 0 && (
                <div>
                  <p className="text-sm text-gray-600">Recovery Amount</p>
                  <p className="text-xl font-bold text-green-600">{formatCurrency(legalCase.recovery_amount)}</p>
                </div>
              )}
              <div>
                <p className="text-sm text-gray-600">Filing Date</p>
                <p className="font-medium text-gray-900">{formatDate(legalCase.filing_date)}</p>
              </div>
              {legalCase.decree_date && (
                <div>
                  <p className="text-sm text-gray-600">Decree Date</p>
                  <p className="font-medium text-green-600">{formatDate(legalCase.decree_date)}</p>
                </div>
              )}
            </div>
          </div>

          {/* Court Details */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Court Details</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Court Name</p>
                <p className="font-medium text-gray-900">{legalCase.court_name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Court Location</p>
                <p className="font-medium text-gray-900">{legalCase.court_location || 'N/A'}</p>
              </div>
              {legalCase.judge_name && (
                <div>
                  <p className="text-sm text-gray-600">Judge Name</p>
                  <p className="font-medium text-gray-900">{legalCase.judge_name}</p>
                </div>
              )}
              {legalCase.next_hearing_date && (
                <div>
                  <p className="text-sm text-gray-600">Next Hearing Date</p>
                  <p className="text-lg font-bold text-orange-600">{formatDate(legalCase.next_hearing_date)}</p>
                </div>
              )}
            </div>
          </div>

          {/* Legal Representatives */}
          {(legalCase.advocate_name || legalCase.external_agency) && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Legal Representatives</h2>
              <div className="grid grid-cols-2 gap-4">
                {legalCase.advocate_name && (
                  <>
                    <div>
                      <p className="text-sm text-gray-600">Advocate Name</p>
                      <p className="font-medium text-gray-900">{legalCase.advocate_name}</p>
                    </div>
                    {legalCase.advocate_contact && (
                      <div>
                        <p className="text-sm text-gray-600">Advocate Contact</p>
                        <p className="font-medium text-gray-900">{legalCase.advocate_contact}</p>
                      </div>
                    )}
                  </>
                )}
                {legalCase.external_agency && (
                  <div className="col-span-2">
                    <p className="text-sm text-gray-600">External Agency</p>
                    <p className="font-medium text-gray-900">{legalCase.external_agency}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Case Description */}
          {legalCase.description && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Case Description</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{legalCase.description}</p>
            </div>
          )}

          {/* Hearings */}
          {legalCase.hearings && legalCase.hearings.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Hearing History</h2>
              <div className="space-y-3">
                {legalCase.hearings.map((hearing, index) => (
                  <div key={index} className="p-4 bg-gray-50 rounded-lg border-l-4 border-blue-500">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <p className="font-medium text-gray-900">{formatDate(hearing.hearing_date)}</p>
                        <p className="text-sm text-gray-600">{hearing.purpose}</p>
                      </div>
                      <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        hearing.attended ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {hearing.attended ? 'Attended' : 'Not Attended'}
                      </span>
                    </div>
                    {hearing.outcome && (
                      <div className="mt-2">
                        <p className="text-sm font-medium text-gray-700">Outcome:</p>
                        <p className="text-sm text-gray-600">{hearing.outcome}</p>
                      </div>
                    )}
                    {hearing.next_date && (
                      <p className="text-xs text-orange-600 mt-2">
                        Next hearing: {formatDate(hearing.next_date)}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Documents */}
          {legalCase.documents && legalCase.documents.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Case Documents</h2>
              <div className="space-y-2">
                {legalCase.documents.map((doc, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                        📄
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{doc.name}</p>
                        <p className="text-xs text-gray-500">{doc.type} • {formatDate(doc.uploaded_at)}</p>
                      </div>
                    </div>
                    <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                      Download
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Notes */}
          {legalCase.notes && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Internal Notes</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{legalCase.notes}</p>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Actions</h2>
            <div className="space-y-2">
              <button
                onClick={() => router.push(`/collections/legal/cases/${legalCase.id}/edit`)}
                className="w-full px-4 py-2 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 text-left"
              >
                ✏️ Edit Case
              </button>
              <button
                onClick={() => router.push(`/collections/legal/cases/${legalCase.id}/hearing/new`)}
                className="w-full px-4 py-2 bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 text-left"
              >
                📅 Add Hearing
              </button>
              <button
                onClick={() => alert('Upload document functionality')}
                className="w-full px-4 py-2 bg-green-50 text-green-700 rounded-lg hover:bg-green-100 text-left"
              >
                📎 Upload Document
              </button>
              <button
                onClick={() => alert('Generate report functionality')}
                className="w-full px-4 py-2 bg-yellow-50 text-yellow-700 rounded-lg hover:bg-yellow-100 text-left"
              >
                📊 Generate Report
              </button>
              {legalCase.status === 'decree_obtained' && (
                <button
                  onClick={() => router.push(`/collections/legal/cases/${legalCase.id}/execution`)}
                  className="w-full px-4 py-2 bg-red-50 text-red-700 rounded-lg hover:bg-red-100 text-left"
                >
                  ⚡ Execute Decree
                </button>
              )}
            </div>
          </div>

          {/* Timeline */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Case Timeline</h2>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">Case Filed</p>
                  <p className="text-xs text-gray-600">{formatDate(legalCase.filing_date)}</p>
                </div>
              </div>
              {legalCase.decree_date && (
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-green-600 rounded-full mt-2"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">Decree Obtained</p>
                    <p className="text-xs text-gray-600">{formatDate(legalCase.decree_date)}</p>
                  </div>
                </div>
              )}
              {legalCase.settlement_date && (
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-purple-600 rounded-full mt-2"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">Case Settled</p>
                    <p className="text-xs text-gray-600">{formatDate(legalCase.settlement_date)}</p>
                  </div>
                </div>
              )}
              {legalCase.closure_date && (
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-gray-600 rounded-full mt-2"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">Case Closed</p>
                    <p className="text-xs text-gray-600">{formatDate(legalCase.closure_date)}</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Financial Summary */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Financial Summary</h2>
            <div className="space-y-3">
              <div className="flex justify-between items-center pb-2 border-b">
                <span className="text-sm text-gray-600">Claim Amount</span>
                <span className="font-semibold text-red-600">{formatCurrency(legalCase.claim_amount)}</span>
              </div>
              {legalCase.decree_amount > 0 && (
                <div className="flex justify-between items-center pb-2 border-b">
                  <span className="text-sm text-gray-600">Decree Amount</span>
                  <span className="font-semibold text-blue-600">{formatCurrency(legalCase.decree_amount)}</span>
                </div>
              )}
              {legalCase.recovery_amount > 0 && (
                <div className="flex justify-between items-center pb-2 border-b">
                  <span className="text-sm text-gray-600">Recovery Amount</span>
                  <span className="font-semibold text-green-600">{formatCurrency(legalCase.recovery_amount)}</span>
                </div>
              )}
              {legalCase.legal_expenses > 0 && (
                <div className="flex justify-between items-center pb-2 border-b">
                  <span className="text-sm text-gray-600">Legal Expenses</span>
                  <span className="font-semibold text-gray-900">{formatCurrency(legalCase.legal_expenses)}</span>
                </div>
              )}
              {legalCase.recovery_amount > 0 && (
                <div className="flex justify-between items-center pt-2">
                  <span className="text-sm font-medium text-gray-700">Recovery %</span>
                  <span className="font-bold text-gray-900">
                    {((legalCase.recovery_amount / legalCase.claim_amount) * 100).toFixed(1)}%
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Status */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Case Status</h2>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Current Status</span>
                <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(legalCase.status)}`}>
                  {legalCase.status.replace('_', ' ').toUpperCase()}
                </span>
              </div>
              {legalCase.next_hearing_date && (
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Next Hearing</span>
                  <span className="text-sm font-medium text-orange-600">
                    {formatDate(legalCase.next_hearing_date)}
                  </span>
                </div>
              )}
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Days Open</span>
                <span className="text-sm font-medium text-gray-900">
                  {Math.floor((new Date().getTime() - new Date(legalCase.filing_date).getTime()) / (1000 * 60 * 60 * 24))}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
