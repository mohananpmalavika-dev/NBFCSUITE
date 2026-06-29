"use client";

import { useEffect, useState } from 'react';
import { AppShell } from '../../../components/AppShell';
import { financeApi } from '../../eomApi';
import type { CostCenter, ProfitCenter } from '../../eomApi';
import { EmptyState, FinancePageFrame, LoadingBlock, StatusBadge } from '../financeComponents';

export default function FinanceExplorerPage() {
  const [costCenters, setCostCenters] = useState<CostCenter[]>([]);
  const [profitCenters, setProfitCenters] = useState<ProfitCenter[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        const [costBody, profitBody] = await Promise.all([
          financeApi.listCostCenters(),
          financeApi.listProfitCenters(),
        ]);
        if (!mounted) return;
        setCostCenters(costBody.items);
        setProfitCenters(profitBody.items);
      } catch {
        if (!mounted) return;
        setCostCenters([]);
        setProfitCenters([]);
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
        title="Financial Explorer"
        description="Trace enterprise financial accountability from organization nodes into cost and profit ownership."
      >
        {loading ? (
          <LoadingBlock />
        ) : costCenters.length + profitCenters.length === 0 ? (
          <EmptyState message="No financial hierarchy has been configured yet." />
        ) : (
          <div className="rounded-md border border-border-default bg-background-surface p-4">
            <div className="space-y-4">
              <div>
                <div className="text-sm font-semibold text-text-primary">Enterprise</div>
                <div className="mt-2 border-l border-border-default pl-4">
                  <div className="text-sm font-semibold text-text-secondary">Financial Organization</div>
                  <div className="mt-3 grid gap-3 lg:grid-cols-2">
                    <div className="space-y-2">
                      <div className="text-xs font-semibold uppercase tracking-[0.14em] text-text-muted">Cost Centers</div>
                      {costCenters.map((item) => (
                        <div key={item.id} className="rounded-md border border-border-light p-3">
                          <div className="flex items-center justify-between gap-3">
                            <div>
                              <div className="font-semibold">{item.name}</div>
                              <div className="text-sm text-text-secondary">{item.code} - {item.category ?? 'Unclassified'}</div>
                            </div>
                            <StatusBadge value={item.status} />
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="space-y-2">
                      <div className="text-xs font-semibold uppercase tracking-[0.14em] text-text-muted">Profit Centers</div>
                      {profitCenters.map((item) => (
                        <div key={item.id} className="rounded-md border border-border-light p-3">
                          <div className="flex items-center justify-between gap-3">
                            <div>
                              <div className="font-semibold">{item.name}</div>
                              <div className="text-sm text-text-secondary">{item.code} - {item.category ?? 'Unclassified'}</div>
                            </div>
                            <StatusBadge value={item.status} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </FinancePageFrame>
    </AppShell>
  );
}
