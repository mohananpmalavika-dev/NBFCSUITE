"use client";

import { useEffect, useState } from 'react';
import { AppShell } from '../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../accountingApi';
import type { AccountingPeriod, CalendarDashboard } from '../accountingApi';
import { CalendarMetric, CalendarPageFrame, CalendarTable, EmptyState, LoadingBlock, PeriodBadge, formatDate } from './calendarComponents';

export default function FinancialCalendarDashboardPage() {
  const [dashboard, setDashboard] = useState<CalendarDashboard | null>(null);
  const [periods, setPeriods] = useState<AccountingPeriod[]>([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const [dashboardBody, periodBody] = await Promise.all([
        accountingApi.getCalendarDashboard(DEFAULT_ACCOUNTING_TENANT),
        accountingApi.listPeriods(DEFAULT_ACCOUNTING_TENANT),
      ]);
      setDashboard(dashboardBody);
      setPeriods(periodBody.items.slice(0, 8));
    } catch {
      setDashboard(null);
      setPeriods([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <AppShell>
      <CalendarPageFrame
        title="Financial Calendar"
        description="Control financial years, accounting periods, posting windows, close orchestration, and calendar health across the enterprise."
      >
        {loading ? (
          <LoadingBlock />
        ) : dashboard ? (
          <div className="space-y-6">
            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="text-sm font-semibold text-text-primary">Tenant</div>
              <div className="text-sm text-text-secondary">{DEFAULT_ACCOUNTING_TENANT}</div>
              <div className="mt-2 text-sm text-text-secondary">{dashboard.summary.message}</div>
            </div>

            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
              <CalendarMetric label="Financial Year" value={dashboard.kpis.current_financial_year} note="Current calendar scope" />
              <CalendarMetric label="Open Periods" value={dashboard.kpis.open_periods} note="Posting currently allowed" />
              <CalendarMetric label="Closed Periods" value={dashboard.kpis.closed_periods} note="Soft, hard, or archived" />
              <CalendarMetric label="Health" value={`${dashboard.kpis.calendar_health}%`} note={dashboard.summary.status} />
            </div>

            <div className="grid gap-3 md:grid-cols-4">
              <CalendarMetric label="Pending EOD" value={dashboard.kpis.pending_eod} note="Business day close queue" />
              <CalendarMetric label="Pending EOM" value={dashboard.kpis.pending_eom} note="Month close due" />
              <CalendarMetric label="Pending EOY" value={dashboard.kpis.pending_eoy} note="Year-end close due" />
              <CalendarMetric label="Exceptions" value={dashboard.kpis.calendar_exceptions} note="Reopen or workflow issues" />
            </div>

            <CalendarTable columns={['Period', 'Financial Year', 'Start', 'End', 'Posting Window', 'Readiness', 'Status']}>
              {periods.map((period) => (
                <tr key={period.id} className="border-t border-border-light hover:bg-gray-50">
                  <td className="p-3 font-semibold text-text-primary">{period.period_name}</td>
                  <td className="p-3 text-text-secondary">{period.financial_year}</td>
                  <td className="p-3 text-text-secondary">{formatDate(period.period_start)}</td>
                  <td className="p-3 text-text-secondary">{formatDate(period.period_end)}</td>
                  <td className="p-3 text-text-secondary">{formatDate(period.posting_window.posting_allowed_to)}</td>
                  <td className="p-3 text-text-secondary">{period.ai.close_readiness}%</td>
                  <td className="p-3"><PeriodBadge value={period.status} /></td>
                </tr>
              ))}
              {periods.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-6 text-center text-text-secondary">No accounting periods found.</td>
                </tr>
              ) : null}
            </CalendarTable>
          </div>
        ) : (
          <EmptyState message="Financial Calendar API is unavailable. Check that the accounting service is running." />
        )}
      </CalendarPageFrame>
    </AppShell>
  );
}
