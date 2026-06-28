"use client";

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { AppShell } from '../../../components/AppShell';
import { eomApiUrl } from '../../eomApi';

export default function GeographyDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [node, setNode] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const res = await fetch(eomApiUrl(`/eom/geography/${params.id}`));
        if (!res.ok) return;
        const body = await res.json();
        if (mounted) setNode(body);
      } catch (e) {
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, [params.id]);

  return (
    <AppShell>
      <div className="space-y-4 max-w-2xl">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold">Geography Node</h2>
            <p className="text-sm text-text-secondary">Detail and analytics for the selected geography node.</p>
          </div>
          <button className="btn" onClick={() => router.back()}>Back</button>
        </div>
        {loading ? (
          <div>Loading…</div>
        ) : node ? (
          <div className="rounded-md border p-4 space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <h3 className="text-sm font-semibold text-text-secondary">Name</h3>
                <p>{node.name}</p>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-text-secondary">Code</h3>
                <p>{node.code}</p>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-text-secondary">Type</h3>
                <p>{node.node_type}</p>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-text-secondary">Status</h3>
                <p>{node.status}</p>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-text-secondary">Manager</h3>
                <p>{node.manager || 'Unassigned'}</p>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-text-secondary">Parent ID</h3>
                <p>{node.parent_id || 'Root'}</p>
              </div>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-text-secondary">Coordinates</h3>
              <p>{node.latitude || 'N/A'} / {node.longitude || 'N/A'}</p>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-text-secondary">Description</h3>
              <p>{node.description || 'No description provided.'}</p>
            </div>
          </div>
        ) : (
          <div className="text-sm text-text-secondary">Geography node not found.</div>
        )}
      </div>
    </AppShell>
  );
}
