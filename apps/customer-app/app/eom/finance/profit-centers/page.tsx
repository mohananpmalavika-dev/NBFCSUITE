"use client";

import { useEffect, useState } from 'react';
import { AppShell } from '../../../components/AppShell';
import { financeApi } from '../../eomApi';
import type { ProfitCenter } from '../../eomApi';
import { EmptyState, FinancePageFrame, FinanceTable, LoadingBlock, StatusBadge } from '../financeComponents';

export default function ProfitCentersPage() {
  const [items, setItems] = useState<ProfitCenter[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        const body = await financeApi.listProfitCenters();
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
        title="Profit Centers"
        description="Track profitability responsibility across products, branches, and revenue-owning businesses."
      >
        {loading ? (
          <LoadingBlock />
        ) : items.length === 0 ? (
          <EmptyState message="No profit centers found." />
        ) : (
          <FinanceTable columns={['Code', 'Name', 'Category', 'Owner', 'Branch', 'Currency', 'Status']}>
            {items.map((item) => (
              <tr key={item.id} className="border-t border-border-light hover:bg-gray-50">
                <td className="p-3 font-semibold">{item.code}</td>
                <td className="p-3">{item.name}</td>
                <td className="p-3 text-text-secondary">{item.category ?? '-'}</td>
                <td className="p-3 text-text-secondary">{item.responsibility_owner ?? '-'}</td>
                <td className="p-3 text-text-secondary">{item.branch_id ?? '-'}</td>
                <td className="p-3 text-text-secondary">{item.currency ?? '-'}</td>
                <td className="p-3"><StatusBadge value={item.status} /></td>
              </tr>
            ))}
          </FinanceTable>
        )}
      </FinancePageFrame>
    </AppShell>
  );
}
