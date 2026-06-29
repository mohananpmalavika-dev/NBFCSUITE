"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../../../accountingApi';
import type { AccountingEvent } from '../../../accountingApi';
import { EmptyState, EventActionButton, EventBadge, EventMetric, EventPageFrame, EventTable, LoadingBlock, formatAmount, formatDate } from '../../eventComponents';

function JsonPanel({ title, value }: { title: string; value: unknown }) {
  return (
    <div className="rounded-md border border-border-default bg-background-surface p-4">
      <div className="text-sm font-semibold text-text-primary">{title}</div>
      <pre className="mt-3 max-h-72 overflow-auto rounded bg-gray-50 p-3 text-xs text-text-secondary">{JSON.stringify(value ?? {}, null, 2)}</pre>
    </div>
  );
}

export default function EventProfilePage({ params }: { params: { id: string } }) {
  const [event, setEvent] = useState<AccountingEvent | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    try {
      setEvent(await accountingApi.getEvent(params.id, DEFAULT_ACCOUNTING_TENANT));
    } catch {
      setEvent(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [params.id]);

  async function run(action: 'validate' | 'retry' | 'replay') {
    setBusy(true);
    setMessage(null);
    try {
      const result =
        action === 'validate'
          ? await accountingApi.validateEvent(params.id, DEFAULT_ACCOUNTING_TENANT)
          : action === 'retry'
            ? await accountingApi.retryEvent(params.id, DEFAULT_ACCOUNTING_TENANT)
            : await accountingApi.replayEvent(params.id, DEFAULT_ACCOUNTING_TENANT);
      setEvent(result);
      setMessage(`${action} completed: ${result.status}`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : `${action} failed`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppShell>
      <EventPageFrame title="Accounting Event 360" description="Complete operational, financial, validation, audit, and AI view of an accounting event.">
        {loading ? (
          <LoadingBlock />
        ) : event ? (
          <div className="space-y-6">
            <div className="flex flex-col gap-3 rounded-md border border-border-default bg-background-surface p-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <Link href="/accounting/event-engine/explorer" className="text-sm font-semibold text-accent-primary underline">Back to Event Explorer</Link>
                <div className="mt-2 text-xl font-semibold text-text-primary">{event.event_type}</div>
                <div className="text-sm text-text-secondary">{event.source_module} / {event.reference_number ?? event.reference_id}</div>
              </div>
              <div className="flex flex-wrap gap-2">
                <EventActionButton onClick={() => run('validate')} disabled={busy}>Validate</EventActionButton>
                <EventActionButton onClick={() => run('retry')} disabled={busy}>Retry</EventActionButton>
                <EventActionButton onClick={() => run('replay')} disabled={busy}>Replay</EventActionButton>
              </div>
            </div>

            {message ? <div className="rounded-md border border-border-default bg-background-surface p-3 text-sm text-text-secondary">{message}</div> : null}

            <div className="grid gap-3 md:grid-cols-4">
              <EventMetric label="Status" value={event.status} note={event.queue_status} />
              <EventMetric label="Validation" value={event.validation_status} note={`${event.validation_result?.errors?.length ?? 0} errors`} />
              <EventMetric label="Amount" value={formatAmount(event.amount, event.currency)} note={formatDate(event.business_date)} />
              <EventMetric label="Version" value={event.version} note={`${event.retry_count} retries`} />
            </div>

            <EventTable columns={['View', 'Key Details']}>
              <tr className="border-t border-border-light">
                <td className="p-3 font-semibold text-text-primary">Business</td>
                <td className="p-3 text-text-secondary">{String(event.business_view?.source_module ?? event.source_module)} / {String(event.business_view?.business_transaction ?? event.event_type)}</td>
              </tr>
              <tr className="border-t border-border-light">
                <td className="p-3 font-semibold text-text-primary">Processing</td>
                <td className="p-3 text-text-secondary"><EventBadge value={event.queue_status} /> <span className="ml-2">{event.processing_time_ms}ms</span></td>
              </tr>
              <tr className="border-t border-border-light">
                <td className="p-3 font-semibold text-text-primary">Financial</td>
                <td className="p-3 text-text-secondary">Rule {String(event.financial_view?.posting_rule_id ?? event.posting_rule_id ?? 'default/pending')}, journal {String(event.financial_view?.journal_id ?? event.journal_id ?? '-')}</td>
              </tr>
              <tr className="border-t border-border-light">
                <td className="p-3 font-semibold text-text-primary">AI</td>
                <td className="p-3 text-text-secondary">{String(event.ai_view?.failure_prediction ?? 'low')} failure prediction, {String(event.ai_view?.duplicate_risk ?? 'low')} duplicate risk</td>
              </tr>
            </EventTable>

            {event.validation_result?.checks?.length ? (
              <EventTable columns={['Check', 'Status', 'Detail']}>
                {event.validation_result.checks.map((check) => (
                  <tr key={check.key} className="border-t border-border-light">
                    <td className="p-3 font-semibold text-text-primary">{check.label}</td>
                    <td className="p-3"><EventBadge value={check.status} /></td>
                    <td className="p-3 text-text-secondary">{check.detail ?? '-'}</td>
                  </tr>
                ))}
              </EventTable>
            ) : null}

            <div className="grid gap-3 xl:grid-cols-2">
              <JsonPanel title="Payload" value={event.payload} />
              <JsonPanel title="Dimensions" value={event.dimensions} />
              <JsonPanel title="Audit View" value={event.audit_view} />
              <JsonPanel title="AI View" value={event.ai_view} />
            </div>
          </div>
        ) : (
          <EmptyState message="Accounting event was not found." />
        )}
      </EventPageFrame>
    </AppShell>
  );
}
