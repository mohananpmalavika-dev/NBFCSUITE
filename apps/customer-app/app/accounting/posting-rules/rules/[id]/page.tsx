"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { AppShell } from '../../../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../../../accountingApi';
import type { PostingRule } from '../../../accountingApi';
import { EmptyState, LoadingBlock, RuleBadge, RuleMetric, RulePageFrame, RuleTable, formatDate } from '../../ruleComponents';

function asList(value: unknown): string[] {
  return Array.isArray(value) ? value.map((item) => String(item)) : [];
}

function formatValue(value: unknown, fallback = '-') {
  if (value === null || value === undefined || value === '') return fallback;
  if (typeof value === 'object') return Object.entries(value as Record<string, unknown>).filter(([, item]) => item).map(([key, item]) => `${key}: ${String(item)}`).join(', ') || fallback;
  return String(value);
}

export default function PostingRuleProfilePage() {
  const params = useParams<{ id: string }>();
  const [rule, setRule] = useState<PostingRule | null>(null);
  const [versions, setVersions] = useState<PostingRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  async function load() {
    if (!params.id) return;
    setLoading(true);
    try {
      const [ruleBody, versionBody] = await Promise.all([
        accountingApi.getPostingRule(params.id, DEFAULT_ACCOUNTING_TENANT),
        accountingApi.getPostingRuleVersions(params.id, DEFAULT_ACCOUNTING_TENANT),
      ]);
      setRule(ruleBody);
      setVersions(versionBody.items);
      setMessage('');
    } catch {
      setRule(null);
      setVersions([]);
      setMessage('Posting rule profile is unavailable.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [params.id]);

  async function publish() {
    if (!rule) return;
    setMessage('Publishing rule...');
    try {
      await accountingApi.publishPostingRule(rule.id, DEFAULT_ACCOUNTING_TENANT);
      setMessage('Rule published.');
      await load();
    } catch {
      setMessage('Unable to publish this rule.');
    }
  }

  return (
    <AppShell>
      <RulePageFrame title="Posting Rule 360" description="Complete business, accounting, operations, governance, and AI view for a posting rule.">
        {loading ? (
          <LoadingBlock />
        ) : rule ? (
          <div className="space-y-6">
            {(() => {
              const executionCount = rule.execution_summary?.execution_count ?? 0;
              const successCount = rule.execution_summary?.success_count ?? 0;
              const successRate = rule.execution_summary?.success_rate ?? (executionCount ? Math.round((successCount / executionCount) * 100) : 0);
              const healthScore = rule.ai?.health_score ?? (rule.ai?.predicted_failure === 'medium' ? 82 : 100);
              return (
                <>
            <div className="flex flex-col gap-3 rounded-md border border-border-default bg-background-surface p-4 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <h2 className="text-xl font-semibold text-text-primary">{rule.rule_name ?? rule.rule_code}</h2>
                  <RuleBadge value={rule.status} />
                  <RuleBadge value={rule.approval_status} />
                </div>
                <p className="mt-1 text-sm text-text-secondary">{rule.rule_code} handles {rule.source_module}.{rule.source_event}</p>
                <p className="mt-1 text-sm text-text-secondary">Valid from {formatDate(rule.effective_from)} to {formatDate(rule.effective_to)}</p>
              </div>
              <div className="flex flex-wrap gap-2">
                <Link href={`/accounting/posting-rules/simulation?ruleId=${rule.id}`} className="inline-flex h-9 items-center rounded-md border border-border-default px-3 text-sm font-semibold text-text-secondary hover:bg-background-accent">
                  Simulate
                </Link>
                <button type="button" onClick={publish} className="inline-flex h-9 items-center rounded-md border border-border-default px-3 text-sm font-semibold text-text-secondary hover:bg-background-accent">
                  Publish
                </button>
              </div>
            </div>

            {message ? <div className="rounded-md border border-border-default bg-background-surface p-3 text-sm text-text-secondary">{message}</div> : null}

            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
              <RuleMetric label="Version" value={`v${rule.version ?? 1}`} note={rule.supersedes_rule_id ? 'Derived from prior rule' : 'Current lineage root'} />
              <RuleMetric label="Priority" value={rule.priority ?? 100} note={formatValue(rule.scope, 'Enterprise scope')} />
              <RuleMetric label="Executions" value={executionCount} note={`${successRate}% success rate`} />
              <RuleMetric label="Rule Health" value={`${healthScore}%`} note={rule.ai?.recommendation ?? 'No exceptions detected'} />
            </div>

            <div className="grid gap-4 xl:grid-cols-2">
              <section className="rounded-md border border-border-default bg-background-surface p-4">
                <h3 className="font-semibold text-text-primary">Business View</h3>
                <div className="mt-3 grid gap-2 text-sm text-text-secondary md:grid-cols-2">
                  <div>Module: {rule.source_module}</div>
                  <div>Event: {rule.source_event}</div>
                  <div>Product: {rule.product ?? 'Enterprise Default'}</div>
                  <div>Scope: {formatValue(rule.scope, 'enterprise')}</div>
                </div>
              </section>

              <section className="rounded-md border border-border-default bg-background-surface p-4">
                <h3 className="font-semibold text-text-primary">Governance View</h3>
                <div className="mt-3 grid gap-2 text-sm text-text-secondary md:grid-cols-2">
                  <div>Approval: {rule.approval_status ?? 'draft'}</div>
                  <div>Workflow: {asList(rule.workflow).join(', ') || 'Finance review'}</div>
                  <div>Created: {formatDate(rule.created_at)}</div>
                  <div>Updated: {formatDate(rule.updated_at)}</div>
                </div>
              </section>
            </div>

            <RuleTable columns={['Side', 'GL Account', 'Formula', 'Currency', 'Dimensions', 'Description']}>
              {[...(rule.debit_lines ?? []), ...(rule.credit_lines ?? [])].map((line, index) => (
                <tr key={`${line.direction}-${index}`} className="border-t border-border-light hover:bg-gray-50">
                  <td className="p-3 font-semibold text-text-primary">{line.direction}</td>
                  <td className="p-3 text-text-secondary">{line.account_code}</td>
                  <td className="p-3 text-text-secondary">{line.formula ?? '-'}</td>
                  <td className="p-3 text-text-secondary">{line.currency ?? 'INR'}</td>
                  <td className="p-3 text-text-secondary">{Object.keys(line.dimension_source ?? {}).join(', ') || '-'}</td>
                  <td className="p-3 text-text-secondary">{line.description ?? '-'}</td>
                </tr>
              ))}
            </RuleTable>

            <div className="grid gap-4 xl:grid-cols-2">
              <section className="rounded-md border border-border-default bg-background-surface p-4">
                <h3 className="font-semibold text-text-primary">Conditions</h3>
                <div className="mt-3 space-y-2 text-sm text-text-secondary">
                  {(rule.conditions ?? []).length === 0 ? <div>No conditions configured.</div> : null}
                  {(rule.conditions ?? []).map((condition, index) => (
                    <div key={`${condition.field}-${index}`}>{condition.field} {condition.operator} {formatValue(condition.value)}</div>
                  ))}
                </div>
              </section>

              <section className="rounded-md border border-border-default bg-background-surface p-4">
                <h3 className="font-semibold text-text-primary">AI View</h3>
                <div className="mt-3 space-y-2 text-sm text-text-secondary">
                  <div>Conflict detection: {rule.ai?.conflict_detection ?? 'clear'}</div>
                  <div>Duplicate risk: {rule.ai?.duplicate_risk ?? 'low'}</div>
                  <div>Predicted failure: {rule.ai?.predicted_failure ?? 'low'}</div>
                  <div>Recommendation: {rule.ai?.recommendation ?? 'Run simulations before production publishing.'}</div>
                </div>
              </section>
            </div>

            <RuleTable columns={['Version', 'Rule', 'Effective From', 'Effective To', 'Approval', 'Status']}>
              {versions.map((version) => (
                <tr key={version.id} className="border-t border-border-light hover:bg-gray-50">
                  <td className="p-3 font-semibold text-text-primary">v{version.version}</td>
                  <td className="p-3 text-text-secondary">{version.rule_name ?? version.rule_code}</td>
                  <td className="p-3 text-text-secondary">{formatDate(version.effective_from)}</td>
                  <td className="p-3 text-text-secondary">{formatDate(version.effective_to)}</td>
                  <td className="p-3"><RuleBadge value={version.approval_status} /></td>
                  <td className="p-3"><RuleBadge value={version.status} /></td>
                </tr>
              ))}
            </RuleTable>
                </>
              );
            })()}
          </div>
        ) : (
          <EmptyState message={message || 'Posting rule was not found.'} />
        )}
      </RulePageFrame>
    </AppShell>
  );
}
