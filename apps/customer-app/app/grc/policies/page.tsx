"use client";

import { useEffect, useState } from 'react';
import { AppShell } from '../../components/AppShell';
import { grcApi, DEFAULT_GRC_TENANT } from '../grcApi';
import type { PolicyResponse } from '../grcApi';

export default function GrcPoliciesPage() {
  const [policies, setPolicies] = useState<PolicyResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadPolicies() {
      setLoading(true);
      setError('');
      try {
        const result = await grcApi.listPolicies(DEFAULT_GRC_TENANT);
        setPolicies(result);
      } catch (err) {
        setError('Unable to load policies. Ensure the GRC service is running.');
      } finally {
        setLoading(false);
      }
    }

    loadPolicies();
  }, []);

  return (
    <AppShell>
      <div className="space-y-6 p-6">
        <div className="rounded-md border border-border-default bg-background-surface p-6">
          <div className="text-sm font-semibold uppercase tracking-wide text-accent-primary">GRC Policies</div>
          <h1 className="mt-2 text-2xl font-semibold text-text-primary">Policy management</h1>
          <p className="mt-2 max-w-3xl text-sm text-text-secondary">
            View enterprise policies and keep policy lifecycle, ownership, and review details in one place.
          </p>
        </div>

        {loading ? (
          <div className="rounded-md border border-border-default bg-background-default p-6 text-sm text-text-secondary">Loading policies…</div>
        ) : error ? (
          <div className="rounded-md border border-border-default bg-danger-surface p-4 text-sm text-danger-foreground">{error}</div>
        ) : (
          <div className="space-y-4">
            {policies.length ? (
              policies.map((policy) => (
                <div key={policy.id} className="rounded-md border border-border-default bg-background-surface p-4">
                  <div className="text-lg font-semibold text-text-primary">{policy.title}</div>
                  <div className="text-sm text-text-secondary">Policy number: {policy.policy_number}</div>
                  <div className="mt-2 text-sm text-text-secondary">Owner: {policy.owner ?? 'Unassigned'}</div>
                  <div className="mt-1 text-sm text-text-secondary">Status: {policy.status}</div>
                </div>
              ))
            ) : (
              <div className="rounded-md border border-border-default bg-background-default p-6 text-sm text-text-secondary">No policies found.</div>
            )}
          </div>
        )}
      </div>
    </AppShell>
  );
}
