"use client";

import { useEffect, useState } from 'react';
import { AppShell } from '../../../components/AppShell';
import { financeApi } from '../../eomApi';
import type { InternalOrder } from '../../eomApi';
import { EmptyState, FinancePageFrame, FinanceTable, LoadingBlock, StatusBadge } from '../financeComponents';

export default function InternalOrdersPage() {
  const [items, setItems] = useState<InternalOrder[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        const body = await financeApi.listInternalOrders();
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
        title="Internal Orders"
        description="Track temporary financial work from draft through approval, active execution, closure, and archive."
      >
        {loading ? (
          <LoadingBlock />
        ) : items.length === 0 ? (
          <EmptyState message="No internal orders found." />
        ) : (
          <FinanceTable columns={['Code', 'Name', 'Cost Center', 'Profit Center', 'Budget Center', 'Status']}>
            {items.map((item) => (
              <tr key={item.id} className="border-t border-border-light hover:bg-gray-50">
                <td className="p-3 font-semibold">{item.code}</td>
                <td className="p-3">{item.name}</td>
                <td className="p-3 text-text-secondary">{item.cost_center_id ?? '-'}</td>
                <td className="p-3 text-text-secondary">{item.profit_center_id ?? '-'}</td>
                <td className="p-3 text-text-secondary">{item.budget_center_id ?? '-'}</td>
                <td className="p-3"><StatusBadge value={item.status} /></td>
              </tr>
            ))}
          </FinanceTable>
        )}
      </FinancePageFrame>
    </AppShell>
  );
}
