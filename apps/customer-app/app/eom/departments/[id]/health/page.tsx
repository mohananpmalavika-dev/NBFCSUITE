"use client";

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { AppShell } from '../../../../components/AppShell';
import { eomApiUrl } from '../../../eomApi';

export default function DepartmentHealthPage() {
  const params = useParams<{ id: string }>();
  const [data, setData] = useState<any>(null);
  useEffect(() => {
    if (!params?.id) return;
    fetch(eomApiUrl(`/eom/departments/${params.id}/health`))
      .then((res) => res.json())
      .then(setData);
  }, [params?.id]);

  return (
    <AppShell>
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Department health</h2>
        {data ? (
          <div className="rounded-md border p-4 space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div><div className="text-sm text-text-secondary">Health score</div><div className="text-3xl font-semibold">{data.health_score}%</div></div>
              <div><div className="text-sm text-text-secondary">Rating</div><div className="text-3xl font-semibold">{data.rating}</div></div>
            </div>
            <div>
              <div className="text-sm text-text-secondary">Issues</div>
              {data.issues.length > 0 ? (
                <ul className="mt-2 list-disc pl-5 text-sm text-text-secondary">
                  {data.issues.map((issue: string, index: number) => <li key={index}>{issue}</li>)}
                </ul>
              ) : (
                <p className="text-sm text-text-secondary">No issues detected.</p>
              )}
            </div>
          </div>
        ) : <div>Loading…</div>}
      </div>
    </AppShell>
  );
}
