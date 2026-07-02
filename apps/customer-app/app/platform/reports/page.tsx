"use client";

import { useEffect, useState } from 'react';
import { AppShell } from '../../components/AppShell';
import { platformApi, DEFAULT_PLATFORM_TENANT } from '../platformApi';
import type { EdpReportsResponse } from '../platformApi';

export default function PlatformReportsPage() {
  const [reports, setReports] = useState<EdpReportsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadReports() {
      setLoading(true);
      setError('');
      try {
        const result = await platformApi.getReports(DEFAULT_PLATFORM_TENANT);
        setReports(result);
      } catch (err) {
        setError('Unable to load platform reports. Ensure the platform service is running.');
        setReports(null);
      } finally {
        setLoading(false);
      }
    }

    loadReports();
  }, []);

  return (
    <AppShell>
      <div className="space-y-6 p-6">
        <div className="rounded-md border border-border-default bg-background-surface p-6">
          <div className="text-sm font-semibold uppercase tracking-wide text-accent-primary">Data Platform Reports</div>
          <h1 className="mt-2 text-2xl font-semibold text-text-primary">EDP Reports</h1>
          <p className="mt-2 max-w-3xl text-sm text-text-secondary">
            Review generated reports for catalog health, data quality coverage, and lineage completeness.
          </p>
        </div>

        {loading ? (
          <div className="rounded-md border border-border-default bg-background-default p-6 text-sm text-text-secondary">Loading reports…</div>
        ) : error ? (
          <div className="rounded-md border border-border-default bg-danger-surface p-4 text-sm text-danger-foreground">{error}</div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {reports?.reports.map((report) => (
              <div key={report.report_type} className="rounded-md border border-border-default bg-background-surface p-4">
                <div className="text-sm text-text-secondary">{report.report_type}</div>
                <div className="mt-2 text-lg font-semibold text-text-primary">{report.status}</div>
                <div className="mt-1 text-sm text-text-secondary">Generated at {new Date(report.last_generated).toLocaleString()}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
}
