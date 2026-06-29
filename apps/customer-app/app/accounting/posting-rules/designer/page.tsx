"use client";

import { useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../../accountingApi';
import type { PostingRulePayload } from '../../accountingApi';
import { RulePageFrame } from '../ruleComponents';

const initialForm = {
  source_module: 'loans',
  source_event: 'disbursement',
  rule_name: 'Gold loan disbursement posting',
  priority: '10',
  product: 'Gold Loan',
  status: 'draft',
  condition_field: 'product',
  condition_operator: 'eq',
  condition_value: 'gold_loan',
  debit_account_code: '1200_LOAN_RECEIVABLE',
  debit_formula: 'amount',
  credit_account_code: '1000_CASH',
  credit_formula: 'amount',
};

export default function RuleDesignerPage() {
  const [form, setForm] = useState(initialForm);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [createdId, setCreatedId] = useState<string | null>(null);

  function update(field: keyof typeof initialForm, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function submit() {
    setSaving(true);
    setMessage(null);
    try {
      const payload: PostingRulePayload = {
        tenant_id: DEFAULT_ACCOUNTING_TENANT,
        source_module: form.source_module.trim(),
        source_event: form.source_event.trim(),
        rule_name: form.rule_name.trim(),
        priority: Number(form.priority || 100),
        status: form.status,
        requires_approval: 'true',
        description: `${form.rule_name.trim()} created from PRE designer`,
        conditions: form.condition_field.trim()
          ? [{ field: form.condition_field.trim(), operator: form.condition_operator, value: form.condition_value }]
          : [],
        lines: [
          {
            account_code: form.debit_account_code.trim(),
            direction: 'debit',
            formula: form.debit_formula.trim() || 'amount',
            description: 'Debit entry',
            sequence: 1,
            dimension_source: { branch_id: 'branch_id', cost_center: 'cost_center', product_id: 'product_id' },
          },
          {
            account_code: form.credit_account_code.trim(),
            direction: 'credit',
            formula: form.credit_formula.trim() || 'amount',
            description: 'Credit entry',
            sequence: 2,
            dimension_source: { branch_id: 'branch_id', cost_center: 'cost_center', product_id: 'product_id' },
          },
        ],
        created_by: 'rule-console',
        metadata: {
          rule_code: `${form.source_module}.${form.source_event}.${form.product}`.replace(/\s+/g, '_').toLowerCase(),
          product: form.product,
          dimensions: { branch: true, cost_center: true, product: true, customer: true },
          validation_rules: ['debits_equal_credits', 'currency_exists', 'gl_active', 'period_open', 'dimensions_complete'],
        },
      };
      const created = await accountingApi.createPostingRule(payload);
      setCreatedId(created.id);
      setMessage(`Created ${created.rule_name ?? created.rule_code}`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Create failed');
    } finally {
      setSaving(false);
    }
  }

  return (
    <AppShell>
      <RulePageFrame title="Rule Designer" description="Build posting rule headers, conditions, debit lines, credit lines, amount expressions, dimensions, validation rules, workflow, and review state.">
        <div className="space-y-4">
          <div className="rounded-md border border-border-default bg-background-surface p-4">
            <div className="grid gap-3 md:grid-cols-3">
              <label className="block space-y-1">
                <span className="text-sm font-semibold text-text-secondary">Source Module</span>
                <input className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={form.source_module} onChange={(event) => update('source_module', event.target.value)} />
              </label>
              <label className="block space-y-1">
                <span className="text-sm font-semibold text-text-secondary">Accounting Event</span>
                <input className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={form.source_event} onChange={(event) => update('source_event', event.target.value)} />
              </label>
              <label className="block space-y-1">
                <span className="text-sm font-semibold text-text-secondary">Priority</span>
                <input className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={form.priority} onChange={(event) => update('priority', event.target.value)} />
              </label>
              <label className="block space-y-1 md:col-span-2">
                <span className="text-sm font-semibold text-text-secondary">Rule Name</span>
                <input className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={form.rule_name} onChange={(event) => update('rule_name', event.target.value)} />
              </label>
              <label className="block space-y-1">
                <span className="text-sm font-semibold text-text-secondary">Product</span>
                <input className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={form.product} onChange={(event) => update('product', event.target.value)} />
              </label>
            </div>
          </div>

          <div className="rounded-md border border-border-default bg-background-surface p-4">
            <div className="mb-3 text-sm font-semibold text-text-primary">Conditions</div>
            <div className="grid gap-3 md:grid-cols-3">
              <input className="h-10 rounded-md border border-border-default px-3 text-sm" value={form.condition_field} onChange={(event) => update('condition_field', event.target.value)} placeholder="Field" />
              <select className="h-10 rounded-md border border-border-default px-3 text-sm" value={form.condition_operator} onChange={(event) => update('condition_operator', event.target.value)}>
                <option value="eq">eq</option>
                <option value="gt">gt</option>
                <option value="lt">lt</option>
                <option value="in">in</option>
                <option value="contains">contains</option>
              </select>
              <input className="h-10 rounded-md border border-border-default px-3 text-sm" value={form.condition_value} onChange={(event) => update('condition_value', event.target.value)} placeholder="Value" />
            </div>
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="mb-3 text-sm font-semibold text-text-primary">Debit Builder</div>
              <div className="grid gap-3">
                <input className="h-10 rounded-md border border-border-default px-3 text-sm" value={form.debit_account_code} onChange={(event) => update('debit_account_code', event.target.value)} placeholder="GL Account" />
                <input className="h-10 rounded-md border border-border-default px-3 text-sm" value={form.debit_formula} onChange={(event) => update('debit_formula', event.target.value)} placeholder="Amount formula" />
              </div>
            </div>
            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="mb-3 text-sm font-semibold text-text-primary">Credit Builder</div>
              <div className="grid gap-3">
                <input className="h-10 rounded-md border border-border-default px-3 text-sm" value={form.credit_account_code} onChange={(event) => update('credit_account_code', event.target.value)} placeholder="GL Account" />
                <input className="h-10 rounded-md border border-border-default px-3 text-sm" value={form.credit_formula} onChange={(event) => update('credit_formula', event.target.value)} placeholder="Amount formula" />
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between rounded-md border border-border-default bg-background-surface p-4">
            <div className="text-sm text-text-secondary">Workflow: Finance Officer to Finance Manager to Controller to CFO to Publish</div>
            <button type="button" onClick={submit} disabled={saving || !form.source_module || !form.source_event || !form.debit_account_code || !form.credit_account_code} className="h-10 rounded-md bg-accent-primary px-3 text-sm font-semibold text-accent-onPrimary disabled:opacity-60">
              {saving ? 'Saving...' : 'Create Rule'}
            </button>
          </div>

          {message ? (
            <div className="rounded-md border border-border-default bg-background-surface p-3 text-sm text-text-secondary">
              {message}
              {createdId ? <Link href={`/accounting/posting-rules/rules/${createdId}`} className="ml-2 font-semibold text-accent-primary underline">Open 360</Link> : null}
            </div>
          ) : null}
        </div>
      </RulePageFrame>
    </AppShell>
  );
}
