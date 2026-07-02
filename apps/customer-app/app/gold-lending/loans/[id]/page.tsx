'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';

interface LoanApplication {
  id: string;
  application_number: string;
  customer_id: string;
  product_id: string;
  branch_id: string;
  requested_amount: number;
  eligible_amount?: number;
  sanctioned_amount?: number;
  requested_tenure_months: number;
  approved_tenure_months?: number;
  purpose?: string;
  status: string;
  stage: string;
  created_at: string;
  submitted_at?: string;
  approved_at?: string;
  rejected_at?: string;
  remarks?: string;
  rejection_reason?: string;
}

interface Ornament {
  id: string;
  ornament_code: string;
  ornament_type: string;
  net_weight: number;
  purity_karat: number;
  appraised_value: number;
}

interface CreditEvaluation {
  id: string;
  cibil_score?: number;
  ai_recommended_amount?: number;
  ai_confidence_score?: number;
  risk_category: string;
  evaluation_status: string;
}

interface Approval {
  id: string;
  approval_level: number;
  approver_user_id?: string;
  approver_role: string;
  decision?: string;
  decision_date?: string;
  comments?: string;
  created_at: string;
}

interface Disbursement {
  id: string;
  disbursement_amount: number;
  disbursement_mode: string;
  disbursement_status: string;
  disbursement_date?: string;
  utr_number?: string;
  account_number?: string;
  ifsc_code?: string;
}

