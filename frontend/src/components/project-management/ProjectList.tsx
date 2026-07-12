/**
 * Project List Component
 * Displays list of projects with filtering and search
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { projectAPI, Project, ProjectStats } from '../../services/projectManagementService';
import './ProjectManagement.css';

const ProjectList: React.FC = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [stats, setStats] = useState<ProjectStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string[]>([]);
  const [priorityFilter, setPriorityFilter] = useState<string[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    loadData();
  }, [page, search, statusFilter, priorityFilter]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load stats
      const statsData = await projectAPI.getStats();
      setStats(statsData);

      // Load projects
      const response = await projectAPI.list({
        page,
        page_size: 20,
        search: search || undefined,
        status: statusFilter.length > 0 ? statusFilter : undefined,
        priority: priorityFilter.length > 0 ? priorityFilter : undefined,
      });

      setProjects(response.items);
      setTotalPages(response.total_pages);
    } catch (err: any) {
      setError(err.message || 'Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusFilterChange = (status: string) => {
    setStatusFilter((prev) =>
      prev.includes(status) ? prev.filter((s) => s !== status) : [...prev, status]
    );
    setPage(1);
  };

  const handlePriorityFilterChange = (priority: string) => {
    setPriorityFilter((prev) =>
      prev.includes(priority) ? prev.filter((p) => p !== priority) : [...prev, priority]
    );
    setPage(1);
  };

  const getStatusBadge = (status: string) => {
    const statusColors: Record<string, string> = {
      planning: 'badge-info',
      in_progress: 'badge-primary',
      on_hold: 'badge-warning',
      completed: 'badge-success',
      cancelled: 'badge-danger',
      archived: 'badge-secondary',
    };
    return statusColors[status] || 'badge-secondary';
  };

  const getPriorityBadge = (priority: string) => {
    const priorityColors: Record<string, string> = {
      low: 'badge-secondary',
      medium: 'badge-info',
      high: 'badge-warning',
      critical: 'badge-danger',
    };
    return priorityColors[priority] || 'badge-secondary';
  };

  const getHealthBadge = (health: string) => {
    const healthColors: Record<string, string> = {
      green: 'badge-success',
      amber: 'badge-warning',
      red: 'badge-danger',
    };
    return healthColors[health] || 'badge-secondary';
  };

  const formatCurrency = (amount: number | undefined) => {
    if (!amount) return '-';
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="pm-container">
        <div className="loading-spinner">Loading projects...</div>
      </div>
    );
  }

  return (
    <div className="pm-container">
      {/* Header */}
      <div className="pm-header">
        <div>
          <h1>Project Management</h1>
          <p className="text-muted">Manage projects, tasks, time tracking, and budgets</p>
        </div>
        <button className="btn btn-primary" onClick={() => navigate('/project-management/projects/new')}>
          <i className="bi bi-plus-circle"></i> New Project
        </button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon bg-primary">
              <i className="bi bi-folder"></i>
            </div>
            <div className="stat-content">
              <div className="stat-value">{stats.total_projects}</div>
              <div className="stat-label">Total Projects</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon bg-success">
              <i className="bi bi-play-circle"></i>
            </div>
            <div className="stat-content">
              <div className="stat-value">{stats.active_projects}</div>
              <div className="stat-label">Active Projects</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon bg-info">
              <i className="bi bi-check-circle"></i>
            </div>
            <div className="stat-content">
              <div className="stat-value">{stats.completed_projects}</div>
              <div className="stat-label">Completed</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon bg-warning">
              <i className="bi bi-currency-rupee"></i>
            </div>
            <div className="stat-content">
              <div className="stat-value">{formatCurrency(stats.total_budget)}</div>
              <div className="stat-label">Total Budget</div>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}

      {/* Filters */}
      <div className="filters-section">
        <div className="search-box">
          <i className="bi bi-search"></i>
          <input
            type="text"
            placeholder="Search projects..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
          />
        </div>

        <div className="filter-group">
          <label>Status:</label>
          <div className="checkbox-group">
            {['planning', 'in_progress', 'on_hold', 'completed'].map((status) => (
              <label key={status} className="checkbox-label">
                <input
                  type="checkbox"
                  checked={statusFilter.includes(status)}
                  onChange={() => handleStatusFilterChange(status)}
                />
                {status.replace('_', ' ').toUpperCase()}
              </label>
            ))}
          </div>
        </div>

        <div className="filter-group">
          <label>Priority:</label>
          <div className="checkbox-group">
            {['low', 'medium', 'high', 'critical'].map((priority) => (
              <label key={priority} className="checkbox-label">
                <input
                  type="checkbox"
                  checked={priorityFilter.includes(priority)}
                  onChange={() => handlePriorityFilterChange(priority)}
                />
                {priority.toUpperCase()}
              </label>
            ))}
          </div>
        </div>
      </div>

      {/* Projects Table */}
      <div className="card">
        <div className="card-header">
          <h5>Projects</h5>
        </div>
        <div className="card-body p-0">
          {projects.length === 0 ? (
            <div className="empty-state">
              <i className="bi bi-folder-x"></i>
              <p>No projects found</p>
              <button className="btn btn-primary" onClick={() => navigate('/project-management/projects/new')}>
                Create First Project
              </button>
            </div>
          ) : (
            <div className="table-responsive">
              <table className="table table-hover">
                <thead>
                  <tr>
                    <th>Code</th>
                    <th>Project Name</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Priority</th>
                    <th>Health</th>
                    <th>Manager</th>
                    <th>Progress</th>
                    <th>Budget</th>
                    <th>Timeline</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {projects.map((project) => (
                    <tr key={project.id} onClick={() => navigate(`/project-management/projects/${project.id}`)} style={{ cursor: 'pointer' }}>
                      <td>
                        <strong>{project.project_code}</strong>
                      </td>
                      <td>
                        <div>
                          <strong>{project.project_name}</strong>
                          {project.client_name && (
                            <div className="text-muted small">Client: {project.client_name}</div>
                          )}
                        </div>
                      </td>
                      <td>
                        <span className="badge badge-light">
                          {project.project_type.replace('_', ' ').toUpperCase()}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${getStatusBadge(project.status)}`}>
                          {project.status.replace('_', ' ').toUpperCase()}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${getPriorityBadge(project.project_priority)}`}>
                          {project.project_priority.toUpperCase()}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${getHealthBadge(project.health_status)}`}>
                          {project.health_status.toUpperCase()}
                        </span>
                      </td>
                      <td>
                        {project.project_manager_name || <span className="text-muted">-</span>}
                      </td>
                      <td>
                        <div className="progress-container">
                          <div className="progress">
                            <div
                              className="progress-bar"
                              role="progressbar"
                              style={{ width: `${project.progress_percentage}%` }}
                              aria-valuenow={project.progress_percentage}
                              aria-valuemin={0}
                              aria-valuemax={100}
                            ></div>
                          </div>
                          <span className="progress-text">{project.progress_percentage}%</span>
                        </div>
                      </td>
                      <td>
                        <div>
                          <small className="text-muted">Budget:</small> {formatCurrency(project.approved_budget)}
                        </div>
                        <div>
                          <small className="text-muted">Spent:</small> {formatCurrency(project.actual_cost)}
                        </div>
                      </td>
                      <td>
                        <div>
                          <small className="text-muted">Start:</small> {new Date(project.planned_start_date).toLocaleDateString()}
                        </div>
                        <div>
                          <small className="text-muted">End:</small> {new Date(project.planned_end_date).toLocaleDateString()}
                        </div>
                      </td>
                      <td>
                        <button
                          className="btn btn-sm btn-outline-primary"
                          onClick={(e) => {
                            e.stopPropagation();
                            navigate(`/project-management/projects/${project.id}`);
                          }}
                        >
                          <i className="bi bi-eye"></i>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="card-footer">
            <div className="pagination">
              <button
                className="btn btn-sm btn-outline-primary"
                disabled={page === 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
              >
                <i className="bi bi-chevron-left"></i> Previous
              </button>
              <span className="pagination-info">
                Page {page} of {totalPages}
              </span>
              <button
                className="btn btn-sm btn-outline-primary"
                disabled={page === totalPages}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              >
                Next <i className="bi bi-chevron-right"></i>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProjectList;
