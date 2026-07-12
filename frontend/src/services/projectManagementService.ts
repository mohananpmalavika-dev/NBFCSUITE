/**
 * Project Management API Service
 * Handles all API calls for project management features
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/project-management`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

export interface Project {
  id: string;
  project_code: string;
  project_name: string;
  project_description?: string;
  project_type: 'internal' | 'external' | 'research' | 'maintenance' | 'development' | 'infrastructure' | 'compliance' | 'audit';
  project_priority: 'low' | 'medium' | 'high' | 'critical';
  status: 'planning' | 'in_progress' | 'on_hold' | 'completed' | 'cancelled' | 'archived';
  planned_start_date: string;
  planned_end_date: string;
  actual_start_date?: string;
  actual_end_date?: string;
  project_manager_id?: string;
  project_manager_name?: string;
  sponsor_name?: string;
  sponsor_email?: string;
  client_name?: string;
  client_contact?: string;
  department_id?: string;
  department_name?: string;
  estimated_budget?: number;
  approved_budget?: number;
  actual_cost?: number;
  currency: string;
  progress_percentage: number;
  health_status: 'green' | 'amber' | 'red';
  objectives?: string;
  success_criteria?: string;
  deliverables?: string[];
  key_risks?: string;
  current_issues?: string;
  tags?: string[];
  is_billable: boolean;
  is_confidential: boolean;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: string;
  task_code: string;
  task_title: string;
  task_description?: string;
  project_id: string;
  project_name: string;
  parent_task_id?: string;
  task_type: 'feature' | 'bug' | 'enhancement' | 'documentation' | 'testing' | 'research' | 'meeting' | 'review';
  task_priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'todo' | 'in_progress' | 'in_review' | 'blocked' | 'completed' | 'cancelled';
  assigned_to_id?: string;
  assigned_to_name?: string;
  assigned_by_id?: string;
  assigned_date?: string;
  planned_start_date?: string;
  planned_end_date?: string;
  actual_start_date?: string;
  actual_end_date?: string;
  due_date?: string;
  estimated_hours?: number;
  actual_hours?: number;
  remaining_hours?: number;
  progress_percentage: number;
  is_blocked: boolean;
  blocked_reason?: string;
  labels?: string[];
  tags?: string[];
  is_billable: boolean;
  created_at: string;
  updated_at: string;
}

export interface TimeEntry {
  id: string;
  entry_code: string;
  employee_id: string;
  employee_name: string;
  project_id: string;
  project_name: string;
  task_id?: string;
  task_title?: string;
  entry_date: string;
  start_time?: string;
  end_time?: string;
  hours: number;
  description: string;
  work_type?: string;
  status: 'draft' | 'submitted' | 'approved' | 'rejected' | 'billed';
  submitted_date?: string;
  approved_by_id?: string;
  approved_date?: string;
  rejection_reason?: string;
  is_billable: boolean;
  hourly_rate?: number;
  billing_amount?: number;
  created_at: string;
  updated_at: string;
}

export interface ProjectBudget {
  id: string;
  budget_code: string;
  project_id: string;
  project_name: string;
  budget_name: string;
  description?: string;
  fiscal_year: string;
  start_date: string;
  end_date: string;
  planned_budget: number;
  approved_budget?: number;
  revised_budget?: number;
  committed_cost: number;
  actual_cost: number;
  available_budget: number;
  budget_variance: number;
  variance_percentage: number;
  status: 'draft' | 'approved' | 'active' | 'exceeded' | 'closed';
  currency: string;
  alert_threshold_percentage: number;
  is_threshold_exceeded: boolean;
  expense_lines: BudgetExpenseLine[];
  created_at: string;
  updated_at: string;
}

export interface BudgetExpenseLine {
  id: string;
  budget_id: string;
  expense_category: string;
  description?: string;
  planned_amount: number;
  committed_amount: number;
  actual_amount: number;
  variance: number;
  status: 'planned' | 'committed' | 'actual';
  expense_month?: string;
}

export interface ProjectStats {
  total_projects: number;
  active_projects: number;
  completed_projects: number;
  on_hold_projects: number;
  total_budget: number;
  total_spent: number;
  budget_utilization_percentage: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// ============================================================================
// PROJECT APIs
// ============================================================================

export const projectAPI = {
  // Get project statistics
  getStats: async (): Promise<ProjectStats> => {
    const response = await api.get('/projects/stats');
    return response.data;
  },

  // List projects with filters
  list: async (params: {
    page?: number;
    page_size?: number;
    status?: string[];
    priority?: string[];
    project_type?: string[];
    project_manager_id?: string;
    department_id?: string;
    search?: string;
    start_date_from?: string;
    start_date_to?: string;
  }): Promise<PaginatedResponse<Project>> => {
    const response = await api.get('/projects', { params });
    return response.data;
  },

  // Get project by ID
  getById: async (id: string): Promise<Project> => {
    const response = await api.get(`/projects/${id}`);
    return response.data;
  },

  // Create project
  create: async (data: Partial<Project>): Promise<Project> => {
    const response = await api.post('/projects', data);
    return response.data;
  },

  // Update project
  update: async (id: string, data: Partial<Project>): Promise<Project> => {
    const response = await api.put(`/projects/${id}`, data);
    return response.data;
  },

  // Delete project
  delete: async (id: string): Promise<void> => {
    await api.delete(`/projects/${id}`);
  },

  // Get project milestones
  getMilestones: async (projectId: string): Promise<any[]> => {
    const response = await api.get(`/projects/${projectId}/milestones`);
    return response.data;
  },

  // Create milestone
  createMilestone: async (projectId: string, data: any): Promise<any> => {
    const response = await api.post(`/projects/${projectId}/milestones`, data);
    return response.data;
  },

  // Update milestone
  updateMilestone: async (milestoneId: string, data: any): Promise<any> => {
    const response = await api.put(`/projects/milestones/${milestoneId}`, data);
    return response.data;
  },

  // Delete milestone
  deleteMilestone: async (milestoneId: string): Promise<void> => {
    await api.delete(`/projects/milestones/${milestoneId}`);
  },
};

// ============================================================================
// TASK APIs
// ============================================================================

export const taskAPI = {
  // List tasks with filters
  list: async (params: {
    page?: number;
    page_size?: number;
    project_id?: string;
    status?: string[];
    priority?: string[];
    task_type?: string[];
    assigned_to_id?: string;
    search?: string;
    due_date_from?: string;
    due_date_to?: string;
  }): Promise<PaginatedResponse<Task>> => {
    const response = await api.get('/tasks', { params });
    return response.data;
  },

  // Get my tasks
  getMyTasks: async (status?: string[]): Promise<Task[]> => {
    const response = await api.get('/tasks/my-tasks', { params: { status } });
    return response.data;
  },

  // Get task by ID
  getById: async (id: string): Promise<Task> => {
    const response = await api.get(`/tasks/${id}`);
    return response.data;
  },

  // Create task
  create: async (data: Partial<Task>): Promise<Task> => {
    const response = await api.post('/tasks', data);
    return response.data;
  },

  // Update task
  update: async (id: string, data: Partial<Task>): Promise<Task> => {
    const response = await api.put(`/tasks/${id}`, data);
    return response.data;
  },

  // Delete task
  delete: async (id: string): Promise<void> => {
    await api.delete(`/tasks/${id}`);
  },

  // Get task comments
  getComments: async (taskId: string): Promise<any[]> => {
    const response = await api.get(`/tasks/${taskId}/comments`);
    return response.data;
  },

  // Create comment
  createComment: async (taskId: string, data: { comment_text: string; is_internal?: boolean }): Promise<any> => {
    const response = await api.post(`/tasks/${taskId}/comments`, data);
    return response.data;
  },
};

// ============================================================================
// TIME TRACKING APIs
// ============================================================================

export const timeTrackingAPI = {
  // List time entries
  list: async (params: {
    page?: number;
    page_size?: number;
    employee_id?: string;
    project_id?: string;
    task_id?: string;
    status?: string[];
    date_from?: string;
    date_to?: string;
  }): Promise<PaginatedResponse<TimeEntry>> => {
    const response = await api.get('/time-entries', { params });
    return response.data;
  },

  // Get my timesheet
  getMyTimesheet: async (dateFrom: string, dateTo: string): Promise<TimeEntry[]> => {
    const response = await api.get('/time-entries/my-timesheet', {
      params: { date_from: dateFrom, date_to: dateTo },
    });
    return response.data;
  },

  // Get time entry by ID
  getById: async (id: string): Promise<TimeEntry> => {
    const response = await api.get(`/time-entries/${id}`);
    return response.data;
  },

  // Create time entry
  create: async (data: Partial<TimeEntry>): Promise<TimeEntry> => {
    const response = await api.post('/time-entries', data);
    return response.data;
  },

  // Update time entry
  update: async (id: string, data: Partial<TimeEntry>): Promise<TimeEntry> => {
    const response = await api.put(`/time-entries/${id}`, data);
    return response.data;
  },

  // Delete time entry
  delete: async (id: string): Promise<void> => {
    await api.delete(`/time-entries/${id}`);
  },

  // Submit time entries
  submit: async (entryIds: string[]): Promise<{ message: string; count: number }> => {
    const response = await api.post('/time-entries/submit', entryIds);
    return response.data;
  },

  // Approve/Reject time entries
  approveReject: async (data: {
    time_entry_ids: string[];
    action: 'approve' | 'reject';
    rejection_reason?: string;
  }): Promise<{ message: string; count: number }> => {
    const response = await api.post('/time-entries/approve-reject', data);
    return response.data;
  },

  // Get project time summary
  getProjectSummary: async (projectId: string): Promise<any> => {
    const response = await api.get(`/time-entries/projects/${projectId}/summary`);
    return response.data;
  },
};

// ============================================================================
// BUDGET APIs
// ============================================================================

export const budgetAPI = {
  // List budgets
  list: async (params: {
    page?: number;
    page_size?: number;
    project_id?: string;
    fiscal_year?: string;
    status?: string[];
  }): Promise<PaginatedResponse<ProjectBudget>> => {
    const response = await api.get('/budgets', { params });
    return response.data;
  },

  // Get budget by ID
  getById: async (id: string): Promise<ProjectBudget> => {
    const response = await api.get(`/budgets/${id}`);
    return response.data;
  },

  // Create budget
  create: async (data: Partial<ProjectBudget>): Promise<ProjectBudget> => {
    const response = await api.post('/budgets', data);
    return response.data;
  },

  // Update budget
  update: async (id: string, data: Partial<ProjectBudget>): Promise<ProjectBudget> => {
    const response = await api.put(`/budgets/${id}`, data);
    return response.data;
  },

  // Approve budget
  approve: async (id: string): Promise<ProjectBudget> => {
    const response = await api.post(`/budgets/${id}/approve`);
    return response.data;
  },

  // Delete budget
  delete: async (id: string): Promise<void> => {
    await api.delete(`/budgets/${id}`);
  },

  // Add expense line
  addExpenseLine: async (budgetId: string, data: Partial<BudgetExpenseLine>): Promise<BudgetExpenseLine> => {
    const response = await api.post(`/budgets/${budgetId}/expense-lines`, data);
    return response.data;
  },

  // Update expense line
  updateExpenseLine: async (expenseLineId: string, data: Partial<BudgetExpenseLine>): Promise<BudgetExpenseLine> => {
    const response = await api.put(`/budgets/expense-lines/${expenseLineId}`, data);
    return response.data;
  },

  // Delete expense line
  deleteExpenseLine: async (expenseLineId: string): Promise<void> => {
    await api.delete(`/budgets/expense-lines/${expenseLineId}`);
  },
};

export default {
  projectAPI,
  taskAPI,
  timeTrackingAPI,
  budgetAPI,
};
