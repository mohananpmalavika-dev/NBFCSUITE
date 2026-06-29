"use client";

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { AppShell } from '../../../../components/AppShell';
import { eomApiUrl } from '../../../eomApi';

export default function DepartmentDashboardPage() {
  const params = useParams<{ id: string }>();
  const [data, setData] = useState<any>(null);
  useEffect(() => {
    if (!params?.id) return;
    fetch(eomApiUrl(`/eom/departments/${params.id}/dashboard`))
      .then((res) => res.json())
      .then(setData);
  }, [params?.id]);

  return (
    <AppShell>
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Department dashboard</h2>
        {data ? (
          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-md border p-4"><div className="text-sm text-text-secondary">Health score</div><div className="text-3xl font-semibold">{data.health_score}%</div></div>
            <div className="rounded-md border p-4"><div className="text-sm text-text-secondary">Active personnel</div><div className="text-3xl font-semibold">{data.active_personnel}</div></div>
            <div className="rounded-md border p-4"><div className="text-sm text-text-secondary">Teams</div><div className="text-3xl font-semibold">{data.teams}</div></div>
            <div className="rounded-md border p-4"><div className="text-sm text-text-secondary">Open requests</div><div className="text-3xl font-semibold">{data.open_requests}</div></div>
            <div className="rounded-md border p-4"><div className="text-sm text-text-secondary">Budget utilization</div><div className="text-3xl font-semibold">{data.budget_utilization}%</div></div>
            <div className="rounded-md border p-4"><div className="text-sm text-text-secondary">Productivity index</div><div className="text-3xl font-semibold">{data.productivity_index}%</div></div>
          </div>
        ) : <div>Loading…</div>}
      </div>
    </AppShell>
  );
}
