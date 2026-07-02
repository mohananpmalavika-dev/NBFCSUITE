"use client";

import { useEffect, useState } from 'react';
import { AppShell } from '../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../accountingApi';
import type {
  CloseDashboardResponse,
  CloseStartPayload,
  CloseTaskCreate,
  CloseTaskListResponse,
} from '../accountingApi';

export default function FinancialClosePage() {
  const [dashboard, setDashboard] = useState<CloseDashboardResponse | null>(null);
  const [tasks, setTasks] = useState<CloseTaskListResponse | null>(null);
  const [cycleId, setCycleId] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function refreshDashboard() {
    setLoading(true);
    setError('');
    try {
      const result = await accountingApi.getCloseDashboard(DEFAULT_ACCOUNTING_TENANT);
      setDashboard(result);
    } catch (err) {
      setError('Unable to load close dashboard. Confirm accounting backend connectivity.');
      setDashboard(null);
    } finally {
      setLoading(false);
    }
  }

  async function loadTasks() {
    if (!cycleId) {
      return;
    }
    setLoading(true);
    setError('');
    try {
      const result = await accountingApi.listCloseTasks(DEFAULT_ACCOUNTING_TENANT);
      setTasks(result);
    } catch (err) {
      setError('Unable to load close task list.');
      setTasks(null);
    } finally {
      setLoading(false);
    }
  }

  async function startCycle() {
    setLoading(true);
    setError('');
    try {
      const payload: CloseStartPayload = {
        tenant_id: DEFAULT_ACCOUNTING_TENANT,
        cycle_name: 'June Financial Close',
        period: '2026-06',
        initiated_by: 'finance-ops',
      };
      const response = await accountingApi.startCloseCycle(payload);
      setCycleId(response.id);
      await refreshDashboard();
    } catch {
      setError('Unable to start close cycle.');
    } finally {
      setLoading(false);
    }
  }

  async function createTask() {
    if (!cycleId) {
      setError('Start a close cycle first.');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const payload: CloseTaskCreate = {
        tenant_id: DEFAULT_ACCOUNTING_TENANT,
        cycle_id: cycleId,
        name: 'Reconcile cash and bank balances',
        owner: 'close-team',
        due_date: '2026-06-30',
        priority: 'high',
      };
      await accountingApi.createCloseTask(payload);
      await loadTasks();
    } catch {
      setError('Unable to create close task.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refreshDashboard();
  }, []);

  return (
    <AppShell>
      <div className="space-y-6 p-6">
        <div className="rounded-md border border-border-default bg-background-surface p-6">
          <div className="text-sm font-semibold uppercase tracking-wide text-accent-primary">Financial Close Platform</div>
          <h1 className="mt-2 text-2xl font-semibold text-text-primary">Close orchestration, consolidation and compliance</h1>
          <p className="mt-2 max-w-3xl text-sm text-text-secondary">
            Manage close cycles, coordinate reconciliation tasks, generate board packs and regulatory reports from a unified finance operations workspace.
          </p>
        </div>

        {error ? (
          <div className="rounded-md border border-border-default bg-danger-surface p-4 text-sm text-danger-foreground">{error}</div>
        ) : null}

        {loading ? (
          <div className="rounded-md border border-border-default bg-background-default p-4 text-sm text-text-secondary">
            Loading financial close data…
          </div>
        ) : null}

        <div className="grid gap-4 lg:grid-cols-3">
          <div className="rounded-md border border-border-default bg-background-surface p-4">
            <div className="text-sm font-semibold text-text-secondary">Close readiness</div>
            <div className="mt-3 text-3xl font-semibold text-text-primary">{dashboard?.close_readiness ?? '--'}%</div>
            <div className="mt-2 text-sm text-text-secondary">Open tasks: {dashboard?.open_tasks ?? 0}</div>
            <div className="text-sm text-text-secondary">Blocked tasks: {dashboard?.blocked_tasks ?? 0}</div>
          </div>
          <div className="rounded-md border border-border-default bg-background-surface p-4">
            <div className="text-sm font-semibold text-text-secondary">Consolidation progress</div>
            <div className="mt-3 text-3xl font-semibold text-text-primary">{dashboard?.consolidation_progress ?? '--'}%</div>
            <div className="mt-2 text-sm text-text-secondary">Board pack status: {dashboard?.board_pack_status ?? 'pending'}</div>
            <div className="text-sm text-text-secondary">Regulatory reporting: {dashboard?.rbi_status ?? 'pending'}</div>
          </div>
          <div className="rounded-md border border-border-default bg-background-default p-4 text-sm text-text-secondary">
            <div className="font-semibold text-text-primary">Tenant</div>
            <div className="mt-2">{DEFAULT_ACCOUNTING_TENANT}</div>
            <div className="mt-4 font-semibold text-text-primary">Current cycle</div>
            <div className="mt-2">{cycleId || 'None started'}</div>
          </div>
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          <button
            type="button"
            onClick={startCycle}
            className="rounded-md bg-accent-primary px-4 py-3 text-sm font-semibold text-white transition hover:bg-accent-primary/90"
          >
            Start Close Cycle
          </button>
          <button
            type="button"
            onClick={createTask}
            className="rounded-md border border-border-default bg-background-default px-4 py-3 text-sm font-semibold text-text-primary transition hover:border-accent-primary"
          >
            Create Reconciliation Task
          </button>
        </div>

        {tasks?.items.length ? (
          <div className="rounded-md border border-border-default bg-background-surface p-4">
            <div className="text-lg font-semibold text-text-primary">Open close tasks</div>
            <div className="mt-4 space-y-3">
              {tasks.items.map((task) => (
                <div key={task.id} className="rounded-md border border-border-light bg-background-default p-3">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <div className="font-semibold text-text-primary">{task.name}</div>
                      <div className="text-sm text-text-secondary">Owner: {task.owner ?? 'TBD'}</div>
                    </div>
                    <div className="text-sm font-semibold text-text-primary">{task.status}</div>
                  </div>
                  <div className="mt-2 text-xs text-text-secondary">Due: {task.due_date ?? 'n/a'}</div>
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </div>
    </AppShell>
  );
}
