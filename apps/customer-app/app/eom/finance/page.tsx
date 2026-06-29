"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../components/AppShell';
import { financeApi } from '../eomApi';
import type { Budget, CostCenter, FinanceDashboard, InternalOrder, ProfitCenter } from '../eomApi';
import { EmptyState, FinancePageFrame, FinanceTable, LoadingBlock, MetricTile, StatusBadge, formatMoney } from './financeComponents';

export default function FinanceDashboardPage() {
  const [dashboard, setDashboard] = useState<FinanceDashboard | null>(null);
  const [costCenters, setCostCenters] = useState<CostCenter[]>([]);
  const [profitCenters, setProfitCenters] = useState<ProfitCenter[]>([]);
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [orders, setOrders] = useState<InternalOrder[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        const [dashboardBody, costBody, profitBody, budgetBody, orderBody] = await Promise.all([
          financeApi.getDashboard(),
          financeApi.listCostCenters(),
          financeApi.listProfitCenters(),
          financeApi.listBudgets(),
          financeApi.listInternalOrders(),
        ]);
        if (!mounted) return;
        setDashboard(dashboardBody);
        setCostCenters(costBody.items);
        setProfitCenters(profitBody.items);
        setBudgets(budgetBody.items);
        setOrders(orderBody.items);
      } catch {
        if (mounted) setDashboard(null);
      } finally {
        if (mounted) setLoading(false);
      }
    }
    load();
    return () => {
      mounted = false;
    };
  }, []);

  const budgetTotal = budgets.reduce((sum, budget) => sum + (budget.revised_total ?? budget.original_total ?? 0), 0);
  const actualTotal = budgets.reduce((sum, budget) => sum + (budget.actual_total ?? 0), 0);
  const forecastTotal = budgets.reduce((sum, budget) => sum + (budget.forecast_total ?? 0), 0);
  const ownershipRows = [
    ...costCenters.slice(0, 4).map((item) => ({
      id: item.id,
      objectType: 'Cost Center',
      code: item.code,
      owner: item.budget_owner ?? '-',
      status: item.status,
      href: '/eom/finance/cost-centers',
    })),
    ...profitCenters.slice(0, 4).map((item) => ({
      id: item.id,
      objectType: 'Profit Center',
      code: item.code,
      owner: item.responsibility_owner ?? '-',
      status: item.status,
      href: '/eom/finance/profit-centers',
    })),
  ];

  return (
    <AppShell>
      <FinancePageFrame
        title="Finance Dashboard"
        description="Monitor ownership, budgets, internal orders, and the setup health of the enterprise financial organization."
      >
        {loading ? (
          <LoadingBlock />
        ) : dashboard ? (
          <div className="space-y-6">
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
              <MetricTile label="Cost Centers" value={dashboard.kpis.cost_centers} note="Expense ownership nodes" />
              <MetricTile label="Profit Centers" value={dashboard.kpis.profit_centers} note="Profitability nodes" />
              <MetricTile label="Budgets" value={dashboard.kpis.budgets} note="Active budget controls" />
              <MetricTile label="Health Score" value={`${dashboard.kpis.health_score}%`} note={dashboard.kpis.health_rating || dashboard.summary.status} />
            </div>

            <div className="grid gap-3 md:grid-cols-3">
              <MetricTile label="Budget Baseline" value={formatMoney(budgetTotal)} note="Original or revised allocation" />
              <MetricTile label="Actual Spend" value={formatMoney(actualTotal)} note="Recorded actual total" />
              <MetricTile label="Forecast" value={formatMoney(forecastTotal)} note="Projected full-year amount" />
            </div>

            <FinanceTable columns={['Object', 'Code', 'Owner', 'Status', 'Open']}>
              {ownershipRows.map((item) => (
                <tr key={item.id} className="border-t border-border-light hover:bg-gray-50">
                  <td className="p-3 font-medium">{item.objectType}</td>
                  <td className="p-3">{item.code}</td>
                  <td className="p-3 text-text-secondary">{item.owner}</td>
                  <td className="p-3"><StatusBadge value={item.status} /></td>
                  <td className="p-3">
                    <Link className="font-semibold text-accent-primary underline" href={item.href}>
                      View register
                    </Link>
                  </td>
                </tr>
              ))}
              {ownershipRows.length === 0 ? (
                <tr>
                  <td colSpan={5} className="p-6 text-center text-text-secondary">No financial organization objects found.</td>
                </tr>
              ) : null}
            </FinanceTable>

            <FinanceTable columns={['Internal Order', 'Name', 'Status', 'Linked Cost Center']}>
              {orders.slice(0, 6).map((order) => (
                <tr key={order.id} className="border-t border-border-light hover:bg-gray-50">
                  <td className="p-3 font-medium">{order.code}</td>
                  <td className="p-3">{order.name}</td>
                  <td className="p-3"><StatusBadge value={order.status} /></td>
                  <td className="p-3 text-text-secondary">{order.cost_center_id ?? '-'}</td>
                </tr>
              ))}
              {orders.length === 0 ? (
                <tr>
                  <td colSpan={4} className="p-6 text-center text-text-secondary">No internal orders found.</td>
                </tr>
              ) : null}
            </FinanceTable>
          </div>
        ) : (
          <EmptyState message="Finance dashboard is unavailable. Check that the EOM API is running on the configured URL." />
        )}
      </FinancePageFrame>
    </AppShell>
  );
}
