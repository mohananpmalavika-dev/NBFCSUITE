/**
 * Budget Management Component
 * Manage project budgets and expenses
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { budgetAPI, ProjectBudget } from '../../services/projectManagementService';
import './ProjectManagement.css';

const BudgetManagement: React.FC = () => {
  const navigate = useNavigate();
  const { projectId } = useParams<{ projectId?: string }>();
  const [budgets, setBudgets] = useState<ProjectBudget[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedBudget, setSelectedBudget] = useState<ProjectBudget | null>(null);

  useEffect(() => {
    loadBudgets();
  }, [projectId]);

  const loadBudgets = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await budgetAPI.list({
        project_id: projectId,
        page_size: 50,
      });

      setBudgets(response.items);
    } catch (err: any) {
      setError(err.message || 'Failed to load budgets');
    } finally {
      setLoading(false);
    }
  };

  const handleApproveBudget = async (budgetId: string) => {
    if (!confirm('Are you sure you want to approve this budget?')) return;

    try {
      await budgetAPI.approve(budgetId);
      await loadBudgets();
      alert('Budget approved successfully');
    } catch (err: any) {
      alert('Failed to approve budget');
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getStatusBadge = (status: string) => {
    const statusColors: Record<string, string> = {
      draft: 'badge-secondary',
      approved: 'badge-success',
      active: 'badge-primary',
      exceeded: 'badge-danger',
      closed: 'badge-secondary',
    };
    return statusColors[status] || 'badge-secondary';
  };

  const getVarianceColor = (variance: number) => {
    if (variance > 0) return 'positive';
    if (variance < 0) return 'negative';
    return '';
  };

  const calculateUtilization = (budget: ProjectBudget) => {
    const totalBudget = budget.approved_budget || budget.planned_budget;
    if (totalBudget === 0) return 0;
    return (budget.actual_cost / totalBudget) * 100;
  };

  if (loading) {
    return (
      <div className="pm-container">
        <div className="loading-spinner">Loading budgets...</div>
      </div>
    );
  }

  return (
    <div className="pm-container">
      {/* Header */}
      <div className="pm-header">
        <div>
          <h1>Budget Management</h1>
          <p className="text-muted">Track and manage project budgets and expenses</p>
        </div>
        <button className="btn btn-primary" onClick={() => navigate('/project-management/budgets/new')}>
          <i className="bi bi-plus-circle"></i> New Budget
        </button>
      </div>

      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}

      {/* Budgets List */}
      {budgets.length === 0 ? (
        <div className="card">
          <div className="card-body">
            <div className="empty-state">
              <i className="bi bi-cash-stack"></i>
              <p>No budgets found</p>
              <button className="btn btn-primary" onClick={() => navigate('/project-management/budgets/new')}>
                Create First Budget
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="budgets-grid">
          {budgets.map((budget) => {
            const utilization = calculateUtilization(budget);
            const isOverBudget = utilization > 100;
            const isNearLimit = utilization > budget.alert_threshold_percentage;

            return (
              <div key={budget.id} className="card budget-card">
                <div className="card-header">
                  <div>
                    <h5>{budget.budget_name}</h5>
                    <div className="text-muted small">{budget.project_name}</div>
                    <div className="text-muted small">FY: {budget.fiscal_year}</div>
                  </div>
                  <span className={`badge ${getStatusBadge(budget.status)}`}>
                    {budget.status.toUpperCase()}
                  </span>
                </div>

                <div className="card-body">
                  {/* Budget Alert */}
                  {isOverBudget && (
                    <div className="budget-alert alert-danger">
                      <i className="bi bi-exclamation-triangle"></i>
                      <span>Budget exceeded by {formatCurrency(Math.abs(budget.budget_variance))}</span>
                    </div>
                  )}
                  {!isOverBudget && isNearLimit && (
                    <div className="budget-alert alert-warning">
                      <i className="bi bi-exclamation-circle"></i>
                      <span>Budget utilization at {utilization.toFixed(1)}%</span>
                    </div>
                  )}

                  {/* Budget Summary */}
                  <div className="budget-summary-grid">
                    <div className="budget-item">
                      <div className="budget-item-label">Planned</div>
                      <div className="budget-item-value">{formatCurrency(budget.planned_budget)}</div>
                    </div>

                    <div className="budget-item">
                      <div className="budget-item-label">Approved</div>
                      <div className="budget-item-value">
                        {formatCurrency(budget.approved_budget || 0)}
                      </div>
                    </div>

                    <div className="budget-item">
                      <div className="budget-item-label">Spent</div>
                      <div className="budget-item-value">{formatCurrency(budget.actual_cost)}</div>
                    </div>

                    <div className="budget-item">
                      <div className="budget-item-label">Available</div>
                      <div className={`budget-item-value ${getVarianceColor(budget.available_budget)}`}>
                        {formatCurrency(budget.available_budget)}
                      </div>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="budget-progress-bar">
                    <div className="progress">
                      <div
                        className={`progress-bar ${isOverBudget ? 'bg-danger' : isNearLimit ? 'bg-warning' : 'bg-success'}`}
                        role="progressbar"
                        style={{ width: `${Math.min(utilization, 100)}%` }}
                        aria-valuenow={utilization}
                        aria-valuemin={0}
                        aria-valuemax={100}
                      ></div>
                    </div>
                    <div className="text-muted small mt-2">
                      Utilization: {utilization.toFixed(1)}% • Variance: {formatCurrency(budget.budget_variance)}
                    </div>
                  </div>

                  {/* Expense Categories */}
                  {budget.expense_lines && budget.expense_lines.length > 0 && (
                    <div className="mt-3">
                      <strong className="small">Top Expenses:</strong>
                      <div className="mt-2" style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                        {budget.expense_lines.slice(0, 3).map((line) => (
                          <span key={line.id} className="expense-category-badge">
                            {line.expense_category}: {formatCurrency(line.actual_amount)}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <div className="card-footer">
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button
                      className="btn btn-sm btn-outline-primary"
                      onClick={() => navigate(`/project-management/budgets/${budget.id}`)}
                    >
                      <i className="bi bi-eye"></i> View Details
                    </button>
                    {budget.status === 'draft' && (
                      <button
                        className="btn btn-sm btn-success"
                        onClick={() => handleApproveBudget(budget.id)}
                      >
                        <i className="bi bi-check-circle"></i> Approve
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default BudgetManagement;
