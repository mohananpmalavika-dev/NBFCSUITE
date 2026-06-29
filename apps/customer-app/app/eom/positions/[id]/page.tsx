"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { AppShell } from '../../../../components/AppShell';
import { eomApiUrl } from '../../../eomApi';

export default function PositionDetailPage() {
  const params = useParams<{ id: string }>();
  const [position, setPosition] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!params?.id) return;
    let mounted = true;
    (async () => {
      try {
        const res = await fetch(eomApiUrl(`/eom/positions/${params.id}`));
        if (!res.ok) return;
        const body = await res.json();
        if (mounted) setPosition(body);
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, [params?.id]);

  if (loading) return <AppShell><div className="p-6">Loading…</div></AppShell>;
  if (!position) return <AppShell><div className="p-6">Position not found.</div></AppShell>;

  return (
    <AppShell>
      <div className="space-y-6 p-6">
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-sm font-medium text-primary-600">Position Profile</p>
            <h2 className="text-2xl font-semibold">{position.title}</h2>
            <p className="text-sm text-text-secondary">{position.code} · {position.status}</p>
          </div>
          <Link href="/eom/positions" className="btn">Back to positions</Link>
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          <section className="rounded-md border p-4 space-y-3">
            <h3 className="font-semibold">Role details</h3>
            <div className="grid gap-2 text-sm">
              <div><span className="font-medium">Grade:</span> {position.grade_id || '—'}</div>
              <div><span className="font-medium">Team:</span> {position.team_id || '—'}</div>
              <div><span className="font-medium">Reports to:</span> {position.reports_to_position_id || '—'}</div>
              <div><span className="font-medium">Created:</span> {position.created_at || '—'}</div>
              <div><span className="font-medium">Updated:</span> {position.updated_at || '—'}</div>
            </div>
          </section>
          <section className="rounded-md border p-4 space-y-3">
            <h3 className="font-semibold">Description</h3>
            <p className="text-sm text-text-secondary">{position.description || 'No description provided.'}</p>
          </section>
        </div>
      </div>
    </AppShell>
  );
}
