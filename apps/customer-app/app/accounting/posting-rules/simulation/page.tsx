"use client";

import { useEffect, useState } from 'react';
import { AppShell } from '../../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../../accountingApi';
import type { PostingRule, PostingRuleSimulationResponse } from '../../accountingApi';
import { EmptyState, LoadingBlock, RuleBadge, RulePageFrame, RuleTable } from '../ruleComponents';

export default function RuleSimulationPage() {
  const [rules, setRules] = useState<PostingRule[]>([]);
  const [ruleId, setRuleId] = useState('');
  const [amount, setAmount] = useState('1000000');
  const [eventData, setEventData] = useState('{"amount":1000000,"product":"gold_loan","branch_id":"branch-001","cost_center":"cc-001","product_id":"gold-loan"}');
  const [result, setResult] = useState<PostingRuleSimulationResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    try {
      const body = await accountingApi.listPostingRules(DEFAULT_ACCOUNTING_TENANT, 'limit=100');
      setRules(body.items);
      setRuleId((current) => current || body.items[0]?.id || '');
    } catch {
      setRules([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function simulate() {
    if (!ruleId) return;
    setRunning(true);
    setMessage(null);
    try {
      const parsed = JSON.parse(eventData || '{}') as Record<string, unknown>;
      const response = await accountingApi.simulatePostingRule(ruleId, DEFAULT_ACCOUNTING_TENANT, {
        amount: Number(amount || 0),
        source_reference: 'PRE-SIM-UI',
        currency: 'INR',
        branch_id: String(parsed.branch_id ?? ''),
        event_data: parsed,
      });
      setResult(response);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Simulation failed');
      setResult(null);
    } finally {
      setRunning(false);
    }
  }

  return (
    <AppShell>
      <RulePageFrame title="Rule Simulation Lab" description="Run single transaction simulations, validate debit and credit impact, and compare generated journal lines before publishing.">
        {loading ? (
          <LoadingBlock />
        ) : rules.length === 0 ? (
          <EmptyState message="No posting rules are available for simulation." />
        ) : (
          <div className="space-y-4">
            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="grid gap-3 md:grid-cols-[minmax(260px,1fr)_180px]">
                <label className="block space-y-1">
                  <span className="text-sm font-semibold text-text-secondary">Rule</span>
                  <select className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={ruleId} onChange={(event) => setRuleId(event.target.value)}>
                    {rules.map((rule) => <option key={rule.id} value={rule.id}>{rule.rule_name ?? rule.rule_code}</option>)}
                  </select>
                </label>
                <label className="block space-y-1">
                  <span className="text-sm font-semibold text-text-secondary">Amount</span>
                  <input className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={amount} onChange={(event) => setAmount(event.target.value)} />
                </label>
              </div>
              <label className="mt-3 block space-y-1">
                <span className="text-sm font-semibold text-text-secondary">Event Data JSON</span>
                <textarea className="min-h-[120px] w-full rounded-md border border-border-default p-3 font-mono text-xs" value={eventData} onChange={(event) => setEventData(event.target.value)} />
              </label>
              <div className="mt-4 flex justify-end">
                <button type="button" onClick={simulate} disabled={running || !ruleId} className="h-10 rounded-md bg-accent-primary px-3 text-sm font-semibold text-accent-onPrimary disabled:opacity-60">
                  {running ? 'Running...' : 'Run Simulation'}
                </button>
              </div>
            </div>

            {message ? <div className="rounded-md border border-border-default bg-background-surface p-3 text-sm text-text-secondary">{message}</div> : null}

            {result ? (
              <div className="space-y-4">
                <div className="grid gap-3 md:grid-cols-4">
                  <div className="rounded-md border border-border-default bg-background-surface p-4"><div className="text-sm text-text-secondary">Balanced</div><div className="mt-1"><RuleBadge value={result.is_balanced ? 'active' : 'failed'} /></div></div>
                  <div className="rounded-md border border-border-default bg-background-surface p-4"><div className="text-sm text-text-secondary">Total Debit</div><div className="mt-1 font-semibold">{result.total_debit}</div></div>
                  <div className="rounded-md border border-border-default bg-background-surface p-4"><div className="text-sm text-text-secondary">Total Credit</div><div className="mt-1 font-semibold">{result.total_credit}</div></div>
                  <div className="rounded-md border border-border-default bg-background-surface p-4"><div className="text-sm text-text-secondary">Risk</div><div className="mt-1 font-semibold">{String(result.ai?.risk ?? 'low')}</div></div>
                </div>
                <RuleTable columns={['Account', 'Name', 'Direction', 'Debit', 'Credit', 'Currency', 'Description']}>
                  {result.lines.map((line, index) => (
                    <tr key={`${line.account_code}-${index}`} className="border-t border-border-light">
                      <td className="p-3 font-semibold text-text-primary">{String(line.account_code ?? '-')}</td>
                      <td className="p-3 text-text-secondary">{String(line.account_name ?? '-')}</td>
                      <td className="p-3 text-text-secondary">{String(line.direction ?? '-')}</td>
                      <td className="p-3 text-text-secondary">{String(line.debit ?? 0)}</td>
                      <td className="p-3 text-text-secondary">{String(line.credit ?? 0)}</td>
                      <td className="p-3 text-text-secondary">{String(line.currency ?? '-')}</td>
                      <td className="p-3 text-text-secondary">{String(line.description ?? '-')}</td>
                    </tr>
                  ))}
                </RuleTable>
              </div>
            ) : null}
          </div>
        )}
      </RulePageFrame>
    </AppShell>
  );
}
