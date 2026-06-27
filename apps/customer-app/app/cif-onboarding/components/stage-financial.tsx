'use client';

import { useCIFStore } from '@/lib/cif-store';
import { cifApi } from '@/lib/cif-api';
import { useState } from 'react';

interface StageFinancialProps {
  onNext: () => void;
}

export default function StageFinancial({ onNext }: StageFinancialProps) {
  const { customerId, financial, updateFinancial, setLoading, setError, markStageComplete } =
    useCIFStore();
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!customerId) {
      setError('No customer selected');
      return;
    }

    setLoading(true);
    try {
      await cifApi.addFinancialProfile(customerId, {
        monthly_income: financial.monthlyIncome,
        monthly_expense: financial.monthlyExpense,
        total_assets: financial.assets,
        total_liabilities: financial.liabilities,
      });

      markStageComplete(10);
      setSubmitted(true);
      setTimeout(onNext, 1000);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="text-center py-12">
        <div className="text-5xl mb-4">✅</div>
        <h2 className="text-2xl font-bold text-slate-900">Financial Profile Saved!</h2>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Stage 10: Financial Profile</h2>
        <p className="text-slate-600">Provide financial information for risk assessment.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Monthly Income (₹)
            </label>
            <input
              type="number"
              value={financial.monthlyIncome || ''}
              onChange={(e) => updateFinancial({ monthlyIncome: parseFloat(e.target.value) })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg"
              placeholder="50000"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Monthly Expenses (₹)
            </label>
            <input
              type="number"
              value={financial.monthlyExpense || ''}
              onChange={(e) => updateFinancial({ monthlyExpense: parseFloat(e.target.value) })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg"
              placeholder="30000"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Total Assets (₹)
            </label>
            <input
              type="number"
              value={financial.assets || ''}
              onChange={(e) => updateFinancial({ assets: parseFloat(e.target.value) })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg"
              placeholder="500000"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Total Liabilities (₹)
            </label>
            <input
              type="number"
              value={financial.liabilities || ''}
              onChange={(e) => updateFinancial({ liabilities: parseFloat(e.target.value) })}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg"
              placeholder="100000"
            />
          </div>
        </div>

        <button
          type="submit"
          className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
        >
          💰 Save Financial Profile
        </button>
      </form>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-semibold text-blue-900 mb-2">💡 Net Worth Calculation</h4>
        <div className="text-sm text-blue-800">
          <p>
            Net Worth = Total Assets - Total Liabilities = ₹
            {((financial.assets || 0) - (financial.liabilities || 0)).toLocaleString('en-IN')}
          </p>
          <p className="mt-2">Monthly Savings = Monthly Income - Monthly Expenses = ₹
            {((financial.monthlyIncome || 0) - (financial.monthlyExpense || 0)).toLocaleString('en-IN')}
          </p>
        </div>
      </div>
    </div>
  );
}