export default function LoanApplicationDetailPage() {
  const params = useParams();
  const router = useRouter();
  const applicationId = params.id as string;

  const [application, setApplication] = useState<LoanApplication | null>(null);
  const [ornaments, setOrnaments] = useState<Ornament[]>([]);
  const [creditEval, setCreditEval] = useState<CreditEvaluation | null>(null);
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [disbursements, setDisbursements] = useState<Disbursement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');

  // Action modals
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [showUpdateModal, setShowUpdateModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadApplicationData();
  }, [applicationId]);

  const loadApplicationData = async () => {
    try {
      setLoading(true);
      const [appData, ornamentsData] = await Promise.all([
        goldApi.getLoanApplication(applicationId),
        goldApi.getApplicationOrnaments(applicationId),
      ]);
      
      setApplication(appData);
      setOrnaments(ornamentsData);

      // Load credit evaluation if available
      if (appData.stage !== 'application' && appData.stage !== 'draft') {
        try {
          const evalData = await goldApi.getApplicationCreditEvaluation(applicationId);
          setCreditEval(evalData);
        } catch (err) {
          console.log('No credit evaluation yet');
        }
      }

      // Load approvals if submitted
      if (appData.status !== 'draft') {
        try {
          const approvalsData = await goldApi.getApplicationApprovals(applicationId);
          setApprovals(approvalsData);
        } catch (err) {
          console.log('No approvals yet');
        }
      }

      // Load disbursements if approved
      if (appData.status === 'approved' || appData.status === 'disbursed') {
        try {
          const disbData = await goldApi.getApplicationDisbursements(applicationId);
          setDisbursements(disbData);
        } catch (err) {
          console.log('No disbursements yet');
        }
      }

      setError('');
    } catch (err: any) {
      setError(err.message || 'Failed to load application');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitApplication = async () => {
    try {
      setSubmitting(true);
      await goldApi.submitLoanApplication(applicationId, 'current-user-id');
      await loadApplicationData();
      setShowSubmitModal(false);
    } catch (err: any) {
      setError(err.message || 'Failed to submit application');
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusBadgeClass = (status: string) => {
    const classes: Record<string, string> = {
      'draft': 'bg-gray-100 text-gray-800',
      'submitted': 'bg-blue-100 text-blue-800',
      'under_review': 'bg-yellow-100 text-yellow-800',
      'approved': 'bg-green-100 text-green-800',
      'rejected': 'bg-red-100 text-red-800',
      'disbursed': 'bg-purple-100 text-purple-800',
    };
    return classes[status] || 'bg-gray-100 text-gray-800';
  };

  const formatAmount = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading application...</p>
        </div>
      </div>
    );
  }

  if (error || !application) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error || 'Application not found'}
          </div>
        </div>
      </div>
    );
  }

  const totalCollateralValue = ornaments.reduce((sum, o) => sum + o.appraised_value, 0);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.push('/gold-lending/loans')}
                className="text-gray-600 hover:text-gray-900"
              >
                ← Back
              </button>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">{application.application_number}</h1>
                <p className="text-gray-600 mt-1">Loan Application Details</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className={`px-3 py-1 text-sm font-medium rounded-full ${getStatusBadgeClass(application.status)}`}>
                {application.status.replace('_', ' ').toUpperCase()}
              </span>
              {application.status === 'draft' && (
                <button
                  onClick={() => setShowSubmitModal(true)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Submit Application
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 mb-1">Requested Amount</div>
            <div className="text-2xl font-bold text-blue-600">
              {formatAmount(application.requested_amount)}
            </div>
          </div>
          {application.sanctioned_amount && (
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-600 mb-1">Sanctioned Amount</div>
              <div className="text-2xl font-bold text-green-600">
                {formatAmount(application.sanctioned_amount)}
              </div>
            </div>
          )}
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 mb-1">Collateral Value</div>
            <div className="text-2xl font-bold text-gray-900">
              {formatAmount(totalCollateralValue)}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 mb-1">LTV Ratio</div>
            <div className="text-2xl font-bold text-gray-900">
              {((application.requested_amount / totalCollateralValue) * 100).toFixed(1)}%
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              {['overview', 'ornaments', 'credit', 'approvals', 'disbursement'].map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-6 py-3 text-sm font-medium border-b-2 ${
                    activeTab === tab
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-sm font-medium text-gray-500 mb-3">Application Details</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Customer ID:</span>
                        <span className="font-medium text-gray-900">{application.customer_id}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Branch ID:</span>
                        <span className="font-medium text-gray-900">{application.branch_id}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Product ID:</span>
                        <span className="font-medium text-gray-900">{application.product_id}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Tenure:</span>
                        <span className="font-medium text-gray-900">{application.requested_tenure_months} months</span>
                      </div>
                      {application.purpose && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">Purpose:</span>
                          <span className="font-medium text-gray-900">{application.purpose}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  <div>
                    <h3 className="text-sm font-medium text-gray-500 mb-3">Timeline</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Created:</span>
                        <span className="font-medium text-gray-900">{formatDate(application.created_at)}</span>
                      </div>
                      {application.submitted_at && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">Submitted:</span>
                          <span className="font-medium text-gray-900">{formatDate(application.submitted_at)}</span>
                        </div>
                      )}
                      {application.approved_at && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">Approved:</span>
                          <span className="font-medium text-gray-900">{formatDate(application.approved_at)}</span>
                        </div>
                      )}
                      {application.rejected_at && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">Rejected:</span>
                          <span className="font-medium text-red-600">{formatDate(application.rejected_at)}</span>
                        </div>
                      )}
                      <div className="flex justify-between">
                        <span className="text-gray-600">Current Stage:</span>
                        <span className="font-medium text-blue-600">{application.stage.replace('_', ' ').toUpperCase()}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {application.remarks && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-500 mb-2">Remarks</h3>
                    <p className="text-sm text-gray-700 bg-gray-50 rounded p-3">{application.remarks}</p>
                  </div>
                )}

                {application.rejection_reason && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <h3 className="text-sm font-medium text-red-800 mb-2">Rejection Reason</h3>
                    <p className="text-sm text-red-700">{application.rejection_reason}</p>
                  </div>
                )}

                {/* Quick Actions */}
                <div className="flex gap-3 pt-4 border-t border-gray-200">
                  {application.stage === 'credit_evaluation' && (
                    <Link
                      href={`/gold-lending/loans/${applicationId}/credit`}
                      className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
                    >
                      View Credit Evaluation
                    </Link>
                  )}
                  {application.status === 'approved' && (
                    <Link
                      href={`/gold-lending/loans/${applicationId}/disbursement`}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                    >
                      Process Disbursement
                    </Link>
                  )}
                </div>
              </div>
            )}

            {/* Ornaments Tab */}
            {activeTab === 'ornaments' && (
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Pledged Ornaments ({ornaments.length})
                </h3>
                {ornaments.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">No ornaments pledged</p>
                ) : (
                  <div className="space-y-3">
                    {ornaments.map(ornament => (
                      <div key={ornament.id} className="bg-gray-50 rounded-lg p-4">
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="font-medium text-gray-900">{ornament.ornament_code}</div>
                            <div className="text-sm text-gray-600 mt-1">{ornament.ornament_type}</div>
                            <div className="text-sm text-gray-600 mt-1">
                              {ornament.net_weight}g @ {ornament.purity_karat}K
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-bold text-gray-900">{formatAmount(ornament.appraised_value)}</div>
                            <div className="text-xs text-gray-500 mt-1">Appraised Value</div>
                          </div>
                        </div>
                      </div>
                    ))}
                    <div className="bg-blue-50 rounded-lg p-4 flex justify-between items-center">
                      <span className="font-medium text-blue-900">Total Collateral Value</span>
                      <span className="text-xl font-bold text-blue-600">{formatAmount(totalCollateralValue)}</span>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Credit Evaluation Tab */}
            {activeTab === 'credit' && (
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Credit Evaluation</h3>
                {!creditEval ? (
                  <div className="text-center py-8">
                    <p className="text-gray-500 mb-4">No credit evaluation performed yet</p>
                    {application.status === 'submitted' && (
                      <Link
                        href={`/gold-lending/loans/${applicationId}/credit`}
                        className="inline-block px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
                      >
                        Perform Credit Evaluation
                      </Link>
                    )}
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      {creditEval.cibil_score && (
                        <div className="bg-gray-50 rounded-lg p-4">
                          <div className="text-sm text-gray-600 mb-1">CIBIL Score</div>
                          <div className="text-2xl font-bold text-gray-900">{creditEval.cibil_score}</div>
                        </div>
                      )}
                      <div className="bg-gray-50 rounded-lg p-4">
                        <div className="text-sm text-gray-600 mb-1">Risk Category</div>
                        <div className="text-xl font-bold text-gray-900">{creditEval.risk_category.toUpperCase()}</div>
                      </div>
                      {creditEval.ai_recommended_amount && (
                        <div className="bg-blue-50 rounded-lg p-4">
                          <div className="text-sm text-blue-600 mb-1">AI Recommended Amount</div>
                          <div className="text-xl font-bold text-blue-900">
                            {formatAmount(creditEval.ai_recommended_amount)}
                          </div>
                        </div>
                      )}
                      {creditEval.ai_confidence_score && (
                        <div className="bg-green-50 rounded-lg p-4">
                          <div className="text-sm text-green-600 mb-1">AI Confidence</div>
                          <div className="text-xl font-bold text-green-900">
                            {(creditEval.ai_confidence_score * 100).toFixed(1)}%
                          </div>
                        </div>
                      )}
                    </div>
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <div className="font-medium text-yellow-900">Status: {creditEval.evaluation_status}</div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Approvals Tab */}
            {activeTab === 'approvals' && (
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Approval Workflow</h3>
                {approvals.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">No approval records yet</p>
                ) : (
                  <div className="space-y-3">
                    {approvals.map(approval => (
                      <div key={approval.id} className="bg-gray-50 rounded-lg p-4">
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="font-medium text-gray-900">Level {approval.approval_level}</div>
                            <div className="text-sm text-gray-600 mt-1">Role: {approval.approver_role}</div>
                            {approval.approver_user_id && (
                              <div className="text-sm text-gray-600">Approver: {approval.approver_user_id}</div>
                            )}
                            {approval.comments && (
                              <div className="text-sm text-gray-700 mt-2 italic">"{approval.comments}"</div>
                            )}
                          </div>
                          <div className="text-right">
                            {approval.decision ? (
                              <>
                                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                                  approval.decision === 'approved' ? 'bg-green-100 text-green-800' :
                                  approval.decision === 'rejected' ? 'bg-red-100 text-red-800' :
                                  'bg-yellow-100 text-yellow-800'
                                }`}>
                                  {approval.decision.toUpperCase()}
                                </span>
                                {approval.decision_date && (
                                  <div className="text-xs text-gray-500 mt-1">
                                    {formatDate(approval.decision_date)}
                                  </div>
                                )}
                              </>
                            ) : (
                              <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">
                                PENDING
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Disbursement Tab */}
            {activeTab === 'disbursement' && (
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Disbursements</h3>
                {disbursements.length === 0 ? (
                  <div className="text-center py-8">
                    <p className="text-gray-500 mb-4">No disbursements yet</p>
                    {application.status === 'approved' && (
                      <Link
                        href={`/gold-lending/loans/${applicationId}/disbursement`}
                        className="inline-block px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                      >
                        Create Disbursement
                      </Link>
                    )}
                  </div>
                ) : (
                  <div className="space-y-3">
                    {disbursements.map(disbursement => (
                      <div key={disbursement.id} className="bg-gray-50 rounded-lg p-4">
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="font-bold text-gray-900">
                              {formatAmount(disbursement.disbursement_amount)}
                            </div>
                            <div className="text-sm text-gray-600 mt-1">
                              Mode: {disbursement.disbursement_mode.toUpperCase()}
                            </div>
                            {disbursement.utr_number && (
                              <div className="text-sm text-gray-600">UTR: {disbursement.utr_number}</div>
                            )}
                            {disbursement.account_number && (
                              <div className="text-sm text-gray-600">
                                Account: {disbursement.account_number}
                                {disbursement.ifsc_code && ` (${disbursement.ifsc_code})`}
                              </div>
                            )}
                            {disbursement.disbursement_date && (
                              <div className="text-sm text-gray-600 mt-1">
                                Date: {formatDate(disbursement.disbursement_date)}
                              </div>
                            )}
                          </div>
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                            disbursement.disbursement_status === 'completed' ? 'bg-green-100 text-green-800' :
                            disbursement.disbursement_status === 'failed' ? 'bg-red-100 text-red-800' :
                            disbursement.disbursement_status === 'pending_verification' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {disbursement.disbursement_status.toUpperCase().replace('_', ' ')}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Submit Modal */}
        {showSubmitModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Submit Application</h3>
              <p className="text-gray-600 mb-6">
                Are you sure you want to submit this application? Once submitted, it cannot be edited.
              </p>
              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setShowSubmitModal(false)}
                  disabled={submitting}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSubmitApplication}
                  disabled={submitting}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300"
                >
                  {submitting ? 'Submitting...' : 'Submit'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
