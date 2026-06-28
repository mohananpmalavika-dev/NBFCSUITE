'use client';

import { AlertTriangle, CheckCircle2, Info, XCircle } from 'lucide-react';
import type { JournalStatus } from '@/lib/api';
import type { JournalValidation } from './journal-types';

const statusStyles: Record<JournalStatus, string> = {
  draft: 'border-slate-300 bg-slate-100 text-slate-700',
  pending: 'border-amber-300 bg-amber-50 text-amber-800',
  approved: 'border-blue-300 bg-blue-50 text-blue-800',
  posted: 'border-emerald-300 bg-emerald-50 text-emerald-800',
  reversed: 'border-violet-300 bg-violet-50 text-violet-800',
  cancelled: 'border-rose-300 bg-rose-50 text-rose-800',
};

export function money(value: number | null | undefined, currency = 'INR') {
  return `${currency} ${Number(value || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
}

export function journalDate(value?: string | null, includeTime = false) {
  if (!value) return '-';
  const options: Intl.DateTimeFormatOptions = includeTime
    ? { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }
    : { day: '2-digit', month: 'short', year: 'numeric' };
  return new Date(value).toLocaleString('en-IN', options);
}

export function journalError(error: unknown, fallback: string) {
  const candidate = error as { response?: { data?: { detail?: string | { message?: string; errors?: string[] } } } };
  const detail = candidate.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (detail?.errors?.length) return detail.errors.join(' ');
  return detail?.message || fallback;
}

export function StatusBadge({ status }: { status: JournalStatus }) {
  return (
    <span className={`inline-flex h-7 items-center rounded border px-2 text-[11px] font-bold uppercase ${statusStyles[status]}`}>
      {status}
    </span>
  );
}

export function ValidationPanel({ result, compact = false }: { result: JournalValidation | null; compact?: boolean }) {
  if (!result) {
    return (
      <div className="flex items-center gap-2 border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600">
        <Info className="h-4 w-4" /> Run validation to see accounting controls and impact.
      </div>
    );
  }

  return (
    <section className="border border-slate-200 bg-white">
      <div className={`flex items-center justify-between gap-3 border-b px-4 ${compact ? 'py-3' : 'py-4'} ${result.valid ? 'border-emerald-200 bg-emerald-50' : 'border-rose-200 bg-rose-50'}`}>
        <div className="flex items-center gap-2">
          {result.valid ? <CheckCircle2 className="h-5 w-5 text-emerald-700" /> : <XCircle className="h-5 w-5 text-rose-700" />}
          <div>
            <p className={`text-sm font-black ${result.valid ? 'text-emerald-900' : 'text-rose-900'}`}>
              {result.valid ? 'Ready for workflow' : 'Posting controls failed'}
            </p>
            <p className="text-xs font-semibold text-slate-600">
              Debit {money(result.total_debit)} / Credit {money(result.total_credit)}
            </p>
          </div>
        </div>
        <span className="text-xs font-bold text-slate-600">{result.checks.filter((check) => check.status === 'passed').length}/{result.checks.length} checks</span>
      </div>
      <div className={`grid gap-2 p-4 ${compact ? '' : 'sm:grid-cols-2'}`}>
        {result.checks.map((check) => (
          <div key={check.key} className="flex items-start gap-2 text-xs">
            {check.status === 'passed'
              ? <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" />
              : <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-rose-600" />}
            <div>
              <p className="font-bold text-slate-800">{check.label}</p>
              {check.detail ? <p className="mt-0.5 text-slate-500">{check.detail}</p> : null}
            </div>
          </div>
        ))}
      </div>
      {result.errors.length ? (
        <div className="border-t border-rose-200 bg-rose-50 px-4 py-3">
          {result.errors.map((error) => <p key={error} className="text-xs font-semibold text-rose-800">{error}</p>)}
        </div>
      ) : null}
      {result.warnings.length ? (
        <div className="flex gap-2 border-t border-amber-200 bg-amber-50 px-4 py-3 text-xs font-semibold text-amber-900">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          <div>{result.warnings.map((warning) => <p key={warning}>{warning}</p>)}</div>
        </div>
      ) : null}
    </section>
  );
}

