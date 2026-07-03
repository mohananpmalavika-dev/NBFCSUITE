/**
 * Interest Calculator
 * Calculate FD/RD returns with detailed breakdown
 */

'use client';

import { useState } from 'react';
import { Calculator, TrendingUp, Clock, PiggyBank, Calendar } from 'lucide-react';

export default function CalculatorPage() {
  const [calculatorType, setCalculatorType] = useState<'FD' | 'RD'>('FD');
  const [fdData, setFdData] = useState({
    principal: 100000,
    rate: 7.0,
    tenure: 365,
    method: 'SIMPLE',
    compoundingFrequency: 4
  });
  const [rdData, setRdData] = useState({
    installment: 5000,
    months: 12,
    rate: 7.0
  });
  const [fdResult, setFdResult] = useState<any>(null);
  const [rdResult, setRdResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const calculateFD = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8007/api/v1/interest/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          principal: fdData.principal,
          rate: fdData.rate,
          days: fdData.tenure,
          method: fdData.method,
          compounding_frequency: fdData.compoundingFrequency
        })
      });
      const data = await response.json();
      setFdResult(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateRD = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8007/api/v1/rd/calculate-maturity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          installment_amount: rdData.installment,
          num_months: rdData.months,
          interest_rate: rdData.rate
        })
      });
      const data = await response.json();
      setRdResult(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-green-50/30 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="text-center">
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="p-4 bg-gradient-to-r from-green-500 to-emerald-500 rounded-2xl">
              <Calculator className="w-8 h-8 text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-slate-900 mb-2">Deposit Calculator</h1>
          <p className="text-slate-600">Calculate your deposit returns and plan your investments</p>
        </div>

        {/* Calculator Type Toggle */}
        <div className="flex justify-center">
          <div className="inline-flex bg-white rounded-xl shadow-lg border border-slate-200 p-2">
            <button
              onClick={() => setCalculatorType('FD')}
              className={`px-8 py-3 rounded-lg font-medium transition-colors flex items-center gap-2 ${
                calculatorType === 'FD'
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-700 hover:bg-slate-50'
              }`}
            >
              <PiggyBank className="w-5 h-5" />
              Fixed Deposit
            </button>
            <button
              onClick={() => setCalculatorType('RD')}
              className={`px-8 py-3 rounded-lg font-medium transition-colors flex items-center gap-2 ${
                calculatorType === 'RD'
                  ? 'bg-orange-600 text-white'
                  : 'text-slate-700 hover:bg-slate-50'
              }`}
            >
              <Clock className="w-5 h-5" />
              Recurring Deposit
            </button>
          </div>
        </div>

        {/* Calculator Forms */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Input Form */}
          <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-6">
              {calculatorType === 'FD' ? 'FD Calculator' : 'RD Calculator'}
            </h2>
            
            {calculatorType === 'FD' ? (
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Principal Amount (₹)
                  </label>
                  <input
                    type="number"
                    value={fdData.principal}
                    onChange={(e) => setFdData({ ...fdData, principal: Number(e.target.value) })}
                    className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Interest Rate (% p.a.)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={fdData.rate}
                    onChange={(e) => setFdData({ ...fdData, rate: Number(e.target.value) })}
                    className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Tenure (Days)
                  </label>
                  <input
                    type="number"
                    value={fdData.tenure}
                    onChange={(e) => setFdData({ ...fdData, tenure: Number(e.target.value) })}
                    className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                  <p className="text-sm text-slate-600 mt-1">
                    = {Math.round(fdData.tenure / 365)} year{fdData.tenure >= 730 ? 's' : ''}
                  </p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Interest Method
                  </label>
                  <select
                    value={fdData.method}
                    onChange={(e) => setFdData({ ...fdData, method: e.target.value })}
                    className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="SIMPLE">Simple Interest</option>
                    <option value="COMPOUND_MONTHLY">Compound - Monthly</option>
                    <option value="COMPOUND_QUARTERLY">Compound - Quarterly</option>
                    <option value="COMPOUND_HALF_YEARLY">Compound - Half Yearly</option>
                    <option value="COMPOUND_YEARLY">Compound - Yearly</option>
                  </select>
                </div>
                
                <button
                  onClick={calculateFD}
                  disabled={loading}
                  className="w-full px-6 py-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  <Calculator className="w-5 h-5" />
                  {loading ? 'Calculating...' : 'Calculate Returns'}
                </button>
              </div>
            ) : (
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Monthly Installment (₹)
                  </label>
                  <input
                    type="number"
                    value={rdData.installment}
                    onChange={(e) => setRdData({ ...rdData, installment: Number(e.target.value) })}
                    className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Number of Months
                  </label>
                  <select
                    value={rdData.months}
                    onChange={(e) => setRdData({ ...rdData, months: Number(e.target.value) })}
                    className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                  >
                    <option value={6}>6 Months</option>
                    <option value={12}>12 Months (1 Year)</option>
                    <option value={24}>24 Months (2 Years)</option>
                    <option value={36}>36 Months (3 Years)</option>
                    <option value={60}>60 Months (5 Years)</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Interest Rate (% p.a.)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={rdData.rate}
                    onChange={(e) => setRdData({ ...rdData, rate: Number(e.target.value) })}
                    className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                  />
                </div>
                
                <button
                  onClick={calculateRD}
                  disabled={loading}
                  className="w-full px-6 py-4 bg-orange-600 text-white rounded-lg font-medium hover:bg-orange-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  <Calculator className="w-5 h-5" />
                  {loading ? 'Calculating...' : 'Calculate Returns'}
                </button>
              </div>
            )}
          </div>

          {/* Results */}
          <div className="space-y-6">
            {calculatorType === 'FD' && fdResult && (
              <div className="bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl shadow-lg p-8 text-white">
                <h3 className="text-2xl font-bold mb-6">Your FD Returns</h3>
                
                <div className="space-y-4">
                  <ResultItem
                    label="Principal Amount"
                    value={`₹${fdResult.principal?.toLocaleString('en-IN')}`}
                  />
                  <ResultItem
                    label="Interest Rate"
                    value={`${fdResult.rate}% p.a.`}
                  />
                  <ResultItem
                    label="Tenure"
                    value={`${fdResult.days} days (${fdResult.years?.toFixed(2)} years)`}
                  />
                  <ResultItem
                    label="Method"
                    value={fdResult.method}
                  />
                  
                  <div className="pt-4 border-t border-white/20">
                    <ResultItem
                      label="Interest Earned"
                      value={`₹${fdResult.interest?.toLocaleString('en-IN')}`}
                      highlight
                    />
                  </div>
                  
                  <div className="pt-2">
                    <p className="text-white/80 text-sm mb-2">Maturity Amount</p>
                    <p className="text-5xl font-bold">
                      ₹{fdResult.maturity_amount?.toLocaleString('en-IN')}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {calculatorType === 'RD' && rdResult && (
              <div className="bg-gradient-to-br from-orange-500 to-red-500 rounded-xl shadow-lg p-8 text-white">
                <h3 className="text-2xl font-bold mb-6">Your RD Returns</h3>
                
                <div className="space-y-4">
                  <ResultItem
                    label="Monthly Installment"
                    value={`₹${rdResult.monthly_installment?.toLocaleString('en-IN')}`}
                  />
                  <ResultItem
                    label="Number of Months"
                    value={rdResult.num_months}
                  />
                  <ResultItem
                    label="Interest Rate"
                    value={`${rdResult.annual_rate}% p.a.`}
                  />
                  <ResultItem
                    label="Total Principal"
                    value={`₹${rdResult.total_principal?.toLocaleString('en-IN')}`}
                  />
                  
                  <div className="pt-4 border-t border-white/20">
                    <ResultItem
                      label="Interest Earned"
                      value={`₹${rdResult.total_interest?.toLocaleString('en-IN')}`}
                      highlight
                    />
                  </div>
                  
                  <div className="pt-2">
                    <p className="text-white/80 text-sm mb-2">Maturity Amount</p>
                    <p className="text-5xl font-bold">
                      ₹{rdResult.maturity_amount?.toLocaleString('en-IN')}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {!fdResult && !rdResult && (
              <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-12 text-center">
                <Calculator className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                <p className="text-slate-600">
                  Enter details and click calculate to see your returns
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Quick Scenarios */}
        <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-8">
          <h3 className="text-xl font-bold text-slate-900 mb-6">Popular Investment Scenarios</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <ScenarioCard
              title="₹1 Lakh for 1 Year"
              description="Short-term FD"
              principal={100000}
              rate={7.0}
              tenure="365 days"
              returns="₹7,000"
            />
            <ScenarioCard
              title="₹5 Lakh for 3 Years"
              description="Medium-term FD"
              principal={500000}
              rate={7.5}
              tenure="1095 days"
              returns="₹1,12,500"
            />
            <ScenarioCard
              title="₹5K/month for 5 Years"
              description="Long-term RD"
              principal={300000}
              rate={7.0}
              tenure="60 months"
              returns="₹65,250"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function ResultItem({ label, value, highlight = false }: any) {
  return (
    <div className="flex justify-between items-center">
      <span className={highlight ? 'text-white font-medium' : 'text-white/80'}>{label}</span>
      <span className={highlight ? 'text-2xl font-bold' : 'font-semibold'}>{value}</span>
    </div>
  );
}

function ScenarioCard({ title, description, principal, rate, tenure, returns }: any) {
  return (
    <div className="p-6 bg-slate-50 rounded-xl border border-slate-200 hover:shadow-md transition-shadow">
      <h4 className="font-bold text-slate-900 mb-1">{title}</h4>
      <p className="text-sm text-slate-600 mb-4">{description}</p>
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-slate-600">Principal</span>
          <span className="font-semibold">₹{principal.toLocaleString('en-IN')}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-600">Rate</span>
          <span className="font-semibold">{rate}%</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-600">Tenure</span>
          <span className="font-semibold">{tenure}</span>
        </div>
        <div className="pt-2 border-t border-slate-200">
          <div className="flex justify-between">
            <span className="text-slate-600">Interest</span>
            <span className="font-bold text-green-600">{returns}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
