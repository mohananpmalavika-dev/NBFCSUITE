"use client";

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { AppShell } from '../../../components/AppShell';
import { eomApiUrl } from '../../eomApi';

export default function BusinessUnitDetailsPage() {
  const params: any = useParams();
  const id = params.id;
  const [item, setItem] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const res = await fetch(eomApiUrl(`/eom/business-units/${id}`));
        if (!res.ok) return;
        const body = await res.json();
        if (mounted) setItem(body);
      } catch (e) {
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, [id]);

  return (
    <AppShell>
      <div className="space-y-4">
        {loading ? (
          <div>Loading…</div>
        ) : item ? (
          <div className="space-y-2">
            <h2 className="text-xl font-semibold">{item.business_unit_name}</h2>
            <div className="text-sm text-text-secondary">{item.business_unit_code} • {item.status}</div>
            <div className="rounded-md border p-3 space-y-2">
              <div><strong>Legal Entity ID:</strong> {item.legal_entity_id}</div>
              <div><strong>Head:</strong> {item.head || 'Not assigned'}</div>
              <div><strong>Description:</strong> {item.description || 'No description'}</div>
              <div><strong>Created:</strong> {item.created_at}</div>
              <div><strong>Updated:</strong> {item.updated_at}</div>
            </div>
          </div>
        ) : (
          <div>Not found.</div>
        )}
      </div>
    </AppShell>
  );
}
