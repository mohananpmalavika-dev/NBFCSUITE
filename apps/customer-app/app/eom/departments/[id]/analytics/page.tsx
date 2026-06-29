"use client";

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { AppShell } from '../../../../components/AppShell';
import { eomApiUrl } from '../../../eomApi';

export default function DepartmentAnalyticsPage() {
  const params = useParams<{ id: string }>();
  const [data, setData] = useState<any>(null);
  useEffect(() => {
    if (!params?.id) return;
    fetch(eomApiUrl(`/eom/departments/${params.id}/analytics`))
      .then((res) => res.json())
      .then(setData);
  }, [params?.id]);

  return (
    <AppShell>
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Department analytics</h2>
        {data ? (
          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-md border p-4"><div className="text-sm text-text-secondary">Headcount growth</div><div className="text-3xl font-semibold">{data.headcount_growth}%</div></div>
            <div className="rounded-md border p-4"><div className="text-sm text-text-secondary">Cost variance</div><div className="text-3xl font-semibold">{data.cost_variance}%</div></div>
            <div className="rounded-md border p-4"><div className="text-sm text-text-secondary">Efficiency</div><div className="text-3xl font-semibold">{data.efficiency}%</div></div>
            <div className="rounded-md border p-4"><div className="text-sm text-text-secondary">Compliance score</div><div className="text-3xl font-semibold">{data.compliance_score}%</div></div>
          </div>
        ) : <div>Loading…</div>}
      </div>
    </AppShell>
  );
}
