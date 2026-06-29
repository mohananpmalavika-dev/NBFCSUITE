"use client";

import { useEffect, useMemo, useState } from 'react';
import { AppShell } from '../../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../../accountingApi';
import type { AccountingPeriod, EodMonitor, FinancialYear } from '../../accountingApi';
import { CalendarMetric, CalendarPageFrame, CalendarTable, EmptyState, LoadingBlock, PeriodBadge, formatDate } from '../calendarComponents';

export default function CloseMonitorPage() {
  const [eod, setEod] = useState<EodMonitor | null>(null);
  const [periods, setPeriods] = useState<AccountingPeriod[]>([]);
  const [years, setYears] = useState<FinancialYear[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const firstOpenPeriod = useMemo(() => periods.find((period) => period.status === 'open' || period.status === 'soft_close'), [periods]);
  const activeYear = useMemo(() => years.find((year) => year.status === 'active') ?? years[0], [years]);

  async function load() {
    setLoading(true);
    try {
      const [eodBody, periodBody, yearBody] = await Promise.all([
        accountingApi.getEodMonitor(DEFAULT_ACCOUNTING_TENANT),
        accountingApi.listPeriods(DEFAULT_ACCOUNTING_TENANT),
        accountingApi.listFinancialYears(DEFAULT_ACCOUNTING_TENANT),
      ]);
      setEod(eodBody);
      setPeriods(periodBody.items);
      setYears(yearBody.items);
    } catch {
      setEod(null);
      setPeriods([]);
      setYears([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function execute(label: 'eod' | 'eom' | 'eoy') {
    setBusy(true);
    setMessage(null);
    try {
      if (label === 'eod') {
        const result = await accountingApi.executeEod(DEFAULT_ACCOUNTING_TENANT, new Date().toISOString());
        setMessage(result.event);
      }
      if (label === 'eom' && firstOpenPeriod) {
        const result = await accountingApi.executeEom(DEFAULT_ACCOUNTING_TENANT, firstOpenPeriod.id);
        setMessage(`${result.event}: ${result.period.period_name}`);
      }
      if (label === 'eoy' && activeYear) {
        const result = await accountingApi.executeEoy(DEFAULT_ACCOUNTING_TENANT, activeYear.year_code);
        setMessage(`${result.event}: archived ${result.periods_archived} periods`);
      }
      await load();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Close execution failed');
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppShell>
      <CalendarPageFrame
        title="Closing Monitor"
        description="Track EOD, EOM, and EOY readiness with operational close tasks, approvals, and AI recommendations."
      >
        {loading ? (
          <LoadingBlock />
        ) : eod ? (
          <div className="space-y-6">
            <div className="grid gap-3 md:grid-cols-4">
              <CalendarMetric label="Business Day" value={eod.business_day.date} note={eod.business_day.status} />
              <CalendarMetric label="Open Queue" value={periods.filter((period) => period.status === 'open').length} note="Periods ready for close" />
              <CalendarMetric label="Soft Close" value={periods.filter((period) => period.status === 'soft_close').length} note="Late adjustment window" />
              <CalendarMetric label="Hard Close" value={periods.filter((period) => period.status === 'hard_close' || period.status === 'archived').length} note="Locked periods" />
            </div>

            <div className="flex flex-col gap-3 rounded-md border border-border-default bg-background-surface p-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <div className="text-sm font-semibold text-text-primary">Close Orchestration</div>
                <div className="text-sm text-text-secondary">Validate transactions, post accounting events, reconcile GL, collect approvals, and lock the period.</div>
              </div>
              <div className="flex flex-wrap gap-2">
                <button type="button" onClick={() => execute('eod')} disabled={busy} className="h-10 rounded-md border border-border-default px-3 text-sm font-semibold text-text-secondary disabled:opacity-60">Run EOD</button>
                <button type="button" onClick={() => execute('eom')} disabled={busy || !firstOpenPeriod} className="h-10 rounded-md border border-border-default px-3 text-sm font-semibold text-text-secondary disabled:opacity-60">Run EOM</button>
                <button type="button" onClick={() => execute('eoy')} disabled={busy || !activeYear} className="h-10 rounded-md bg-accent-primary px-3 text-sm font-semibold text-accent-onPrimary disabled:opacity-60">Run EOY</button>
              </div>
            </div>

            {message ? <div className="rounded-md border border-border-default bg-background-surface p-3 text-sm text-text-secondary">{message}</div> : null}

            <CalendarTable columns={['Close Date', 'Branch', 'Status', 'Balanced', 'Closed By', 'Closed At']}>
              {eod.items.map((item) => (
                <tr key={String(item.id)} className="border-t border-border-light hover:bg-gray-50">
                  <td className="p-3 font-semibold text-text-primary">{formatDate(String(item.business_date ?? ''))}</td>
                  <td className="p-3 text-text-secondary">{String(item.branch_id ?? '-')}</td>
                  <td className="p-3"><PeriodBadge value={String(item.status ?? 'unknown')} /></td>
                  <td className="p-3 text-text-secondary">{String(item.is_balanced ?? '-')}</td>
                  <td className="p-3 text-text-secondary">{String(item.closed_by ?? '-')}</td>
                  <td className="p-3 text-text-secondary">{formatDate(String(item.closed_at ?? ''))}</td>
                </tr>
              ))}
              {eod.items.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-6 text-center text-text-secondary">No EOD close runs found.</td>
                </tr>
              ) : null}
            </CalendarTable>
          </div>
        ) : (
          <EmptyState message="Close monitor data is unavailable. Check that the accounting service is running." />
        )}
      </CalendarPageFrame>
    </AppShell>
  );
}
