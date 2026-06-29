"use client";

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { AppShell } from '../../../../components/AppShell';
import { eomApiUrl } from '../../../eomApi';

export default function BranchAnalyticsPage() {
  const params = useParams<{ id: string }>();
  const [data, setData] = useState<any>(null);
  useEffect(() => {
    if (!params?.id) return;
    fetch(eomApiUrl(`/eom/branches/${params.id}/analytics`))
      .then((res) => res.json())
      .then(setData);
  }, [params?.id]);

  return (
    <AppShell>
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Branch analytics</h2>
        {data ? (
          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-md border p-4"><div className="text-sm text-text-secondary">Customer growth</div><div className="text-3xl font-semibold">{data.customer_growth}%</div></div>
            <div className="rounded-md border p-4"><div className="text-sm text-text-secondary">Loan growth</div><div className="text-3xl font-semibold">{data.loan_growth}%</div></div>
            <div className="rounded-md border p-4"><div className="text-sm text-text-secondary">Deposit growth</div><div className="text-3xl font-semibold">{data.deposit_growth}%</div></div>
            <div className="rounded-md border p-4"><div className="text-sm text-text-secondary">Audit score</div><div className="text-3xl font-semibold">{data.audit_score}</div></div>
          </div>
        ) : <div>Loading…</div>}
      </div>
    </AppShell>
  );
}
