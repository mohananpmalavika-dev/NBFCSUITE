'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { settlementApi } from '@/lib/api/collection';
import { SettlementProposal, PaymentTerms } from '@/types/collection';

export default function NewSettlementPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [loanDetails, setLoanDetails] = useState<any>(null);
  const [formData, setFormData] = useState({
    loan_account_id: '',
    customer_id: 0,
    original_outstanding: 0,
    principal_outstanding: 0,
    interest_outstanding: 0,
    penalty_outstanding: 0,
    other_charges: 0,
    settlement_amount: 0,
    waiver_amount: 0,
    waiver_percentage: 0,
    payment_terms: 'lumpsum' as keyof typeof PaymentTerms,
    number_of_installments: 1,
    installment_frequency: 'monthly',
    valid_until: '',
    reason: '',
    justification: '',
    internal_notes: '',
    customer_name: '',
    customer_contact: '',
  });

  const [npvData, setNpvData] = useState({
    estimated_recovery_time: 12,
    estimated_recovery_amount: 0,
    discount_rate: 12,
    npv_without_settlement: 0,
    npv_with_settlement: 0,
    npv_benefit: 0,
  });

  useEffect(() => {
    calculateWaiver();
  }, [formData.original_outstanding, formData.settlement_amount]);

  useEffect(() => {
    if (formData.loan_account_id) {
      fetchLoanDetails();
    }
  }, [formData.loan_account_id]);

  const fetchLoanDetails = async () => {
    try {
      // This would fetch actual loan details from the API
      // For now, we'll simulate it
      setLoanDetails({
        customer_name: 'Sample Customer',
        dpd: 120,
        npa_status: 'substandard',
      });
    } catch (error) {
      console.error('Failed to fetch loan details:', error);
    }
  };

  const calculateWaiver = () => {
    const waiver = formData.original_outstanding - formData.settlement_amount;
    const percentage =
      formData.original_outstanding > 0
        ? (waiver / formData.original_outstanding) * 100
        : 0;

    setFormData((prev) => ({
      ...prev,
      waiver_amount: waiver,
      waiver_percentage: percentage,
    }));
  };

  const calculateNPV = () => {
    const monthsToRecover = npvData.estimated_recovery_time;
    const monthlyRate = npvData.discount_rate / 12 / 100;
    
    // NPV of future recovery without settlement
    const npvWithout =
      npvData.estimated_recovery_amount /
      Math.pow(1 + monthlyRate, monthsToRecover);
    
    // NPV with settlement (immediate payment)
    const npvWith = formData.settlement_amount;
    
    const benefit = npvWith - npvWithout;

    setNpvData((prev) => ({
      ...prev,
      npv_without_settlement: npvWithout,
      npv_with_settlement: npvWith,
      npv_benefit: benefit,
    }));
  };

  const handleSubmit = async (e: React.FormEvent, isDraft = false) => {
    e.preventDefault();
    
    if (!formData.loan_account_id || formData.settlement_amount <= 0) {
      alert('Please fill in all required fields');
      return;
    }

    setLoading(true);
    try {
      const payload = {
        ...formData,
        loan_account_id: parseInt(formData.loan_account_id) || 0,
        customer_id: formData.customer_id || 0,
        status: isDraft ? 'draft' : 'pending_approval',
        npv_analysis: npvData,
      };

      const proposal = await settlementApi.createProposal(payload);
      router.push(`/collections/settlement/${proposal.id}`);
    } catch (error) {
      console.error('Failed to create proposal:', error);
      alert('Failed to create settlement proposal');
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

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            New Settlement Proposal
          </h1>
          <p className="text-gray-600 mt-1">
            Create a new OTS proposal with NPV analysis
          </p>
        </div>
        <button
          onClick={() => router.back()}
          className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          Cancel
        </button>
      </div>

      <form onSubmit={(e) => handleSubmit(e, false)} className="space-y-6">
        {/* Loan Details Section */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Loan Account Details
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Loan Account ID *
              </label>
              <input
                type="text"
                value={formData.loan_account_id}
                onChange={(e) =>
                  setFormData({ ...formData, loan_account_id: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Customer Name
              </label>
              <input
                type="text"
                value={formData.customer_name}
                onChange={(e) =>
                  setFormData({ ...formData, customer_name: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Customer Contact
              </label>
              <input
                type="text"
                value={formData.customer_contact}
                onChange={(e) =>
                  setFormData({ ...formData, customer_contact: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* Outstanding Amount Breakdown */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Outstanding Amount Breakdown
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Principal Outstanding *
              </label>
              <input
                type="number"
                value={formData.principal_outstanding}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    principal_outstanding: parseFloat(e.target.value) || 0,
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Interest Outstanding
              </label>
              <input
                type="number"
                value={formData.interest_outstanding}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    interest_outstanding: parseFloat(e.target.value) || 0,
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Penalty Outstanding
              </label>
              <input
                type="number"
                value={formData.penalty_outstanding}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    penalty_outstanding: parseFloat(e.target.value) || 0,
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Other Charges
              </label>
              <input
                type="number"
                value={formData.other_charges}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    other_charges: parseFloat(e.target.value) || 0,
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Total Original Outstanding *
              </label>
              <input
                type="number"
                value={
                  formData.principal_outstanding +
                  formData.interest_outstanding +
                  formData.penalty_outstanding +
                  formData.other_charges
                }
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    original_outstanding: parseFloat(e.target.value) || 0,
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 font-semibold"
                readOnly
              />
            </div>
          </div>
        </div>

        {/* Settlement Terms */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Settlement Terms
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Settlement Amount *
              </label>
              <input
                type="number"
                value={formData.settlement_amount}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    settlement_amount: parseFloat(e.target.value) || 0,
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Waiver Amount
              </label>
              <input
                type="text"
                value={formatCurrency(formData.waiver_amount)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 font-semibold text-orange-600"
                readOnly
              />
              <p className="text-xs text-gray-500 mt-1">
                {formData.waiver_percentage.toFixed(2)}% discount
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Payment Terms *
              </label>
              <select
                value={formData.payment_terms}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    payment_terms: e.target.value as PaymentTerm,
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="lumpsum">Lump Sum</option>
                <option value="installments">Installments</option>
              </select>
            </div>
            {formData.payment_terms === 'installments' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Number of Installments
                  </label>
                  <input
                    type="number"
                    value={formData.number_of_installments}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        number_of_installments: parseInt(e.target.value) || 1,
                      })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Frequency
                  </label>
                  <select
                    value={formData.installment_frequency}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        installment_frequency: e.target.value,
                      })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                  </select>
                </div>
              </>
            )}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Valid Until
              </label>
              <input
                type="date"
                value={formData.valid_until}
                onChange={(e) =>
                  setFormData({ ...formData, valid_until: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* NPV Analysis */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            NPV Analysis (Optional)
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Est. Recovery Time (months)
              </label>
              <input
                type="number"
                value={npvData.estimated_recovery_time}
                onChange={(e) =>
                  setNpvData({
                    ...npvData,
                    estimated_recovery_time: parseInt(e.target.value) || 12,
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Est. Recovery Amount
              </label>
              <input
                type="number"
                value={npvData.estimated_recovery_amount}
                onChange={(e) =>
                  setNpvData({
                    ...npvData,
                    estimated_recovery_amount: parseFloat(e.target.value) || 0,
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Discount Rate (%)
              </label>
              <input
                type="number"
                value={npvData.discount_rate}
                onChange={(e) =>
                  setNpvData({
                    ...npvData,
                    discount_rate: parseFloat(e.target.value) || 12,
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <button
            type="button"
            onClick={calculateNPV}
            className="mb-4 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            Calculate NPV
          </button>
          {npvData.npv_benefit !== 0 && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-purple-50 rounded-lg">
              <div>
                <p className="text-sm text-gray-600">NPV Without Settlement</p>
                <p className="text-lg font-semibold text-gray-900">
                  {formatCurrency(npvData.npv_without_settlement)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">NPV With Settlement</p>
                <p className="text-lg font-semibold text-gray-900">
                  {formatCurrency(npvData.npv_with_settlement)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">NPV Benefit</p>
                <p
                  className={`text-lg font-semibold ${
                    npvData.npv_benefit > 0 ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {formatCurrency(npvData.npv_benefit)}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Justification */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Justification & Notes
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Reason for Settlement *
              </label>
              <textarea
                value={formData.reason}
                onChange={(e) =>
                  setFormData({ ...formData, reason: e.target.value })
                }
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Brief reason for proposing settlement..."
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Detailed Justification
              </label>
              <textarea
                value={formData.justification}
                onChange={(e) =>
                  setFormData({ ...formData, justification: e.target.value })
                }
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Detailed business justification with NPV analysis..."
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Internal Notes
              </label>
              <textarea
                value={formData.internal_notes}
                onChange={(e) =>
                  setFormData({ ...formData, internal_notes: e.target.value })
                }
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Internal notes (not visible to customer)..."
              />
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3">
          <button
            type="button"
            onClick={() => router.back()}
            className="px-6 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={(e) => handleSubmit(e, true)}
            disabled={loading}
            className="px-6 py-2 text-blue-700 bg-blue-50 border border-blue-300 rounded-lg hover:bg-blue-100 disabled:opacity-50"
          >
            Save as Draft
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Submitting...' : 'Submit for Approval'}
          </button>
        </div>
      </form>
    </div>
  );
}
