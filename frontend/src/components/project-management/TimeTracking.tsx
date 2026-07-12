/**
 * Time Tracking Component
 * Timesheet entry and management
 */

import React, { useState, useEffect } from 'react';
import { timeTrackingAPI, TimeEntry } from '../../services/projectManagementService';
import './ProjectManagement.css';

const TimeTracking: React.FC = () => {
  const [timeEntries, setTimeEntries] = useState<TimeEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  // Date range for timesheet
  const [weekStart, setWeekStart] = useState<Date>(getWeekStart(new Date()));
  const [weekEnd, setWeekEnd] = useState<Date>(getWeekEnd(new Date()));

  // Form state
  const [formData, setFormData] = useState({
    project_id: '',
    task_id: '',
    entry_date: new Date().toISOString().split('T')[0],
    hours: '',
    description: '',
    work_type: '',
    is_billable: true,
  });

  function getWeekStart(date: Date): Date {
    const d = new Date(date);
    const day = d.getDay();
    const diff = d.getDate() - day + (day === 0 ? -6 : 1); // Adjust when day is Sunday
    return new Date(d.setDate(diff));
  }

  function getWeekEnd(date: Date): Date {
    const start = getWeekStart(date);
    return new Date(start.getTime() + 6 * 24 * 60 * 60 * 1000);
  }

  useEffect(() => {
    loadTimesheet();
  }, [weekStart, weekEnd]);

  const loadTimesheet = async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await timeTrackingAPI.getMyTimesheet(
        weekStart.toISOString().split('T')[0],
        weekEnd.toISOString().split('T')[0]
      );

      setTimeEntries(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load timesheet');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await timeTrackingAPI.create({
        ...formData,
        hours: parseFloat(formData.hours),
      } as any);

      setShowForm(false);
      setFormData({
        project_id: '',
        task_id: '',
        entry_date: new Date().toISOString().split('T')[0],
        hours: '',
        description: '',
        work_type: '',
        is_billable: true,
      });
      await loadTimesheet();
    } catch (err: any) {
      alert('Failed to create time entry');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this time entry?')) return;

    try {
      await timeTrackingAPI.delete(id);
      await loadTimesheet();
    } catch (err: any) {
      alert('Failed to delete time entry');
    }
  };

  const handleSubmitEntries = async (entryIds: string[]) => {
    try {
      await timeTrackingAPI.submit(entryIds);
      await loadTimesheet();
      alert('Time entries submitted successfully');
    } catch (err: any) {
      alert('Failed to submit time entries');
    }
  };

  const navigateWeek = (direction: 'prev' | 'next') => {
    const daysToAdd = direction === 'next' ? 7 : -7;
    const newStart = new Date(weekStart.getTime() + daysToAdd * 24 * 60 * 60 * 1000);
    setWeekStart(getWeekStart(newStart));
    setWeekEnd(getWeekEnd(newStart));
  };

  const getTotalHours = () => {
    return timeEntries.reduce((sum, entry) => sum + entry.hours, 0);
  };

  const getDraftEntries = () => {
    return timeEntries.filter((entry) => entry.status === 'draft');
  };

  const getStatusBadge = (status: string) => {
    const statusColors: Record<string, string> = {
      draft: 'badge-secondary',
      submitted: 'badge-info',
      approved: 'badge-success',
      rejected: 'badge-danger',
      billed: 'badge-primary',
    };
    return statusColors[status] || 'badge-secondary';
  };

  if (loading) {
    return (
      <div className="pm-container">
        <div className="loading-spinner">Loading timesheet...</div>
      </div>
    );
  }

  return (
    <div className="pm-container">
      {/* Header */}
      <div className="pm-header">
        <div>
          <h1>Time Tracking</h1>
          <p className="text-muted">Track time spent on projects and tasks</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          <i className="bi bi-plus-circle"></i> {showForm ? 'Cancel' : 'Add Time Entry'}
        </button>
      </div>

      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}

      {/* Time Entry Form */}
      {showForm && (
        <div className="card mb-3">
          <div className="card-header">
            <h5>New Time Entry</h5>
          </div>
          <div className="card-body">
            <form onSubmit={handleSubmit}>
              <div className="form-row">
                <div className="form-group">
                  <label>Date *</label>
                  <input
                    type="date"
                    className="form-control"
                    value={formData.entry_date}
                    onChange={(e) => setFormData({ ...formData, entry_date: e.target.value })}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Hours *</label>
                  <input
                    type="number"
                    className="form-control"
                    value={formData.hours}
                    onChange={(e) => setFormData({ ...formData, hours: e.target.value })}
                    min="0.25"
                    max="24"
                    step="0.25"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Work Type</label>
                  <select
                    className="form-control"
                    value={formData.work_type}
                    onChange={(e) => setFormData({ ...formData, work_type: e.target.value })}
                  >
                    <option value="">Select Type</option>
                    <option value="development">Development</option>
                    <option value="testing">Testing</option>
                    <option value="meeting">Meeting</option>
                    <option value="documentation">Documentation</option>
                    <option value="review">Review</option>
                    <option value="research">Research</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>Description *</label>
                <textarea
                  className="form-control"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  required
                  placeholder="Describe the work done..."
                ></textarea>
              </div>

              <div className="form-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={formData.is_billable}
                    onChange={(e) => setFormData({ ...formData, is_billable: e.target.checked })}
                  />
                  Billable
                </label>
              </div>

              <button type="submit" className="btn btn-primary">
                Save Time Entry
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Week Navigator */}
      <div className="card mb-3">
        <div className="card-body">
          <div className="week-navigator">
            <button className="btn btn-outline-primary" onClick={() => navigateWeek('prev')}>
              <i className="bi bi-chevron-left"></i> Previous Week
            </button>

            <div className="week-range">
              <h4>
                {weekStart.toLocaleDateString()} - {weekEnd.toLocaleDateString()}
              </h4>
              <p className="text-muted">Total Hours: {getTotalHours().toFixed(2)}</p>
            </div>

            <button className="btn btn-outline-primary" onClick={() => navigateWeek('next')}>
              Next Week <i className="bi bi-chevron-right"></i>
            </button>
          </div>

          {getDraftEntries().length > 0 && (
            <div className="mt-3 text-center">
              <button
                className="btn btn-primary"
                onClick={() => handleSubmitEntries(getDraftEntries().map((e) => e.id))}
              >
                Submit {getDraftEntries().length} Draft Entries
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Timesheet Table */}
      <div className="card">
        <div className="card-header">
          <h5>Time Entries</h5>
        </div>
        <div className="card-body p-0">
          {timeEntries.length === 0 ? (
            <div className="empty-state">
              <i className="bi bi-clock-history"></i>
              <p>No time entries for this week</p>
            </div>
          ) : (
            <div className="table-responsive">
              <table className="table table-hover">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Project</th>
                    <th>Task</th>
                    <th>Hours</th>
                    <th>Work Type</th>
                    <th>Description</th>
                    <th>Status</th>
                    <th>Billable</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {timeEntries.map((entry) => (
                    <tr key={entry.id}>
                      <td>{new Date(entry.entry_date).toLocaleDateString()}</td>
                      <td>
                        <strong>{entry.project_name}</strong>
                      </td>
                      <td>{entry.task_title || <span className="text-muted">-</span>}</td>
                      <td>
                        <strong>{entry.hours}</strong>h
                      </td>
                      <td>{entry.work_type || <span className="text-muted">-</span>}</td>
                      <td>
                        <div className="description-cell">{entry.description}</div>
                      </td>
                      <td>
                        <span className={`badge ${getStatusBadge(entry.status)}`}>
                          {entry.status.toUpperCase()}
                        </span>
                      </td>
                      <td>
                        {entry.is_billable ? (
                          <i className="bi bi-check-circle text-success"></i>
                        ) : (
                          <i className="bi bi-x-circle text-muted"></i>
                        )}
                      </td>
                      <td>
                        {entry.status === 'draft' && (
                          <button
                            className="btn btn-sm btn-outline-danger"
                            onClick={() => handleDelete(entry.id)}
                          >
                            <i className="bi bi-trash"></i>
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr>
                    <td colSpan={3} className="text-right"><strong>Total:</strong></td>
                    <td><strong>{getTotalHours().toFixed(2)}h</strong></td>
                    <td colSpan={5}></td>
                  </tr>
                </tfoot>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TimeTracking;
