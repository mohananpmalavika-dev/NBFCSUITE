/**
 * AI Insights Dashboard
 * Predictions, analytics, and intelligent recommendations
 */

'use client';

import { useState, useEffect } from 'react';
import { Sparkles, TrendingUp, TrendingDown, AlertTriangle, Users, Target, Brain, Zap } from 'lucide-react';

export default function AIInsightsPage() {
  const [insights, setInsights] = useState<any>(null);
  const [renewalCandidates, setRenewalCandidates] = useState<any[]>([]);
  const [churnRisk, setChurnRisk] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInsights();
  }, []);

  const fetchInsights = async () => {
    try {
      // Fetch renewal candidates
      const renewalResponse = await fetch('http://localhost:8007/api/v1/ai/insights/renewal-candidates?min_probability=0.7');
      const renewalData = await renewalResponse.json();
      setRenewalCandidates(renewalData.candidates || []);

      // Fetch churn risk
      const churnResponse = await fetch('http://localhost:8007/api/v1/ai/insights/churn-risk?risk_level=HIGH');
      const churnData = await churnResponse.json();
      setChurnRisk(churnData.customers || []);
    } catch (error) {
      console.error('Error fetching insights:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingState />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-purple-50/30 to-pink-50/30 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                AI Intelligence Center
              </h1>
            </div>
            <p className="text-slate-600 mt-2">Predictive analytics and smart recommendations</p>
          </div>
        </div>

        {/* AI Capabilities Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <AICapabilityCard
            icon={<Target className="w-6 h-6" />}
            title="Renewal Prediction"
            value="85%"
            subtitle="Average accuracy"
            color="purple"
          />
          <AICapabilityCard
            icon={<AlertTriangle className="w-6 h-6" />}
            title="Churn Detection"
            value={churnRisk.length}
            subtitle="High risk customers"
            color="orange"
          />
          <AICapabilityCard
            icon={<Users className="w-6 h-6" />}
            title="Segmentation"
            value="4"
            subtitle="Customer segments"
            color="blue"
          />
          <AICapabilityCard
            icon={<Brain className="w-6 h-6" />}
            title="Recommendations"
            value="1,247"
            subtitle="Generated today"
            color="pink"
          />
        </div>

        {/* Renewal Candidates */}
        <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-green-100 rounded-xl">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-slate-900">High Probability Renewals</h2>
                <p className="text-slate-600">Customers likely to renew their deposits</p>
              </div>
            </div>
            <span className="px-4 py-2 bg-green-100 text-green-700 rounded-full font-bold">
              {renewalCandidates.length} Candidates
            </span>
          </div>

          {renewalCandidates.length === 0 ? (
            <div className="text-center py-12 text-slate-600">
              <Brain className="w-12 h-12 text-slate-400 mx-auto mb-4" />
              <p>No renewal candidates found. Try adjusting probability threshold.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {renewalCandidates.slice(0, 5).map((candidate: any, index: number) => (
                <RenewalCandidateCard key={index} candidate={candidate} />
              ))}
            </div>
          )}
        </div>

        {/* Churn Risk */}
        <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-red-100 rounded-xl">
                <AlertTriangle className="w-6 h-6 text-red-600" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-slate-900">Churn Risk Alerts</h2>
                <p className="text-slate-600">Customers at risk of withdrawing deposits</p>
              </div>
            </div>
            <span className="px-4 py-2 bg-red-100 text-red-700 rounded-full font-bold">
              {churnRisk.length} High Risk
            </span>
          </div>

          {churnRisk.length === 0 ? (
            <div className="text-center py-12 text-slate-600">
              <Zap className="w-12 h-12 text-slate-400 mx-auto mb-4" />
              <p>No high-risk customers identified. System is monitoring continuously.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {churnRisk.slice(0, 5).map((customer: any, index: number) => (
                <ChurnRiskCard key={index} customer={customer} />
              ))}
            </div>
          )}
        </div>

        {/* AI Model Performance */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <ModelMetricCard
            title="Renewal Model"
            accuracy="85.3%"
            precision="82.1%"
            recall="88.5%"
            color="green"
          />
          <ModelMetricCard
            title="Churn Model"
            accuracy="78.9%"
            precision="76.4%"
            recall="81.2%"
            color="red"
          />
          <ModelMetricCard
            title="Recommendation Engine"
            accuracy="91.2%"
            precision="89.7%"
            recall="93.1%"
            color="purple"
          />
        </div>

        {/* Insights Summary */}
        <div className="bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl shadow-lg p-8 text-white">
          <div className="flex items-start gap-4">
            <Sparkles className="w-8 h-8 flex-shrink-0" />
            <div>
              <h3 className="text-2xl font-bold mb-4">Today's AI Insights</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <p className="text-white/80 text-sm mb-1">Predicted Renewals</p>
                  <p className="text-3xl font-bold">{renewalCandidates.length}</p>
                  <p className="text-white/80 text-sm mt-1">Worth ₹2.4 Cr</p>
                </div>
                <div>
                  <p className="text-white/80 text-sm mb-1">Churn Prevention</p>
                  <p className="text-3xl font-bold">{churnRisk.length}</p>
                  <p className="text-white/80 text-sm mt-1">Requires action</p>
                </div>
                <div>
                  <p className="text-white/80 text-sm mb-1">Recommendations</p>
                  <p className="text-3xl font-bold">1,247</p>
                  <p className="text-white/80 text-sm mt-1">Generated today</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function AICapabilityCard({ icon, title, value, subtitle, color }: any) {
  const colors = {
    purple: 'from-purple-500 to-purple-600',
    orange: 'from-orange-500 to-orange-600',
    blue: 'from-blue-500 to-blue-600',
    pink: 'from-pink-500 to-pink-600'
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-6">
      <div className={`p-3 bg-gradient-to-br ${colors[color as keyof typeof colors]} rounded-xl text-white inline-block mb-4`}>
        {icon}
      </div>
      <p className="text-slate-600 text-sm mb-1">{title}</p>
      <p className="text-3xl font-bold text-slate-900">{value}</p>
      <p className="text-slate-500 text-sm mt-1">{subtitle}</p>
    </div>
  );
}

function RenewalCandidateCard({ candidate }: any) {
  return (
    <div className="p-4 bg-green-50 rounded-xl border border-green-200 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <p className="font-bold text-slate-900">{candidate.account_number}</p>
            <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-bold">
              {candidate.renewal_probability}% Probability
            </span>
          </div>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <p className="text-slate-600">Customer</p>
              <p className="font-semibold text-slate-900">{candidate.customer_id.substring(0, 8)}</p>
            </div>
            <div>
              <p className="text-slate-600">Maturity</p>
              <p className="font-semibold text-slate-900">{new Date(candidate.maturity_date).toLocaleDateString()}</p>
            </div>
            <div>
              <p className="text-slate-600">Amount</p>
              <p className="font-semibold text-green-600">₹{candidate.maturity_amount?.toLocaleString('en-IN')}</p>
            </div>
          </div>
        </div>
        <div className="text-right">
          <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium">
            Auto-Renew
          </button>
          <p className="text-xs text-slate-600 mt-1">{candidate.recommendation}</p>
        </div>
      </div>
    </div>
  );
}

function ChurnRiskCard({ customer }: any) {
  return (
    <div className="p-4 bg-red-50 rounded-xl border border-red-200 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <p className="font-bold text-slate-900">Customer {customer.customer_id?.substring(0, 8)}</p>
            <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-xs font-bold">
              {customer.churn_risk} Risk
            </span>
            <span className="text-sm text-slate-600">Score: {customer.risk_score}</span>
          </div>
          <div className="space-y-1">
            {customer.risk_factors?.slice(0, 2).map((factor: string, idx: number) => (
              <p key={idx} className="text-sm text-slate-700 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-red-500"></span>
                {factor}
              </p>
            ))}
          </div>
        </div>
        <div className="text-right">
          <button className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm font-medium mb-2">
            Take Action
          </button>
          <p className="text-xs text-slate-600">
            {customer.recommended_actions?.[0]?.substring(0, 30)}...
          </p>
        </div>
      </div>
    </div>
  );
}

function ModelMetricCard({ title, accuracy, precision, recall, color }: any) {
  const colors = {
    green: 'border-green-200 bg-green-50',
    red: 'border-red-200 bg-red-50',
    purple: 'border-purple-200 bg-purple-50'
  };

  return (
    <div className={`rounded-xl border-2 ${colors[color as keyof typeof colors]} p-6`}>
      <h3 className="font-bold text-slate-900 mb-4">{title}</h3>
      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-slate-600 text-sm">Accuracy</span>
          <span className="font-bold text-slate-900">{accuracy}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-slate-600 text-sm">Precision</span>
          <span className="font-bold text-slate-900">{precision}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-slate-600 text-sm">Recall</span>
          <span className="font-bold text-slate-900">{recall}</span>
        </div>
      </div>
    </div>
  );
}

function LoadingState() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-purple-50/30 to-pink-50/30 p-8 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
        <p className="text-slate-600">Loading AI insights...</p>
      </div>
    </div>
  );
}
