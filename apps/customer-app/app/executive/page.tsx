'use client';

import { apiClient } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

interface ExecutiveDashboard {
  generated_at: string;
  portfolio_health: Record<string, number>;
  risk_summary: Record<string, number>;
  collections_summary: Record<string, number>;
  assistant_summary: Record<string, number>;
  recommendations: string[];
}

const riskOrder = ['critical', 'high', 'medium', 'low', 'unknown'];

export default function ExecutiveDashboardPage() {
  const { token, isLoading } = useAuth();
  const router = useRouter();
  const [dashboard, setDashboard] = useState<ExecutiveDashboard | null>(null);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!isLoading && !token) {
      router.push('/login');
    }
  }, [token, isLoading, router]);

  useEffect(() => {
    if (!token) {
      return;
    }

    const loadDashboard = async () => {
      setMessage('');
      try {
        const response = await apiClient.getExecutiveDashboard();
        setDashboard(response.data);
      } catch {
        setMessage('Could not load the FinDNA executive dashboard.');
      }
    };

    loadDashboard();
  }, [token]);

  if (isLoading) {
    return <div className="p-8 text-center">Loading...</div>;
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-950">Executive Dashboard</h1>
            <p className="mt-1 text-slate-600">Portfolio health, risk posture, and FinDNA assistant activity.</p>
          </div>
          <button
            onClick={() => router.push('/')}
            className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-white"
          >
            Dashboard
          </button>
        </div>

        {message && (
          <div className="mb-4 rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            {message}
          </div>
        )}

        {!dashboard ? (
          <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-sm text-slate-600">No executive data loaded.</p>
          </section>
        ) : (
          <div className="space-y-6">
            <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-5">
              <MetricCard label="Scored customers" value={dashboard.portfolio_health.scored_customers || 0} />
              <MetricCard label="Avg behavior score" value={dashboard.portfolio_health.average_behavior_score || 0} />
              <MetricCard label="Fraud records" value={dashboard.portfolio_health.fraud_records || 0} />
              <MetricCard label="Avg fraud score" value={dashboard.portfolio_health.average_fraud_score || 0} />
              <MetricCard label="Churn predictions" value={dashboard.portfolio_health.churn_predictions || 0} />
            </section>

            <section className="grid grid-cols-1 gap-6 lg:grid-cols-[1.2fr_0.8fr]">
              <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
                <div className="mb-5 flex items-center justify-between gap-3">
                  <h2 className="text-xl font-semibold text-slate-950">Risk Summary</h2>
                  <p className="text-xs text-slate-500">
                    Generated {new Date(dashboard.generated_at).toLocaleString()}
                  </p>
                </div>
                <div className="space-y-4">
                  {riskOrder.map((risk) => (
                    <RiskBar key={risk} label={risk} value={dashboard.risk_summary[risk] || 0} />
                  ))}
                </div>
              </div>

              <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
                <h2 className="mb-5 text-xl font-semibold text-slate-950">Collections Signals</h2>
                <div className="space-y-4">
                  {Object.entries(dashboard.collections_summary).map(([label, value]) => (
                    <MetricRow key={label} label={label} value={value} />
                  ))}
                </div>
              </div>
            </section>

            <section className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
                <h2 className="mb-5 text-xl font-semibold text-slate-950">Assistant Runs</h2>
                {Object.keys(dashboard.assistant_summary).length === 0 ? (
                  <p className="rounded-md bg-slate-50 p-4 text-sm text-slate-600">No assistant invocations yet.</p>
                ) : (
                  <div className="space-y-4">
                    {Object.entries(dashboard.assistant_summary).map(([label, value]) => (
                      <MetricRow key={label} label={label} value={value} />
                    ))}
                  </div>
                )}
              </div>

              <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
                <h2 className="mb-5 text-xl font-semibold text-slate-950">Recommendations</h2>
                <div className="space-y-3">
                  {dashboard.recommendations.map((recommendation) => (
                    <p key={recommendation} className="rounded-md border border-blue-100 bg-blue-50 p-3 text-sm text-blue-950">
                      {recommendation}
                    </p>
                  ))}
                </div>
              </div>
            </section>
          </div>
        )}
      </div>
    </main>
  );
}

function MetricCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-bold text-slate-950">{Number(value).toLocaleString()}</p>
    </div>
  );
}

function MetricRow({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex items-center justify-between rounded-md bg-slate-50 px-3 py-2">
      <p className="text-sm capitalize text-slate-600">{label.replace(/_/g, ' ')}</p>
      <p className="font-semibold text-slate-950">{Number(value).toLocaleString()}</p>
    </div>
  );
}

function RiskBar({ label, value }: { label: string; value: number }) {
  const width = Math.min(100, Math.max(6, value * 12));
  const tone =
    label === 'critical' || label === 'high'
      ? 'bg-red-500'
      : label === 'medium'
        ? 'bg-amber-500'
        : label === 'low'
          ? 'bg-emerald-500'
          : 'bg-slate-400';

  return (
    <div>
      <div className="mb-1 flex items-center justify-between">
        <p className="text-sm capitalize text-slate-600">{label}</p>
        <p className="text-sm font-semibold text-slate-950">{value}</p>
      </div>
      <div className="h-2 rounded-full bg-slate-100">
        <div className={`h-2 rounded-full ${tone}`} style={{ width: `${width}%` }} />
      </div>
    </div>
  );
}
