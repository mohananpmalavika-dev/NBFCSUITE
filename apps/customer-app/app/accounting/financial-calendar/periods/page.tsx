"use client";

import { useEffect, useState } from 'react';
import { AppShell } from '../../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../../accountingApi';
import type { AccountingPeriod, FinancialYear } from '../../accountingApi';
import { CalendarPageFrame, CalendarTable, EmptyState, LoadingBlock, PeriodBadge, formatDate } from '../calendarComponents';

type PeriodAction = 'open' | 'soft-close' | 'hard-close' | 'reopen';

export default function AccountingPeriodsPage() {
  const [years, setYears] = useState<FinancialYear[]>([]);
  const [items, setItems] = useState<AccountingPeriod[]>([]);
  const [year, setYear] = useState('');
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  async function load(selectedYear = year) {
    setLoading(true);
    try {
      const [yearBody, periodBody] = await Promise.all([
        accountingApi.listFinancialYears(DEFAULT_ACCOUNTING_TENANT),
        accountingApi.listPeriods(DEFAULT_ACCOUNTING_TENANT, selectedYear),
      ]);
      setYears(yearBody.items);
      setItems(periodBody.items);
    } catch {
      setYears([]);
      setItems([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function runAction(periodId: string, action: PeriodAction) {
    setBusyId(periodId);
    setMessage(null);
    try {
      const result = await accountingApi.setPeriodState(periodId, DEFAULT_ACCOUNTING_TENANT, action, action);
      setMessage(`${result.period_name} is now ${result.status}`);
      await load();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Action failed');
    } finally {
      setBusyId(null);
    }
  }

  function changeYear(value: string) {
    setYear(value);
    load(value);
  }

  return (
    <AppShell>
      <CalendarPageFrame
        title="Accounting Periods"
        description="Govern posting windows, period states, close readiness, and reopen workflows."
      >
        <div className="space-y-4">
          <div className="flex flex-col gap-3 rounded-md border border-border-default bg-background-surface p-4 sm:flex-row sm:items-end sm:justify-between">
            <label className="block space-y-1">
              <span className="text-sm font-semibold text-text-secondary">Financial Year</span>
              <select className="h-10 min-w-[220px] rounded-md border border-border-default px-3 text-sm" value={year} onChange={(event) => changeYear(event.target.value)}>
                <option value="">All years</option>
                {years.map((item) => (
                  <option key={item.id} value={item.year_code}>{item.year_code}</option>
                ))}
              </select>
            </label>
            <div className="text-sm text-text-secondary">Soft close permits late adjustments; hard close blocks posting and requires reopen approval.</div>
          </div>

          {message ? <div className="rounded-md border border-border-default bg-background-surface p-3 text-sm text-text-secondary">{message}</div> : null}

          {loading ? (
            <LoadingBlock />
          ) : items.length === 0 ? (
            <EmptyState message="No accounting periods found. Create a financial year to generate periods." />
          ) : (
            <CalendarTable columns={['Period', 'Year', 'Start', 'End', 'Posting Until', 'Readiness', 'Status', 'Actions']}>
              {items.map((period) => (
                <tr key={period.id} className="border-t border-border-light hover:bg-gray-50">
                  <td className="p-3 font-semibold text-text-primary">{period.period_name}</td>
                  <td className="p-3 text-text-secondary">{period.financial_year}</td>
                  <td className="p-3 text-text-secondary">{formatDate(period.period_start)}</td>
                  <td className="p-3 text-text-secondary">{formatDate(period.period_end)}</td>
                  <td className="p-3 text-text-secondary">{formatDate(period.posting_window.posting_allowed_to)}</td>
                  <td className="p-3 text-text-secondary">{period.ai.close_readiness}%</td>
                  <td className="p-3"><PeriodBadge value={period.status} /></td>
                  <td className="p-3">
                    <div className="flex flex-wrap gap-2">
                      {(['open', 'soft-close', 'hard-close', 'reopen'] as PeriodAction[]).map((action) => (
                        <button
                          key={action}
                          type="button"
                          onClick={() => runAction(period.id, action)}
                          disabled={busyId === period.id}
                          className="h-8 rounded-md border border-border-default px-2 text-xs font-semibold text-text-secondary hover:bg-background-accent disabled:opacity-60"
                        >
                          {action}
                        </button>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </CalendarTable>
          )}
        </div>
      </CalendarPageFrame>
    </AppShell>
  );
}
