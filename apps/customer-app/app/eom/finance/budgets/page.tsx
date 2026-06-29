"use client";

import { useEffect, useState } from 'react';
import { AppShell } from '../../../components/AppShell';
import { financeApi } from '../../eomApi';
import type { Budget } from '../../eomApi';
import { EmptyState, FinancePageFrame, FinanceTable, LoadingBlock, StatusBadge, formatMoney } from '../financeComponents';

export default function BudgetsPage() {
  const [items, setItems] = useState<Budget[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        const body = await financeApi.listBudgets();
        if (mounted) setItems(body.items);
      } catch {
        if (mounted) setItems([]);
      } finally {
        if (mounted) setLoading(false);
      }
    }
    load();
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <AppShell>
      <FinancePageFrame
        title="Budgets"
        description="Review original, revised, committed, actual, and forecast amounts by financial ownership node."
      >
        {loading ? (
          <LoadingBlock />
        ) : items.length === 0 ? (
          <EmptyState message="No budgets found." />
        ) : (
          <FinanceTable columns={['Year', 'Center', 'Original', 'Revised', 'Committed', 'Actual', 'Forecast', 'Status']}>
            {items.map((item) => {
              const currency = item.currency ?? 'INR';
              return (
                <tr key={item.id} className="border-t border-border-light hover:bg-gray-50">
                  <td className="p-3 font-semibold">{item.year}</td>
                  <td className="p-3 text-text-secondary">{item.cost_center_id ?? item.profit_center_id ?? item.budget_center_id ?? '-'}</td>
                  <td className="p-3">{formatMoney(item.original_total, currency)}</td>
                  <td className="p-3">{formatMoney(item.revised_total, currency)}</td>
                  <td className="p-3">{formatMoney(item.committed_total, currency)}</td>
                  <td className="p-3">{formatMoney(item.actual_total, currency)}</td>
                  <td className="p-3">{formatMoney(item.forecast_total, currency)}</td>
                  <td className="p-3"><StatusBadge value={item.status} /></td>
                </tr>
              );
            })}
          </FinanceTable>
        )}
      </FinancePageFrame>
    </AppShell>
  );
}
