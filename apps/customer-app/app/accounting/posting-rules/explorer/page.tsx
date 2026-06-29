"use client";

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../../accountingApi';
import type { PostingRule } from '../../accountingApi';
import { EmptyState, LoadingBlock, RuleActionButton, RuleBadge, RulePageFrame, RuleTable, formatDate } from '../ruleComponents';

export default function RuleExplorerPage() {
  const [items, setItems] = useState<PostingRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');
  const [module, setModule] = useState('');
  const [status, setStatus] = useState('');
  const [busyId, setBusyId] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const params = useMemo(() => {
    const parts = ['limit=100'];
    if (query.trim()) parts.push(`q=${encodeURIComponent(query.trim())}`);
    if (module) parts.push(`source_module=${encodeURIComponent(module)}`);
    if (status) parts.push(`status=${encodeURIComponent(status)}`);
    return parts.join('&');
  }, [query, module, status]);

  async function load() {
    setLoading(true);
    try {
      const body = await accountingApi.listPostingRules(DEFAULT_ACCOUNTING_TENANT, params);
      setItems(body.items);
    } catch {
      setItems([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [params]);

  async function publish(rule: PostingRule) {
    setBusyId(rule.id);
    setMessage(null);
    try {
      const result = await accountingApi.publishPostingRule(rule.id, DEFAULT_ACCOUNTING_TENANT);
      setMessage(`${result.rule_name ?? result.rule_code} published`);
      await load();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Publish failed');
    } finally {
      setBusyId(null);
    }
  }

  return (
    <AppShell>
      <RulePageFrame title="Rule Explorer" description="Search, filter, inspect, publish, export, and compare posting rules by event, product, status, and effective date.">
        <div className="space-y-4">
          <div className="grid gap-3 rounded-md border border-border-default bg-background-surface p-4 md:grid-cols-[minmax(220px,1fr)_180px_180px]">
            <label className="block space-y-1">
              <span className="text-sm font-semibold text-text-secondary">Search</span>
              <input className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Rule, module, event" />
            </label>
            <label className="block space-y-1">
              <span className="text-sm font-semibold text-text-secondary">Module</span>
              <select className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={module} onChange={(event) => setModule(event.target.value)}>
                <option value="">All modules</option>
                {['loans', 'deposits', 'collections', 'treasury', 'forex', 'hrms', 'procurement', 'assets'].map((item) => <option key={item} value={item}>{item}</option>)}
              </select>
            </label>
            <label className="block space-y-1">
              <span className="text-sm font-semibold text-text-secondary">Status</span>
              <select className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={status} onChange={(event) => setStatus(event.target.value)}>
                <option value="">All statuses</option>
                {['draft', 'pending_approval', 'active', 'archived'].map((item) => <option key={item} value={item}>{item}</option>)}
              </select>
            </label>
          </div>

          {message ? <div className="rounded-md border border-border-default bg-background-surface p-3 text-sm text-text-secondary">{message}</div> : null}

          {loading ? (
            <LoadingBlock />
          ) : items.length === 0 ? (
            <EmptyState message="No posting rules matched the current filters." />
          ) : (
            <RuleTable columns={['Rule Code', 'Rule Name', 'Accounting Event', 'Product', 'Version', 'Priority', 'Effective Date', 'Status', 'Actions']}>
              {items.map((rule) => (
                <tr key={rule.id} className="border-t border-border-light hover:bg-gray-50">
                  <td className="p-3 font-semibold"><Link href={`/accounting/posting-rules/rules/${rule.id}`} className="text-accent-primary underline">{rule.rule_code}</Link></td>
                  <td className="p-3 text-text-secondary">{rule.rule_name ?? '-'}</td>
                  <td className="p-3 text-text-secondary">{rule.source_module}.{rule.source_event}</td>
                  <td className="p-3 text-text-secondary">{rule.product ?? 'Enterprise Default'}</td>
                  <td className="p-3 text-text-secondary">v{rule.version}</td>
                  <td className="p-3 text-text-secondary">{rule.priority}</td>
                  <td className="p-3 text-text-secondary">{formatDate(rule.effective_from)}</td>
                  <td className="p-3"><RuleBadge value={rule.status} /></td>
                  <td className="p-3">
                    <div className="flex flex-wrap gap-2">
                      <Link href={`/accounting/posting-rules/simulation?rule=${rule.id}`} className="inline-flex h-8 items-center rounded-md border border-border-default px-2 text-xs font-semibold text-text-secondary hover:bg-background-accent">Simulate</Link>
                      <RuleActionButton onClick={() => publish(rule)} disabled={busyId === rule.id}>Publish</RuleActionButton>
                    </div>
                  </td>
                </tr>
              ))}
            </RuleTable>
          )}
        </div>
      </RulePageFrame>
    </AppShell>
  );
}
