'use client';

import { useCIFStore } from '@/lib/cif-store';
import { cifApi } from '@/lib/cif-api';
import { useState } from 'react';

interface StageBehaviorProps {
  onNext: () => void;
}

export default function StageBehavior({ onNext }: StageBehaviorProps) {
  const { customerId, financial, behavior, updateBehavior, setLoading, setError, markStageComplete } =
    useCIFStore();
  const [submitted, setSubmitted] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);

  const handleAnalyze = async () => {
    if (!customerId) {
      setError('No customer selected');
      return;
    }

    setAnalyzing(true);
    setLoading(true);
    try {
      const response = await cifApi.analyzeBehavior(customerId, {
        monthly_income: financial.monthlyIncome,
        monthly_expense: financial.monthlyExpense,
        total_assets: financial.assets,
        total_liabilities: financial.liabilities,
      });

      updateBehavior({
        riskAppetite: response.risk_appetite,
        spendingPattern: response.spending_pattern,
        finDna: response.fin_dna,
        productAffinity: response.product_affinity,
      });

      markStageComplete(13);
      setSubmitted(true);
      setTimeout(onNext, 1500);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setAnalyzing(false);
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="text-center py-12 space-y-6">
        <div className="text-5xl mb-4">🧠</div>
        <h2 className="text-2xl font-bold text-slate-900">FinDNA Generated!</h2>
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6">
          <p className="text-sm text-slate-600 mb-2">Behavioral Profile</p>
          <p className="text-2xl font-bold text-slate-900">{behavior.finDna}</p>
          <p className="text-sm text-slate-600 mt-2">
            This unique behavioral signature will help us recommend the right products for you.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Stage 13: Behavioral Analysis</h2>
        <p className="text-slate-600">
          Generate FinDNA - Your behavioral financial signature. This helps us understand your
          financial personality and recommend suitable products.
        </p>
      </div>

      <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-6 space-y-4">
        <h3 className="font-bold text-slate-900">🧠 What is FinDNA?</h3>
        <p className="text-sm text-slate-700">
          FinDNA is a unique behavioral profile that combines financial metrics with spending
          patterns to create a complete picture of your financial personality. It helps us:
        </p>
        <ul className="text-sm text-slate-700 space-y-2">
          <li>✓ Predict your financial behavior</li>
          <li>✓ Recommend the right products</li>
          <li>✓ Detect early churn risk</li>
          <li>✓ Price products competitively</li>
        </ul>
      </div>

      {!submitted && !analyzing && (
        <button
          onClick={handleAnalyze}
          className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:opacity-90 font-semibold transition-all"
        >
          🧠 Analyze & Generate FinDNA
        </button>
      )}

      {analyzing && (
        <div className="text-center py-8">
          <div className="inline-block animate-spin h-8 w-8 border-4 border-purple-500 border-t-transparent rounded-full mb-4"></div>
          <p className="text-slate-600">Analyzing behavioral patterns...</p>
        </div>
      )}

      {behavior.productAffinity && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-3">
          <h3 className="font-bold text-blue-900">📊 Product Recommendations</h3>
          <div className="space-y-2">
            {Object.entries(behavior.productAffinity as Record<string, number>)
              .sort(([, a], [, b]) => b - a)
              .map(([product, score]) => (
                <div key={product} className="flex items-center justify-between">
                  <span className="text-sm text-blue-800">{product}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-2 bg-blue-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-blue-600 rounded-full"
                        style={{ width: `${score}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-semibold text-blue-900 w-10 text-right">
                      {Math.round(score)}%
                    </span>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}
