/**
 * Task Board Component
 * Kanban-style task board for task management
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { taskAPI, Task } from '../../services/projectManagementService';
import './ProjectManagement.css';

const TaskBoard: React.FC = () => {
  const navigate = useNavigate();
  const { projectId } = useParams<{ projectId?: string }>();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);

  const columns = [
    { id: 'todo', title: 'To Do', status: 'todo' },
    { id: 'in_progress', title: 'In Progress', status: 'in_progress' },
    { id: 'in_review', title: 'In Review', status: 'in_review' },
    { id: 'completed', title: 'Completed', status: 'completed' },
  ];

  useEffect(() => {
    loadTasks();
  }, [projectId]);

  const loadTasks = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await taskAPI.list({
        project_id: projectId,
        page_size: 100,
      });

      setTasks(response.items);
    } catch (err: any) {
      setError(err.message || 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (taskId: string, newStatus: string) => {
    try {
      await taskAPI.update(taskId, { status: newStatus as any });
      await loadTasks();
    } catch (err: any) {
      alert('Failed to update task status');
    }
  };

  const getTasksByStatus = (status: string) => {
    return tasks.filter((task) => task.status === status);
  };

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      low: '#6c757d',
      medium: '#17a2b8',
      high: '#ffc107',
      urgent: '#dc3545',
    };
    return colors[priority] || '#6c757d';
  };

  if (loading) {
    return (
      <div className="pm-container">
        <div className="loading-spinner">Loading tasks...</div>
      </div>
    );
  }

  return (
    <div className="pm-container">
      {/* Header */}
      <div className="pm-header">
        <div>
          <h1>Task Board</h1>
          <p className="text-muted">Manage tasks in Kanban view</p>
        </div>
        <button className="btn btn-primary" onClick={() => navigate(`/project-management/tasks/new${projectId ? `?project=${projectId}` : ''}`)}>
          <i className="bi bi-plus-circle"></i> New Task
        </button>
      </div>

      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}

      {/* Kanban Board */}
      <div className="kanban-board">
        {columns.map((column) => {
          const columnTasks = getTasksByStatus(column.status);
          return (
            <div key={column.id} className="kanban-column">
              <div className="kanban-column-header">
                <h3>{column.title}</h3>
                <span className="task-count">{columnTasks.length}</span>
              </div>

              <div className="kanban-column-body">
                {columnTasks.length === 0 ? (
                  <div className="empty-column">
                    <p>No tasks</p>
                  </div>
                ) : (
                  columnTasks.map((task) => (
                    <div
                      key={task.id}
                      className="task-card"
                      onClick={() => navigate(`/project-management/tasks/${task.id}`)}
                      style={{ borderLeftColor: getPriorityColor(task.task_priority) }}
                    >
                      <div className="task-card-header">
                        <span className="task-code">{task.task_code}</span>
                        <span className={`badge badge-${task.task_priority === 'urgent' ? 'danger' : task.task_priority === 'high' ? 'warning' : 'secondary'}`}>
                          {task.task_priority.toUpperCase()}
                        </span>
                      </div>

                      <h4 className="task-title">{task.task_title}</h4>

                      {task.task_description && (
                        <p className="task-description">{task.task_description.substring(0, 100)}{task.task_description.length > 100 ? '...' : ''}</p>
                      )}

                      <div className="task-card-footer">
                        <div className="task-meta">
                          {task.assigned_to_name && (
                            <div className="task-assignee">
                              <i className="bi bi-person"></i> {task.assigned_to_name}
                            </div>
                          )}
                          {task.due_date && (
                            <div className="task-due-date">
                              <i className="bi bi-calendar"></i> {new Date(task.due_date).toLocaleDateString()}
                            </div>
                          )}
                        </div>

                        {task.estimated_hours && (
                          <div className="task-hours">
                            <i className="bi bi-clock"></i> {task.estimated_hours}h
                          </div>
                        )}
                      </div>

                      {task.labels && task.labels.length > 0 && (
                        <div className="task-labels">
                          {task.labels.slice(0, 3).map((label, idx) => (
                            <span key={idx} className="task-label">{label}</span>
                          ))}
                        </div>
                      )}

                      <div className="task-actions" onClick={(e) => e.stopPropagation()}>
                        <select
                          value={task.status}
                          onChange={(e) => handleStatusChange(task.id, e.target.value)}
                          className="status-select"
                        >
                          <option value="todo">To Do</option>
                          <option value="in_progress">In Progress</option>
                          <option value="in_review">In Review</option>
                          <option value="blocked">Blocked</option>
                          <option value="completed">Completed</option>
                        </select>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default TaskBoard;
