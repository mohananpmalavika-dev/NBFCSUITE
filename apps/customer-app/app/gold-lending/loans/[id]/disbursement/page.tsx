'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../../goldApi';
import { useParams, useRouter } from 'next/navigation';

interface Application {
  id: string;
  application_number: string;
  customer_id: string;
  sanctioned_amount: number;
  status: string;
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
  beneficiary_name?: string;
}

export default function DisbursementPage() {
  const params = useParams();
  const router = useRouter();
  const applicationId = params.id as string;

  const [application, setApplication] = useState<Application | null>(null);
  const [disbursements, setDisbursements] = useState<Disbursement[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Form state
  const [showForm, setShowForm] = useState(false);
  const [amount, setAmount] = useState('');
  const [mode, setMode] = useState('neft');
  const [accountNumber, setAccountNumber] = useState('');
  const [ifscCode, setIfscCode] = useState('');
  const [beneficiaryName, setBeneficiaryName] = useState('');
  const [upiId, setUpiId] = useState('');
  const [chequeNumber, setChequeNumber] = useState('');
  const [remarks, setRemarks] = useState('');

  useEffect(() => {
    loadData();
  }, [applicationId]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [appData, disbData] = await Promise.all([
        goldApi.getLoanApplication(applicationId),
        goldApi.getApplicationDisbursements(applicationId),
      ]);
      
      setApplication(appData);
      setDisbursements(disbData);
      
      if (!amount && appData.sanctioned_amount) {
        setAmount(appData.sanctioned_amount.toString());
      }

      setError('');
    } catch (err: any) {
      setError(err.message || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDisbursement = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!amount || parseFloat(amount) <= 0) {
      setError('Valid amount is required');
      return;
    }

    if (!mode) {
      setError('Disbursement mode is required');
      return;
    }

    if (['neft', 'imps', 'rtgs'].includes(mode)) {
      if (!accountNumber || !ifscCode || !beneficiaryName) {
        setError('Bank details are required for this mode');
        return;
      }
    }

    if (mode === 'upi' && !upiId) {
      setError('UPI ID is required');
      return;
    }

    if (mode === 'cheque' && !chequeNumber) {
      setError('Cheque number is required');
      return;
    }

    try {
      setCreating(true);
      setError('');

      const payload: any = {
        application_id: applicationId,
        disbursement_amount: parseFloat(amount),
        disbursement_mode: mode,
        initiated_by_user_id: 'current-user-id',
      };

      if (accountNumber) payload.account_number = accountNumber;
      if (ifscCode) payload.ifsc_code = ifscCode;
      if (beneficiaryName) payload.beneficiary_name = beneficiaryName;
      if (upiId) payload.upi_id = upiId;
      if (chequeNumber) payload.cheque_number = chequeNumber;
      if (remarks) payload.remarks = remarks;

      await goldApi.createDisbursement(payload);
      
      setSuccess('Disbursement created successfully!');
      setShowForm(false);
      resetForm();
      await loadData();
    } catch (err: any) {
      setError(err.message || 'Failed to create disbursement');
    } finally {
      setCreating(false);
    }
  };

  const resetForm = () => {
    setMode('neft');
    setAccountNumber('');
    setIfscCode('');
    setBeneficiaryName('');
    setUpiId('');
    setChequeNumber('');
    setRemarks('');
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
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => router.push(`/gold-lending/loans/${applicationId}`)}
            className="text-gray-600 hover:text-gray-900 mb-4"
          >
            ← Back to Application
          </button>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Loan Disbursement</h1>
              <p className="text-gray-600 mt-1">
                Application: {application?.application_number}
              </p>
            </div>
            {application?.status === 'approved' && !showForm && (
              <button
                onClick={() => setShowForm(true)}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                + Create Disbursement
              </button>
            )}
          </div>
        </div>

        {/* Messages */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
            {success}
          </div>
        )}

        {/* Application Summary */}
        {application && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-blue-700">Customer ID:</span>
                <span className="ml-2 font-medium text-blue-900">{application.customer_id}</span>
              </div>
              <div>
                <span className="text-blue-700">Sanctioned Amount:</span>
                <span className="ml-2 font-bold text-blue-900">
                  {formatAmount(application.sanctioned_amount)}
                </span>
              </div>
              <div>
                <span className="text-blue-700">Status:</span>
                <span className="ml-2 font-medium text-blue-900">{application.status}</span>
              </div>
            </div>
          </div>
        )}

        {/* Create Disbursement Form */}
        {showForm && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Create New Disbursement</h2>
              <button
                onClick={() => {
                  setShowForm(false);
                  resetForm();
                }}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateDisbursement} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Amount (₹) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    placeholder="Enter amount"
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Mode <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={mode}
                    onChange={(e) => setMode(e.target.value)}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="neft">NEFT</option>
                    <option value="imps">IMPS</option>
                    <option value="rtgs">RTGS</option>
                    <option value="upi">UPI</option>
                    <option value="cheque">Cheque</option>
                    <option value="cash">Cash</option>
                  </select>
                </div>
              </div>

              {/* Bank Details for NEFT/IMPS/RTGS */}
              {['neft', 'imps', 'rtgs'].includes(mode) && (
                <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-medium text-gray-900">Bank Details</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Account Number <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        value={accountNumber}
                        onChange={(e) => setAccountNumber(e.target.value)}
                        placeholder="Account number"
                        required
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        IFSC Code <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        value={ifscCode}
                        onChange={(e) => setIfscCode(e.target.value)}
                        placeholder="IFSC code"
                        required
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Beneficiary Name <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        value={beneficiaryName}
                        onChange={(e) => setBeneficiaryName(e.target.value)}
                        placeholder="Account holder name"
                        required
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* UPI Details */}
              {mode === 'upi' && (
                <div className="p-4 bg-gray-50 rounded-lg">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    UPI ID <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={upiId}
                    onChange={(e) => setUpiId(e.target.value)}
                    placeholder="example@upi"
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              )}

              {/* Cheque Details */}
              {mode === 'cheque' && (
                <div className="p-4 bg-gray-50 rounded-lg">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Cheque Number <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={chequeNumber}
                    onChange={(e) => setChequeNumber(e.target.value)}
                    placeholder="Cheque number"
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Remarks</label>
                <textarea
                  value={remarks}
                  onChange={(e) => setRemarks(e.target.value)}
                  placeholder="Additional remarks"
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
                <button
                  type="button"
                  onClick={() => {
                    setShowForm(false);
                    resetForm();
                  }}
                  disabled={creating}
                  className="px-6 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-300 flex items-center gap-2"
                >
                  {creating && (
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  )}
                  {creating ? 'Creating...' : 'Create Disbursement'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Disbursements List */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Disbursement History</h2>
          
          {disbursements.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-400 text-5xl mb-4">💰</div>
              <p className="text-gray-600 text-lg">No disbursements yet</p>
              <p className="text-gray-500 text-sm mt-2">
                Create a disbursement to transfer funds to the customer
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {disbursements.map(disbursement => (
                <div key={disbursement.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <div className="font-bold text-2xl text-gray-900">
                        {formatAmount(disbursement.disbursement_amount)}
                      </div>
                      <div className="text-sm text-gray-600 mt-1">
                        Mode: {disbursement.disbursement_mode.toUpperCase()}
                      </div>
                    </div>
                    <span className={`px-3 py-1 text-xs font-medium rounded-full ${
                      disbursement.disbursement_status === 'completed' ? 'bg-green-100 text-green-800' :
                      disbursement.disbursement_status === 'failed' ? 'bg-red-100 text-red-800' :
                      disbursement.disbursement_status === 'pending_verification' ? 'bg-yellow-100 text-yellow-800' :
                      disbursement.disbursement_status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {disbursement.disbursement_status.toUpperCase().replace('_', ' ')}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-3 text-sm">
                    {disbursement.utr_number && (
                      <div>
                        <span className="text-gray-600">UTR Number:</span>
                        <span className="ml-2 font-medium text-gray-900">{disbursement.utr_number}</span>
                      </div>
                    )}
                    {disbursement.account_number && (
                      <div>
                        <span className="text-gray-600">Account:</span>
                        <span className="ml-2 font-medium text-gray-900">
                          {disbursement.account_number}
                        </span>
                      </div>
                    )}
                    {disbursement.ifsc_code && (
                      <div>
                        <span className="text-gray-600">IFSC:</span>
                        <span className="ml-2 font-medium text-gray-900">{disbursement.ifsc_code}</span>
                      </div>
                    )}
                    {disbursement.beneficiary_name && (
                      <div>
                        <span className="text-gray-600">Beneficiary:</span>
                        <span className="ml-2 font-medium text-gray-900">{disbursement.beneficiary_name}</span>
                      </div>
                    )}
                    {disbursement.disbursement_date && (
                      <div className="col-span-2">
                        <span className="text-gray-600">Disbursed On:</span>
                        <span className="ml-2 font-medium text-gray-900">
                          {formatDate(disbursement.disbursement_date)}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
