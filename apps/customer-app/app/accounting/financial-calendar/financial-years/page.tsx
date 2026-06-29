"use client";

import { useEffect, useState } from 'react';
import { AppShell } from '../../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../../accountingApi';
import type { FinancialYear } from '../../accountingApi';
import { CalendarPageFrame, CalendarTable, EmptyState, LoadingBlock, PeriodBadge, formatDate } from '../calendarComponents';

const initialForm = {
  year_code: '2026-27',
  description: 'Fiscal year 2026-27',
  start_date: '2026-04-01',
  end_date: '2027-03-31',
  calendar_type: 'fiscal',
  status: 'active',
};

export default function FinancialYearsPage() {
  const [items, setItems] = useState<FinancialYear[]>([]);
  const [form, setForm] = useState(initialForm);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    try {
      const body = await accountingApi.listFinancialYears(DEFAULT_ACCOUNTING_TENANT);
      setItems(body.items);
    } catch {
      setItems([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  function update(field: keyof typeof initialForm, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function submit() {
    setSaving(true);
    setMessage(null);
    try {
      const result = await accountingApi.createFinancialYear({
        tenant_id: DEFAULT_ACCOUNTING_TENANT,
        year_code: form.year_code.trim(),
        description: form.description.trim(),
        start_date: `${form.start_date}T00:00:00`,
        end_date: `${form.end_date}T23:59:59`,
        calendar_type: form.calendar_type,
        status: form.status,
        calendars: ['Corporate', 'Payroll', 'Treasury', 'Forex', 'Tax'],
        close_schedule: { daily_close: 'EOD', month_close: 'M+5', year_close: 'Y+30' },
        generate_periods: 'true',
        performed_by: 'finance-console',
      });
      setMessage(`Created ${result.financial_year.year_code} and generated ${result.generated_count} periods`);
      await load();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Create failed');
    } finally {
      setSaving(false);
    }
  }

  return (
    <AppShell>
      <CalendarPageFrame
        title="Financial Years"
        description="Create fiscal years, assign enterprise calendars, and generate monthly accounting periods for close orchestration."
      >
        <div className="space-y-4">
          <div className="rounded-md border border-border-default bg-background-surface p-4">
            <div className="grid gap-3 md:grid-cols-3">
              <label className="block space-y-1">
                <span className="text-sm font-semibold text-text-secondary">Year Code</span>
                <input className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={form.year_code} onChange={(event) => update('year_code', event.target.value)} />
              </label>
              <label className="block space-y-1 md:col-span-2">
                <span className="text-sm font-semibold text-text-secondary">Description</span>
                <input className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={form.description} onChange={(event) => update('description', event.target.value)} />
              </label>
              <label className="block space-y-1">
                <span className="text-sm font-semibold text-text-secondary">Start Date</span>
                <input type="date" className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={form.start_date} onChange={(event) => update('start_date', event.target.value)} />
              </label>
              <label className="block space-y-1">
                <span className="text-sm font-semibold text-text-secondary">End Date</span>
                <input type="date" className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={form.end_date} onChange={(event) => update('end_date', event.target.value)} />
              </label>
              <label className="block space-y-1">
                <span className="text-sm font-semibold text-text-secondary">Calendar Type</span>
                <select className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={form.calendar_type} onChange={(event) => update('calendar_type', event.target.value)}>
                  <option value="fiscal">Fiscal</option>
                  <option value="calendar">Calendar</option>
                  <option value="custom">Custom</option>
                </select>
              </label>
            </div>
            <div className="mt-4 flex items-center justify-between gap-3">
              <div className="text-sm text-text-secondary">Generates 12 monthly periods with Corporate, Payroll, Treasury, Forex, and Tax calendars.</div>
              <button
                type="button"
                onClick={submit}
                disabled={saving || !form.year_code.trim() || !form.start_date || !form.end_date}
                className="h-10 rounded-md bg-accent-primary px-3 text-sm font-semibold text-accent-onPrimary disabled:opacity-60"
              >
                {saving ? 'Creating...' : 'Create Year'}
              </button>
            </div>
          </div>

          {message ? <div className="rounded-md border border-border-default bg-background-surface p-3 text-sm text-text-secondary">{message}</div> : null}

          {loading ? (
            <LoadingBlock />
          ) : items.length === 0 ? (
            <EmptyState message="No financial years found." />
          ) : (
            <CalendarTable columns={['Year', 'Description', 'Start', 'End', 'Type', 'Calendars', 'Status']}>
              {items.map((year) => (
                <tr key={year.id} className="border-t border-border-light hover:bg-gray-50">
                  <td className="p-3 font-semibold text-text-primary">{year.year_code}</td>
                  <td className="p-3 text-text-secondary">{year.description ?? '-'}</td>
                  <td className="p-3 text-text-secondary">{formatDate(year.start_date)}</td>
                  <td className="p-3 text-text-secondary">{formatDate(year.end_date)}</td>
                  <td className="p-3 text-text-secondary">{year.calendar_type}</td>
                  <td className="p-3 text-text-secondary">{year.calendars.join(', ') || '-'}</td>
                  <td className="p-3"><PeriodBadge value={year.status} /></td>
                </tr>
              ))}
            </CalendarTable>
          )}
        </div>
      </CalendarPageFrame>
    </AppShell>
  );
}
