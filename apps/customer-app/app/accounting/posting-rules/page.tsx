"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../accountingApi';
import type { PostingRule, PostingRuleDashboard } from '../accountingApi';
import { EmptyState, LoadingBlock, RuleBadge, RuleMetric, RulePageFrame, RuleTable, formatDate } from './ruleComponents';

export default function PostingRulesDashboardPage() {
  const [dashboard, setDashboard] = useState<PostingRuleDashboard | null>(null);
  const [rules, setRules] = useState<PostingRule[]>([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const [dashboardBody, rulesBody] = await Promise.all([
        accountingApi.getPostingRuleDashboard(DEFAULT_ACCOUNTING_TENANT),
        accountingApi.listPostingRules(DEFAULT_ACCOUNTING_TENANT, 'limit=8'),
      ]);
      setDashboard(dashboardBody);
      setRules(rulesBody.items);
    } catch {
      setDashboard(null);
      setRules([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <AppShell>
      <RulePageFrame
        title="Posting Rule Engine"
        description="Configure how accounting events become balanced debit and credit journal entries without hardcoding business logic."
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
              <RuleMetric label="Posting Rules" value={dashboard.kpis.posting_rules} note="Configured accounting policies" />
              <RuleMetric label="Active Rules" value={dashboard.kpis.active_rules} note="Published and available" />
              <RuleMetric label="Rule Coverage" value={`${dashboard.kpis.rule_coverage}%`} note="Events covered by rules" />
              <RuleMetric label="Rule Health" value={`${dashboard.kpis.rule_health}%`} note={dashboard.summary.status} />
            </div>

            <div className="grid gap-3 md:grid-cols-4">
              <RuleMetric label="Draft Rules" value={dashboard.kpis.draft_rules} note="Pending workflow" />
              <RuleMetric label="Failed Runs" value={dashboard.kpis.failed_rules} note="Execution exceptions" />
              <RuleMetric label="Avg Time" value={`${dashboard.kpis.average_execution_time_ms}ms`} note="Execution latency" />
              <RuleMetric label="Unused Rules" value={dashboard.kpis.unused_rules} note="No execution logs" />
            </div>

            <RuleTable columns={['Rule Code', 'Rule Name', 'Event', 'Product', 'Version', 'Priority', 'Effective', 'Status']}>
              {rules.map((rule) => (
                <tr key={rule.id} className="border-t border-border-light hover:bg-gray-50">
                  <td className="p-3 font-semibold"><Link href={`/accounting/posting-rules/rules/${rule.id}`} className="text-accent-primary underline">{rule.rule_code}</Link></td>
                  <td className="p-3 text-text-secondary">{rule.rule_name ?? '-'}</td>
                  <td className="p-3 text-text-secondary">{rule.source_module}.{rule.source_event}</td>
                  <td className="p-3 text-text-secondary">{rule.product ?? 'Enterprise Default'}</td>
                  <td className="p-3 text-text-secondary">v{rule.version}</td>
                  <td className="p-3 text-text-secondary">{rule.priority}</td>
                  <td className="p-3 text-text-secondary">{formatDate(rule.effective_from)}</td>
                  <td className="p-3"><RuleBadge value={rule.status} /></td>
                </tr>
              ))}
              {rules.length === 0 ? (
                <tr>
                  <td colSpan={8} className="p-6 text-center text-text-secondary">No posting rules found.</td>
                </tr>
              ) : null}
            </RuleTable>
          </div>
        ) : (
          <EmptyState message="Posting Rule Engine API is unavailable. Check that the accounting service is running." />
        )}
      </RulePageFrame>
    </AppShell>
  );
}
