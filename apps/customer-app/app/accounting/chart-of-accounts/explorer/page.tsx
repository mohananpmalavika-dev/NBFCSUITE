"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../../accountingApi';
import type { GLTreeNode } from '../../accountingApi';
import { CoaPageFrame, EmptyState, LoadingBlock, StatusBadge, formatAmount } from '../coaComponents';

function TreeRows({ nodes, level = 0 }: { nodes: GLTreeNode[]; level?: number }) {
  return (
    <>
      {nodes.map((node) => (
        <div key={node.id}>
          <div className="grid grid-cols-[minmax(260px,1fr)_120px_120px_120px_120px] items-center border-t border-border-light text-sm hover:bg-gray-50">
            <div className="p-3" style={{ paddingLeft: 12 + level * 24 }}>
              <Link href={`/accounting/chart-of-accounts/accounts/${node.id}`} className="font-semibold text-accent-primary underline">
                {node.account_code}
              </Link>
              <div className="text-text-secondary">{node.account_name}</div>
            </div>
            <div className="p-3 text-text-secondary">{node.account_type}</div>
            <div className="p-3 text-text-secondary">{node.currency ?? '-'}</div>
            <div className="p-3 text-text-secondary">{formatAmount(node.balance, node.currency ?? 'INR')}</div>
            <div className="p-3"><StatusBadge value={node.status} /></div>
          </div>
          {node.children.length > 0 ? <TreeRows nodes={node.children} level={level + 1} /> : null}
        </div>
      ))}
    </>
  );
}

export default function ChartExplorerPage() {
  const [items, setItems] = useState<GLTreeNode[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        const body = await accountingApi.getTree(DEFAULT_ACCOUNTING_TENANT);
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
      <CoaPageFrame
        title="Chart Explorer"
        description="Review the GL hierarchy from control accounts into posting accounts, with balance and status context."
      >
        {loading ? (
          <LoadingBlock />
        ) : items.length === 0 ? (
          <EmptyState message="No chart hierarchy found." actionHref="/accounting/chart-of-accounts/directory" />
        ) : (
          <div className="overflow-x-auto rounded-md border border-border-default bg-background-surface">
            <div className="min-w-[760px]">
              <div className="grid grid-cols-[minmax(260px,1fr)_120px_120px_120px_120px] bg-gray-50 text-sm font-semibold text-text-secondary">
                <div className="p-3">Account</div>
                <div className="p-3">Type</div>
                <div className="p-3">Currency</div>
                <div className="p-3">Balance</div>
                <div className="p-3">Status</div>
              </div>
              <TreeRows nodes={items} />
            </div>
          </div>
        )}
      </CoaPageFrame>
    </AppShell>
  );
}
