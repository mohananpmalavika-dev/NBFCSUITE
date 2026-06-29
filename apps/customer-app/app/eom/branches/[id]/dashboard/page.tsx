"use client";

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { AppShell } from '../../../../components/AppShell';
import { eomApiUrl } from '../../../eomApi';

export default function BranchDashboardPage() {
  const params = useParams<{ id: string }>();
  const [data, setData] = useState<any>(null);
  useEffect(() => {
    if (!params?.id) return;
    fetch(eomApiUrl(`/eom/branches/${params.id}/dashboard`))
      .then((res) => res.json())
      .then(setData);
  }, [params?.id]);

  return (
    <AppShell>
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Branch dashboard</h2>
        {data ? (
          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-md border p-4"><div className="text-sm text-text-secondary">Health score</div><div className="text-3xl font-semibold">{data.health_score}%</div></div>
            <div className="rounded-md border p-4"><div className="text-sm text-text-secondary">Active customers</div><div className="text-3xl font-semibold">{data.active_customers}</div></div>
            <div className="rounded-md border p-4"><div className="text-sm text-text-secondary">Loans</div><div className="text-3xl font-semibold">{data.loans}</div></div>
            <div className="rounded-md border p-4"><div className="text-sm text-text-secondary">Deposits</div><div className="text-3xl font-semibold">{data.deposits}</div></div>
            <div className="rounded-md border p-4"><div className="text-sm text-text-secondary">Cash balance</div><div className="text-3xl font-semibold">{data.cash_balance}</div></div>
            <div className="rounded-md border p-4"><div className="text-sm text-text-secondary">Profit</div><div className="text-3xl font-semibold">{data.profit}</div></div>
          </div>
        ) : <div>Loading…</div>}
      </div>
    </AppShell>
  );
}
