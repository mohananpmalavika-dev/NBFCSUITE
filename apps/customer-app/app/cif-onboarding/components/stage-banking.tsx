'use client';

import { useCIFStore } from '@/lib/cif-store';
import { cifApi } from '@/lib/cif-api';
import { useState } from 'react';

interface StageBankingProps {
  onNext: () => void;
}

export default function StageBanking({ onNext }: StageBankingProps) {
  const { customerId, banking, updateBanking, setLoading, setError, markStageComplete } =
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
      await cifApi.addBankingProfile(customerId, {
        primary_bank_account: banking.accountNumber || '',
        primary_bank_name: banking.primaryBank || '',
        primary_account_type: 'savings',
        average_balance: banking.averageBalance,
      });

      markStageComplete(11);
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
        <h2 className="text-2xl font-bold text-slate-900">Banking Profile Saved!</h2>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Stage 11: Banking Profile</h2>
        <p className="text-slate-600">Link existing bank accounts for transaction monitoring.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Primary Bank
          </label>
          <input
            type="text"
            value={banking.primaryBank || ''}
            onChange={(e) => updateBanking({ primaryBank: e.target.value })}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
            placeholder="HDFC Bank, ICICI Bank, etc."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Account Number
          </label>
          <input
            type="text"
            value={banking.accountNumber || ''}
            onChange={(e) => updateBanking({ accountNumber: e.target.value })}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
            placeholder="1234567890"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Average Monthly Balance (₹)
          </label>
          <input
            type="number"
            value={banking.averageBalance || ''}
            onChange={(e) => updateBanking({ averageBalance: parseFloat(e.target.value) })}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg"
            placeholder="100000"
          />
        </div>

        <button
          type="submit"
          className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
        >
          🏦 Save Banking Profile
        </button>
      </form>
    </div>
  );
}
