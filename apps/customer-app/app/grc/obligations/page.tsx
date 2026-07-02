"use client";

import { useEffect, useState } from 'react';
import { AppShell } from '../../components/AppShell';
import { grcApi, DEFAULT_GRC_TENANT } from '../grcApi';

export default function GrcObligationsPage() {
  const [obligations, setObligations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadObligations() {
      setLoading(true);
      setError('');
      try {
        const result = await grcApi.listObligations(DEFAULT_GRC_TENANT);
        setObligations(result);
      } catch (err) {
        setError('Unable to load obligations. Ensure the GRC service is running.');
      } finally {
        setLoading(false);
      }
    }

    loadObligations();
  }, []);

  return (
    <AppShell>
      <div className="space-y-6 p-6">
        <div className="rounded-md border border-border-default bg-background-surface p-6">
          <div className="text-sm font-semibold uppercase tracking-wide text-accent-primary">GRC Obligations</div>
          <h1 className="mt-2 text-2xl font-semibold text-text-primary">Compliance obligations</h1>
          <p className="mt-2 max-w-3xl text-sm text-text-secondary">
            Track regulatory obligations with due dates, clause mapping, owners, and status.
          </p>
        </div>

        {loading ? (
          <div className="rounded-md border border-border-default bg-background-default p-6 text-sm text-text-secondary">Loading obligations…</div>
        ) : error ? (
          <div className="rounded-md border border-border-default bg-danger-surface p-4 text-sm text-danger-foreground">{error}</div>
        ) : (
          <div className="space-y-4">
            {obligations.length ? (
              obligations.map((item) => (
                <div key={item.id} className="rounded-md border border-border-default bg-background-surface p-4">
                  <div className="text-lg font-semibold text-text-primary">{item.clause ?? 'No clause assigned'}</div>
                  <div className="text-sm text-text-secondary">Owner: {item.owner ?? 'Unassigned'}</div>
                  <div className="mt-1 text-sm text-text-secondary">Due date: {item.due_date ?? 'TBD'}</div>
                  <div className="mt-1 text-sm text-text-secondary">Status: {item.status}</div>
                </div>
              ))
            ) : (
              <div className="rounded-md border border-border-default bg-background-default p-6 text-sm text-text-secondary">No obligations found.</div>
            )}
          </div>
        )}
      </div>
    </AppShell>
  );
}
