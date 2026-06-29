"use client";

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { AppShell } from '../../../../components/AppShell';
import { eomApiUrl } from '../../../eomApi';

export default function BranchHealthPage() {
  const params = useParams<{ id: string }>();
  const [data, setData] = useState<any>(null);
  useEffect(() => {
    if (!params?.id) return;
    fetch(eomApiUrl(`/eom/branches/${params.id}/health`))
      .then((res) => res.json())
      .then(setData);
  }, [params?.id]);

  return (
    <AppShell>
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Branch health</h2>
        {data ? (
          <div className="rounded-md border p-4 space-y-2">
            <div><span className="font-medium">Score:</span> {data.health_score}%</div>
            <div><span className="font-medium">Rating:</span> {data.rating}</div>
            <div><span className="font-medium">Issues:</span> {data.issues.length ? data.issues.join(', ') : 'None'}</div>
          </div>
        ) : <div>Loading…</div>}
      </div>
    </AppShell>
  );
}
