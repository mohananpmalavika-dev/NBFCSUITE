'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../../goldApi';
import { useParams, useRouter } from 'next/navigation';

interface CreditEvaluation {
  id: string;
  application_id: string;
  cibil_score?: number;
  cibil_report_id?: string;
  ltv_ratio: number;
  debt_to_income_ratio?: number;
  existing_loans_count?: number;
  existing_loans_amount?: number;
  collateral_quality_score?: number;
  ai_recommended_amount?: number;
  ai_confidence_score?: number;
  risk_category: string;
  risk_score?: number;
  evaluation_status: string;
  evaluated_by_user_id?: string;
  evaluation_date?: string;
  remarks?: string;
}

interface Application {
  id: string;
  application_number: string;
  customer_id: string;
  requested_amount: number;
  status: string;
}

export default function CreditEvaluationPage() {
  const params = useParams();
  const router = useRouter();
  const applicationId = params.id as string;

  const [application, setApplication] = useState<Application | null>(null);
  const [evaluation, setEvaluation] = useState<CreditEvaluation | null>(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Form fields
  const [cibilScore, setCibilScore] = useState('');
  const [cibilReportId, setCibilReportId] = useState('');
  const [ltvRatio, setLtvRatio] = useState('');
  const [debtToIncome, setDebtToIncome] = useState('');
  const [existingLoansCount, setExistingLoansCount] = useState('');
  const [existingLoansAmount, setExistingLoansAmount] = useState('');
  const [collateralQuality, setCollateralQuality] = useState('');
  const [aiAmount, setAiAmount] = useState('');
  const [aiConfidence, setAiConfidence] = useState('');
  const [riskCategory, setRiskCategory] = useState('medium');
  const [riskScore, setRiskScore] = useState('');
  const [remarks, setRemarks] = useState('');

  useEffect(() => {
    loadData();
  }, [applicationId]);

  const loadData = async () => {
    try {
      setLoading(true);
      const appData = await goldApi.getLoanApplication(applicationId);
      setApplication(appData);

      try {
        const evalData = await goldApi.getApplicationCreditEvaluation(applicationId);
        setEvaluation(evalData);
        populateForm(evalData);
      } catch (err) {
        console.log('No existing evaluation');
      }

      setError('');
    } catch (err: any) {
      setError(err.message || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const populateForm = (eval: CreditEvaluation) => {
    if (eval.cibil_score) setCibilScore(eval.cibil_score.toString());
    if (eval.cibil_report_id) setCibilReportId(eval.cibil_report_id);
    setLtvRatio(eval.ltv_ratio.toString());
    if (eval.debt_to_income_ratio) setDebtToIncome(eval.debt_to_income_ratio.toString());
    if (eval.existing_loans_count) setExistingLoansCount(eval.existing_loans_count.toString());
    if (eval.existing_loans_amount) setExistingLoansAmount(eval.existing_loans_amount.toString());
    if (eval.collateral_quality_score) setCollateralQuality(eval.collateral_quality_score.toString());
    if (eval.ai_recommended_amount) setAiAmount(eval.ai_recommended_amount.toString());
    if (eval.ai_confidence_score) setAiConfidence(eval.ai_confidence_score.toString());
    setRiskCategory(eval.risk_category);
    if (eval.risk_score) setRiskScore(eval.risk_score.toString());
    if (eval.remarks) setRemarks(eval.remarks);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!ltvRatio || parseFloat(ltvRatio) <= 0) {
      setError('LTV ratio is required');
      return;
    }

    try {
      setCreating(true);
      setError('');

      const payload: any = {
        application_id: applicationId,
        ltv_ratio: parseFloat(ltvRatio),
        risk_category: riskCategory,
        evaluated_by_user_id: 'current-user-id',
      };

      if (cibilScore) payload.cibil_score = parseInt(cibilScore);
      if (cibilReportId) payload.cibil_report_id = cibilReportId;
      if (debtToIncome) payload.debt_to_income_ratio = parseFloat(debtToIncome);
      if (existingLoansCount) payload.existing_loans_count = parseInt(existingLoansCount);
      if (existingLoansAmount) payload.existing_loans_amount = parseFloat(existingLoansAmount);
      if (collateralQuality) payload.collateral_quality_score = parseFloat(collateralQuality);
      if (aiAmount) payload.ai_recommended_amount = parseFloat(aiAmount);
      if (aiConfidence) payload.ai_confidence_score = parseFloat(aiConfidence);
      if (riskScore) payload.risk_score = parseFloat(riskScore);
      if (remarks) payload.remarks = remarks;

      await goldApi.createCreditEvaluation(payload);
      
      setSuccess('Credit evaluation saved successfully!');
      setTimeout(() => {
        router.push(`/gold-lending/loans/${applicationId}`);
      }, 2000);
    } catch (err: any) {
      setError(err.message || 'Failed to save evaluation');
    } finally {
      setCreating(false);
    }
  };

  const formatAmount = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
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
          <h1 className="text-3xl font-bold text-gray-900">Credit Evaluation</h1>
          <p className="text-gray-600 mt-1">
            Application: {application?.application_number}
          </p>
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
                <span className="text-blue-700">Requested Amount:</span>
                <span className="ml-2 font-medium text-blue-900">
                  {formatAmount(application.requested_amount)}
                </span>
              </div>
              <div>
                <span className="text-blue-700">Status:</span>
                <span className="ml-2 font-medium text-blue-900">{application.status}</span>
              </div>
            </div>
          </div>
        )}

        {/* Evaluation Form */}
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-sm p-6 space-y-6">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Credit Bureau Data</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">CIBIL Score</label>
                <input
                  type="number"
                  value={cibilScore}
                  onChange={(e) => setCibilScore(e.target.value)}
                  placeholder="e.g., 750"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">CIBIL Report ID</label>
                <input
                  type="text"
                  value={cibilReportId}
                  onChange={(e) => setCibilReportId(e.target.value)}
                  placeholder="Report reference ID"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Financial Assessment</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  LTV Ratio (%) <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={ltvRatio}
                  onChange={(e) => setLtvRatio(e.target.value)}
                  placeholder="e.g., 75.00"
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Debt to Income Ratio (%)</label>
                <input
                  type="number"
                  step="0.01"
                  value={debtToIncome}
                  onChange={(e) => setDebtToIncome(e.target.value)}
                  placeholder="e.g., 40.00"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Existing Loans Count</label>
                <input
                  type="number"
                  value={existingLoansCount}
                  onChange={(e) => setExistingLoansCount(e.target.value)}
                  placeholder="Number of loans"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Existing Loans Amount (₹)</label>
                <input
                  type="number"
                  value={existingLoansAmount}
                  onChange={(e) => setExistingLoansAmount(e.target.value)}
                  placeholder="Total outstanding"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Collateral Quality Score</label>
                <input
                  type="number"
                  step="0.01"
                  value={collateralQuality}
                  onChange={(e) => setCollateralQuality(e.target.value)}
                  placeholder="0-100"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">AI Recommendation</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">AI Recommended Amount (₹)</label>
                <input
                  type="number"
                  value={aiAmount}
                  onChange={(e) => setAiAmount(e.target.value)}
                  placeholder="AI suggested amount"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">AI Confidence Score</label>
                <input
                  type="number"
                  step="0.01"
                  value={aiConfidence}
                  onChange={(e) => setAiConfidence(e.target.value)}
                  placeholder="0.00 - 1.00"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Risk Assessment</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Risk Category <span className="text-red-500">*</span>
                </label>
                <select
                  value={riskCategory}
                  onChange={(e) => setRiskCategory(e.target.value)}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="very_low">Very Low</option>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="very_high">Very High</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Risk Score</label>
                <input
                  type="number"
                  step="0.01"
                  value={riskScore}
                  onChange={(e) => setRiskScore(e.target.value)}
                  placeholder="0-100"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Remarks</label>
            <textarea
              value={remarks}
              onChange={(e) => setRemarks(e.target.value)}
              placeholder="Additional evaluation notes"
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={() => router.push(`/gold-lending/loans/${applicationId}`)}
              disabled={creating}
              className="px-6 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={creating}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 flex items-center gap-2"
            >
              {creating && (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              )}
              {creating ? 'Saving...' : 'Save Evaluation'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
