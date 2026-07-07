'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { treasuryService, CashPositionCreate, DenominationBreakup } from '@/services/treasury.service';

export default function RecordCashPositionPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showDenomination, setShowDenomination] = useState(false);

  const today = new Date().toISOString().split('T')[0];

  const [formData, setFormData] = useState<CashPositionCreate>({
    position_date: today,
    opening_balance: 0,
    cash_received: 0,
    cash_paid: 0,
    bank_deposit: 0,
    bank_withdrawal: 0,
    discrepancy_amount: 0,
    notes: '',
    status: 'draft'
  });

  const [denomination, setDenomination] = useState<DenominationBreakup>({
    notes_2000: 0,
    notes_500: 0,
    notes_200: 0,
    notes_100: 0,
    notes_50: 0,
    notes_20: 0,
    notes_10: 0,
    coins_10: 0,
    coins_5: 0,
    coins_2: 0,
    coins_1: 0
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'number') {
      setFormData(prev => ({ ...prev, [name]: parseFloat(value) || 0 }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleDenominationChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setDenomination(prev => ({ ...prev, [name]: parseInt(value) || 0 }));
  };

  const calculateClosingBalance = () => {
    return (
      formData.opening_balance +
      formData.cash_received +
      formData.bank_withdrawal -
      formData.cash_paid -
      formData.bank_deposit
    );
  };

  const calculateDenominationTotal = () => {
    return (
      denomination.notes_2000 * 2000 +
      denomination.notes_500 * 500 +
      denomination.notes_200 * 200 +
      denomination.notes_100 * 100 +
      denomination.notes_50 * 50 +
      denomination.notes_20 * 20 +
      denomination.notes_10 * 10 +
      denomination.coins_10 * 10 +
      denomination.coins_5 * 5 +
      denomination.coins_2 * 2 +
      denomination.coins_1 * 1
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const dataToSubmit = {
        ...formData,
        closing_balance: calculateClosingBalance(),
        denomination_details: showDenomination ? denomination : undefined
      };

      const position = await treasuryService.createCashPosition(dataToSubmit);
      router.push(`/treasury/cash-position`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to record cash position');
      setLoading(false);
    }
  };

  const handleCancel = () => {
    router.push('/treasury/cash-position');
  };

  const closingBalance = calculateClosingBalance();
  const denominationTotal = calculateDenominationTotal();
  const hasDiscrepancy = showDenomination && Math.abs(closingBalance - denominationTotal) > 0.01;

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Record Cash Position</h1>
        <p className="text-sm text-gray-600 mt-1">Enter daily cash position details</p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white shadow rounded-lg">
        <div className="p-6 space-y-6">
          {/* Basic Details */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Basic Details</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="position_date" className="block text-sm font-medium text-gray-700 mb-1">
                  Position Date <span className="text-red-500">*</span>
                </label>
                <input
                  type="date"
                  id="position_date"
                  name="position_date"
                  value={formData.position_date}
                  onChange={handleChange}
                  required
                  max={today}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label htmlFor="vault_location" className="block text-sm font-medium text-gray-700 mb-1">
                  Vault Location
                </label>
                <input
                  type="text"
                  id="vault_location"
                  name="vault_location"
                  value={formData.vault_location || ''}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Main Branch Vault"
                />
              </div>
            </div>
          </div>

          {/* Cash Movements */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Cash Movements</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="opening_balance" className="block text-sm font-medium text-gray-700 mb-1">
                  Opening Balance <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  id="opening_balance"
                  name="opening_balance"
                  value={formData.opening_balance}
                  onChange={handleChange}
                  required
                  step="0.01"
                  min="0"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label htmlFor="cash_received" className="block text-sm font-medium text-gray-700 mb-1">
                  Cash Received <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  id="cash_received"
                  name="cash_received"
                  value={formData.cash_received}
                  onChange={handleChange}
                  required
                  step="0.01"
                  min="0"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label htmlFor="cash_paid" className="block text-sm font-medium text-gray-700 mb-1">
                  Cash Paid <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  id="cash_paid"
                  name="cash_paid"
                  value={formData.cash_paid}
                  onChange={handleChange}
                  required
                  step="0.01"
                  min="0"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label htmlFor="bank_deposit" className="block text-sm font-medium text-gray-700 mb-1">
                  Bank Deposit <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  id="bank_deposit"
                  name="bank_deposit"
                  value={formData.bank_deposit}
                  onChange={handleChange}
                  required
                  step="0.01"
                  min="0"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label htmlFor="bank_withdrawal" className="block text-sm font-medium text-gray-700 mb-1">
                  Bank Withdrawal
                </label>
                <input
                  type="number"
                  id="bank_withdrawal"
                  name="bank_withdrawal"
                  value={formData.bank_withdrawal}
                  onChange={handleChange}
                  step="0.01"
                  min="0"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="text-sm text-blue-600 mb-1">Calculated Closing Balance</div>
                <div className="text-2xl font-bold text-blue-900">
                  ₹{closingBalance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </div>
              </div>
            </div>
          </div>

          {/* Denomination Breakup (Optional) */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Denomination Breakup</h2>
              <button
                type="button"
                onClick={() => setShowDenomination(!showDenomination)}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                {showDenomination ? 'Hide' : 'Show'} Denomination
              </button>
            </div>

            {showDenomination && (
              <>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">₹2000 Notes</label>
                    <input
                      type="number"
                      name="notes_2000"
                      value={denomination.notes_2000}
                      onChange={handleDenominationChange}
                      min="0"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">₹500 Notes</label>
                    <input
                      type="number"
                      name="notes_500"
                      value={denomination.notes_500}
                      onChange={handleDenominationChange}
                      min="0"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">₹200 Notes</label>
                    <input
                      type="number"
                      name="notes_200"
                      value={denomination.notes_200}
                      onChange={handleDenominationChange}
                      min="0"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">₹100 Notes</label>
                    <input
                      type="number"
                      name="notes_100"
                      value={denomination.notes_100}
                      onChange={handleDenominationChange}
                      min="0"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">₹50 Notes</label>
                    <input
                      type="number"
                      name="notes_50"
                      value={denomination.notes_50}
                      onChange={handleDenominationChange}
                      min="0"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">₹20 Notes</label>
                    <input
                      type="number"
                      name="notes_20"
                      value={denomination.notes_20}
                      onChange={handleDenominationChange}
                      min="0"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">₹10 Notes</label>
                    <input
                      type="number"
                      name="notes_10"
                      value={denomination.notes_10}
                      onChange={handleDenominationChange}
                      min="0"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">₹10 Coins</label>
                    <input
                      type="number"
                      name="coins_10"
                      value={denomination.coins_10}
                      onChange={handleDenominationChange}
                      min="0"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="text-sm text-gray-600">Denomination Total</div>
                      <div className="text-xl font-bold text-gray-900">
                        ₹{denominationTotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </div>
                    </div>
                    {hasDiscrepancy && (
                      <div className="text-right">
                        <div className="text-sm text-red-600">Discrepancy</div>
                        <div className="text-xl font-bold text-red-600">
                          ₹{Math.abs(closingBalance - denominationTotal).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </>
            )}
          </div>

          {/* Notes */}
          <div>
            <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-1">
              Notes
            </label>
            <textarea
              id="notes"
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Any additional notes or observations..."
            />
          </div>
        </div>

        {/* Form Actions */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end space-x-3 rounded-b-lg">
          <button
            type="button"
            onClick={handleCancel}
            disabled={loading}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Recording...' : 'Record Position'}
          </button>
        </div>
      </form>
    </div>
  );
}
