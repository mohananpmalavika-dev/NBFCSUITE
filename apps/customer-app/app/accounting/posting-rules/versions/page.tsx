"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../../accountingApi';
import type { PostingRule } from '../../accountingApi';
import { EmptyState, LoadingBlock, RuleBadge, RulePageFrame, RuleTable, formatDate } from '../ruleComponents';

export default function RuleVersionsPage() {
  const [rules, setRules] = useState<PostingRule[]>([]);
  const [ruleId, setRuleId] = useState('');
  const [versions, setVersions] = useState<PostingRule[]>([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const body = await accountingApi.listPostingRules(DEFAULT_ACCOUNTING_TENANT, 'limit=100');
      setRules(body.items);
      const selected = ruleId || body.items[0]?.id || '';
      setRuleId(selected);
      if (selected) {
        const versionBody = await accountingApi.getPostingRuleVersions(selected, DEFAULT_ACCOUNTING_TENANT);
        setVersions(versionBody.items);
      }
    } catch {
      setRules([]);
      setVersions([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function changeRule(value: string) {
    setRuleId(value);
    setLoading(true);
    try {
      const body = await accountingApi.getPostingRuleVersions(value, DEFAULT_ACCOUNTING_TENANT);
      setVersions(body.items);
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell>
      <RulePageFrame title="Rule Versions" description="Compare posting rule versions, effective dates, approval states, and accounting impact lineage.">
        <div className="space-y-4">
          <div className="rounded-md border border-border-default bg-background-surface p-4">
            <label className="block max-w-md space-y-1">
              <span className="text-sm font-semibold text-text-secondary">Rule</span>
              <select className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={ruleId} onChange={(event) => changeRule(event.target.value)}>
                {rules.map((rule) => <option key={rule.id} value={rule.id}>{rule.rule_name ?? rule.rule_code}</option>)}
              </select>
            </label>
          </div>

          {loading ? (
            <LoadingBlock />
          ) : versions.length === 0 ? (
            <EmptyState message="No rule versions found." />
          ) : (
            <RuleTable columns={['Version', 'Rule', 'Supersedes', 'Effective From', 'Effective To', 'Approval', 'Status', 'Open']}>
              {versions.map((rule) => (
                <tr key={rule.id} className="border-t border-border-light hover:bg-gray-50">
                  <td className="p-3 font-semibold text-text-primary">v{rule.version}</td>
                  <td className="p-3 text-text-secondary">{rule.rule_name ?? rule.rule_code}</td>
                  <td className="p-3 text-text-secondary">{rule.supersedes_rule_id ?? '-'}</td>
                  <td className="p-3 text-text-secondary">{formatDate(rule.effective_from)}</td>
                  <td className="p-3 text-text-secondary">{formatDate(rule.effective_to)}</td>
                  <td className="p-3"><RuleBadge value={rule.approval_status} /></td>
                  <td className="p-3"><RuleBadge value={rule.status} /></td>
                  <td className="p-3"><Link href={`/accounting/posting-rules/rules/${rule.id}`} className="text-accent-primary underline">Open</Link></td>
                </tr>
              ))}
            </RuleTable>
          )}
        </div>
      </RulePageFrame>
    </AppShell>
  );
}
