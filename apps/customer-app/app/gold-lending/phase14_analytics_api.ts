/**
 * Phase 14: Analytics & Business Intelligence API Client
 * TypeScript client for analytics and BI operations
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

// =====================================================
// Type Definitions
// =====================================================

export interface DataWarehouse {
  id: string;
  warehouse_code: string;
  warehouse_name: string;
  warehouse_type: string;
  connection_config: Record<string, any>;
  refresh_schedule?: Record<string, any>;
  last_refresh_at?: string;
  next_refresh_at?: string;
  status: string;
  storage_size_gb?: number;
  row_count?: number;
  tags?: string[];
  metadata?: Record<string, any>;
  maker_id?: string;
  checker_id?: string;
  maker_comment?: string;
  checker_comment?: string;
  approval_status: string;
  approved_at?: string;
  created_by?: string;
  updated_by?: string;
  created_at: string;
  updated_at: string;
  version: number;
}

export interface DataSource {
  id: string;
  source_code: string;
  source_name: string;
  source_type: string;
  connection_string?: string;
  connection_config: Record<string, any>;
  authentication_type?: string;
  schema_config?: Record<string, any>;
  sync_frequency?: string;
  last_sync_at?: string;
  next_sync_at?: string;
  sync_status: string;
  avg_response_time_ms?: number;
  data_volume_gb?: number;
  record_count?: number;
  health_status: string;
  last_health_check_at?: string;
  health_check_config?: Record<string, any>;
  status: string;
  metadata?: Record<string, any>;
  created_by?: string;
  updated_by?: string;
  created_at: string;
  updated_at: string;
  version: number;
}

export interface Report {
  id: string;
  report_code: string;
  report_name: string;
  report_type: string;
  category?: string;
  description?: string;
  data_source_id?: string;
  query_definition: Record<string, any>;
  parameters?: Array<Record<string, any>>;
  visualization_type?: string;
  visualization_config?: Record<string, any>;
  layout_config?: Record<string, any>;
  schedule_enabled?: boolean;
  schedule_config?: Record<string, any>;
  last_run_at?: string;
  next_run_at?: string;
  avg_execution_time_ms?: number;
  cache_enabled?: boolean;
  cache_duration_minutes?: number;
  last_cached_at?: string;
  is_public?: boolean;
  owner_id?: string;
  shared_with?: string[];
  status: string;
  metadata?: Record<string, any>;
  created_by?: string;
  updated_by?: string;
  created_at: string;
  updated_at: string;
  version: number;
}

export interface ReportExecution {
  id: string;
  execution_code: string;
  report_id: string;
  execution_type?: string;
  parameters_used?: Record<string, any>;
  filters_applied?: Record<string, any>;
  started_at: string;
  completed_at?: string;
  execution_time_ms?: number;
  rows_returned?: number;
  data_size_kb?: number;
  result_status?: string;
  result_location?: string;
  result_format?: string;
  result_preview?: Record<string, any>;
  error_message?: string;
  error_details?: Record<string, any>;
  retry_count: number;
  executed_by?: string;
  execution_context?: Record<string, any>;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface Dashboard {
  id: string;
  dashboard_code: string;
  dashboard_name: string;
  dashboard_type: string;
  category?: string;
  description?: string;
  layout_type?: string;
  layout_config: Record<string, any>;
  widgets: Array<Record<string, any>>;
  auto_refresh?: boolean;
  refresh_interval_seconds?: number;
  last_refreshed_at?: string;
  global_filters?: Array<Record<string, any>>;
  filter_config?: Record<string, any>;
  is_public?: boolean;
  owner_id?: string;
  shared_with?: string[];
  theme?: string;
  display_config?: Record<string, any>;
  mobile_optimized?: boolean;
  view_count: number;
  last_viewed_at?: string;
  avg_load_time_ms?: number;
  status: string;
  metadata?: Record<string, any>;
  created_by?: string;
  updated_by?: string;
  created_at: string;
  updated_at: string;
  version: number;
}

export interface Widget {
  id: string;
  widget_code: string;
  widget_name: string;
  widget_type: string;
  report_id?: string;
  data_source_id?: string;
  query_config?: Record<string, any>;
  chart_type?: string;
  visualization_config: Record<string, any>;
  color_scheme?: string;
  drill_down_enabled?: boolean;
  drill_down_config?: Record<string, any>;
  click_actions?: Record<string, any>;
  auto_refresh?: boolean;
  refresh_interval_seconds?: number;
  cache_enabled?: boolean;
  size_config?: Record<string, any>;
  position_config?: Record<string, any>;
  status: string;
  metadata?: Record<string, any>;
  created_by?: string;
  updated_by?: string;
  created_at: string;
  updated_at: string;
  version: number;
}

export interface MLModel {
  id: string;
  model_code: string;
  model_name: string;
  model_type: string;
  algorithm?: string;
  framework?: string;
  version: string;
  model_file_path?: string;
  model_artifact_url?: string;
  training_data_source_id?: string;
  training_dataset_size?: number;
  training_started_at?: string;
  training_completed_at?: string;
  training_duration_minutes?: number;
  accuracy_score?: number;
  precision_score?: number;
  recall_score?: number;
  f1_score?: number;
  rmse?: number;
  mae?: number;
  r2_score?: number;
  performance_metrics?: Record<string, any>;
  hyperparameters?: Record<string, any>;
  feature_importance?: Record<string, any>;
  deployment_status: string;
  deployment_endpoint?: string;
  deployed_at?: string;
  prediction_count: number;
  last_prediction_at?: string;
  avg_prediction_time_ms?: number;
  status: string;
  metadata?: Record<string, any>;
  created_by?: string;
  updated_by?: string;
  created_at: string;
  updated_at: string;
  version: number;
}

export interface Prediction {
  id: string;
  prediction_code: string;
  model_id: string;
  input_features: Record<string, any>;
  prediction_result: Record<string, any>;
  confidence_score?: number;
  prediction_time_ms?: number;
  model_version?: string;
  prediction_type?: string;
  business_context?: Record<string, any>;
  actual_value?: Record<string, any>;
  prediction_error?: number;
  is_accurate?: boolean;
  requested_by?: string;
  request_context?: Record<string, any>;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface DataStream {
  id: string;
  stream_code: string;
  stream_name: string;
  stream_type: string;
  connection_config: Record<string, any>;
  topic_name?: string;
  partition_key?: string;
  data_format?: string;
  schema_definition?: Record<string, any>;
  processing_mode?: string;
  batch_size?: number;
  batch_timeout_ms?: number;
  consumer_groups?: string[];
  consumer_config?: Record<string, any>;
  messages_per_second?: number;
  total_messages_processed: number;
  last_message_at?: string;
  lag_seconds?: number;
  error_handling_strategy?: string;
  dead_letter_queue?: string;
  error_count: number;
  status: string;
  metadata?: Record<string, any>;
  created_by?: string;
  updated_by?: string;
  created_at: string;
  updated_at: string;
  version: number;
}

export interface AnalyticsAlert {
  id: string;
  alert_code: string;
  alert_name: string;
  alert_type: string;
  severity?: string;
  data_source_id?: string;
  metric_name?: string;
  condition_config: Record<string, any>;
  evaluation_frequency_minutes?: number;
  lookback_period_minutes?: number;
  detection_algorithm?: string;
  sensitivity?: number;
  notification_channels?: string[];
  notification_template?: string;
  recipients?: string[];
  last_evaluated_at?: string;
  next_evaluation_at?: string;
  is_triggered: boolean;
  last_triggered_at?: string;
  trigger_count: number;
  suppression_enabled?: boolean;
  suppression_duration_minutes?: number;
  suppressed_until?: string;
  status: string;
  metadata?: Record<string, any>;
  created_by?: string;
  updated_by?: string;
  created_at: string;
  updated_at: string;
  version: number;
}

export interface AlertNotification {
  id: string;
  notification_code: string;
  alert_id: string;
  notification_type?: string;
  recipient?: string;
  subject?: string;
  message?: string;
  sent_at?: string;
  delivered_at?: string;
  delivery_status?: string;
  alert_value?: Record<string, any>;
  threshold_value?: Record<string, any>;
  deviation_percentage?: number;
  acknowledged_by?: string;
  acknowledged_at?: string;
  resolution_notes?: string;
  resolved_at?: string;
  error_message?: string;
  retry_count: number;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface DataQualityRule {
  id: string;
  rule_code: string;
  rule_name: string;
  rule_type: string;
  data_source_id?: string;
  table_name?: string;
  column_name?: string;
  rule_definition: Record<string, any>;
  validation_query?: string;
  expected_value?: Record<string, any>;
  tolerance?: number;
  execution_frequency_minutes?: number;
  last_executed_at?: string;
  next_execution_at?: string;
  last_result_status?: string;
  pass_rate?: number;
  failure_count: number;
  on_failure_action?: string;
  notification_config?: Record<string, any>;
  status: string;
  metadata?: Record<string, any>;
  created_by?: string;
  updated_by?: string;
  created_at: string;
  updated_at: string;
  version: number;
}

export interface AnalyticsOverview {
  total_data_sources: number;
  active_data_sources: number;
  total_reports: number;
  total_dashboards: number;
  total_ml_models: number;
  deployed_models: number;
  total_streams: number;
  active_streams: number;
  active_alerts: number;
  triggered_alerts: number;
  total_dashboard_views: number;
  total_predictions: number;
}

// =====================================================
// API Client Class
// =====================================================

export class AnalyticsAPIClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }

  // =====================================================
  // Data Warehouse Methods
  // =====================================================

  async createDataWarehouse(data: Partial<DataWarehouse>): Promise<DataWarehouse> {
    return this.request('/api/v1/gold/analytics/warehouses', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listDataWarehouses(params?: {
    skip?: number;
    limit?: number;
    warehouse_type?: string;
    status?: string;
  }): Promise<DataWarehouse[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request(`/api/v1/gold/analytics/warehouses?${query}`);
  }

  async getDataWarehouse(id: string): Promise<DataWarehouse> {
    return this.request(`/api/v1/gold/analytics/warehouses/${id}`);
  }

  async updateDataWarehouse(id: string, data: Partial<DataWarehouse>): Promise<DataWarehouse> {
    return this.request(`/api/v1/gold/analytics/warehouses/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async approveDataWarehouse(id: string, approval: {
    approval_status: string;
    checker_comment?: string;
  }): Promise<DataWarehouse> {
    return this.request(`/api/v1/gold/analytics/warehouses/${id}/approve`, {
      method: 'POST',
      body: JSON.stringify(approval),
    });
  }

  async deleteDataWarehouse(id: string): Promise<void> {
    return this.request(`/api/v1/gold/analytics/warehouses/${id}`, {
      method: 'DELETE',
    });
  }

  // =====================================================
  // Data Source Methods
  // =====================================================

  async createDataSource(data: Partial<DataSource>): Promise<DataSource> {
    return this.request('/api/v1/gold/analytics/data-sources', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listDataSources(params?: {
    skip?: number;
    limit?: number;
    source_type?: string;
    status?: string;
    health_status?: string;
  }): Promise<DataSource[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request(`/api/v1/gold/analytics/data-sources?${query}`);
  }

  async getDataSource(id: string): Promise<DataSource> {
    return this.request(`/api/v1/gold/analytics/data-sources/${id}`);
  }

  async updateDataSource(id: string, data: Partial<DataSource>): Promise<DataSource> {
    return this.request(`/api/v1/gold/analytics/data-sources/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async syncDataSource(id: string): Promise<DataSource> {
    return this.request(`/api/v1/gold/analytics/data-sources/${id}/sync`, {
      method: 'POST',
    });
  }

  async checkDataSourceHealth(id: string): Promise<DataSource> {
    return this.request(`/api/v1/gold/analytics/data-sources/${id}/health-check`, {
      method: 'POST',
    });
  }

  async deleteDataSource(id: string): Promise<void> {
    return this.request(`/api/v1/gold/analytics/data-sources/${id}`, {
      method: 'DELETE',
    });
  }

  // =====================================================
  // Report Methods
  // =====================================================

  async createReport(data: Partial<Report>): Promise<Report> {
    return this.request('/api/v1/gold/analytics/reports', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listReports(params?: {
    skip?: number;
    limit?: number;
    report_type?: string;
    category?: string;
    status?: string;
  }): Promise<Report[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request(`/api/v1/gold/analytics/reports?${query}`);
  }

  async getReport(id: string): Promise<Report> {
    return this.request(`/api/v1/gold/analytics/reports/${id}`);
  }

  async updateReport(id: string, data: Partial<Report>): Promise<Report> {
    return this.request(`/api/v1/gold/analytics/reports/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async executeReport(id: string, request: {
    parameters?: Record<string, any>;
    filters?: Record<string, any>;
    output_format?: string;
  }): Promise<ReportExecution> {
    return this.request(`/api/v1/gold/analytics/reports/${id}/execute`, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async listReportExecutions(reportId: string, params?: {
    skip?: number;
    limit?: number;
  }): Promise<ReportExecution[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request(`/api/v1/gold/analytics/reports/${reportId}/executions?${query}`);
  }

  async deleteReport(id: string): Promise<void> {
    return this.request(`/api/v1/gold/analytics/reports/${id}`, {
      method: 'DELETE',
    });
  }

  // =====================================================
  // Dashboard Methods
  // =====================================================

  async createDashboard(data: Partial<Dashboard>): Promise<Dashboard> {
    return this.request('/api/v1/gold/analytics/dashboards', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listDashboards(params?: {
    skip?: number;
    limit?: number;
    dashboard_type?: string;
    category?: string;
    status?: string;
  }): Promise<Dashboard[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request(`/api/v1/gold/analytics/dashboards?${query}`);
  }

  async getDashboard(id: string): Promise<Dashboard> {
    return this.request(`/api/v1/gold/analytics/dashboards/${id}`);
  }

  async updateDashboard(id: string, data: Partial<Dashboard>): Promise<Dashboard> {
    return this.request(`/api/v1/gold/analytics/dashboards/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async refreshDashboard(id: string): Promise<Dashboard> {
    return this.request(`/api/v1/gold/analytics/dashboards/${id}/refresh`, {
      method: 'POST',
    });
  }

  async deleteDashboard(id: string): Promise<void> {
    return this.request(`/api/v1/gold/analytics/dashboards/${id}`, {
      method: 'DELETE',
    });
  }

  // =====================================================
  // Widget Methods
  // =====================================================

  async createWidget(data: Partial<Widget>): Promise<Widget> {
    return this.request('/api/v1/gold/analytics/widgets', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listWidgets(params?: {
    skip?: number;
    limit?: number;
    widget_type?: string;
    status?: string;
  }): Promise<Widget[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request(`/api/v1/gold/analytics/widgets?${query}`);
  }

  async getWidget(id: string): Promise<Widget> {
    return this.request(`/api/v1/gold/analytics/widgets/${id}`);
  }

  async updateWidget(id: string, data: Partial<Widget>): Promise<Widget> {
    return this.request(`/api/v1/gold/analytics/widgets/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteWidget(id: string): Promise<void> {
    return this.request(`/api/v1/gold/analytics/widgets/${id}`, {
      method: 'DELETE',
    });
  }

  // =====================================================
  // ML Model Methods
  // =====================================================

  async createMLModel(data: Partial<MLModel>): Promise<MLModel> {
    return this.request('/api/v1/gold/analytics/ml-models', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listMLModels(params?: {
    skip?: number;
    limit?: number;
    model_type?: string;
    deployment_status?: string;
    status?: string;
  }): Promise<MLModel[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request(`/api/v1/gold/analytics/ml-models?${query}`);
  }

  async getMLModel(id: string): Promise<MLModel> {
    return this.request(`/api/v1/gold/analytics/ml-models/${id}`);
  }

  async updateMLModel(id: string, data: Partial<MLModel>): Promise<MLModel> {
    return this.request(`/api/v1/gold/analytics/ml-models/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async updateMLModelPerformance(id: string, performance: {
    accuracy_score?: number;
    precision_score?: number;
    recall_score?: number;
    f1_score?: number;
    rmse?: number;
    mae?: number;
    r2_score?: number;
    performance_metrics?: Record<string, any>;
  }): Promise<MLModel> {
    return this.request(`/api/v1/gold/analytics/ml-models/${id}/performance`, {
      method: 'PUT',
      body: JSON.stringify(performance),
    });
  }

  async deployMLModel(id: string): Promise<MLModel> {
    return this.request(`/api/v1/gold/analytics/ml-models/${id}/deploy`, {
      method: 'POST',
    });
  }

  async makePrediction(modelId: string, request: {
    input_features: Record<string, any>;
    prediction_type?: string;
    business_context?: Record<string, any>;
  }): Promise<Prediction> {
    return this.request(`/api/v1/gold/analytics/ml-models/${modelId}/predict`, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async listModelPredictions(modelId: string, params?: {
    skip?: number;
    limit?: number;
  }): Promise<Prediction[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request(`/api/v1/gold/analytics/ml-models/${modelId}/predictions?${query}`);
  }

  async deleteMLModel(id: string): Promise<void> {
    return this.request(`/api/v1/gold/analytics/ml-models/${id}`, {
      method: 'DELETE',
    });
  }

  // =====================================================
  // Prediction Methods
  // =====================================================

  async getPrediction(id: string): Promise<Prediction> {
    return this.request(`/api/v1/gold/analytics/predictions/${id}`);
  }

  async validatePrediction(id: string, validation: {
    actual_value: Record<string, any>;
    validation_notes?: string;
  }): Promise<Prediction> {
    return this.request(`/api/v1/gold/analytics/predictions/${id}/validate`, {
      method: 'POST',
      body: JSON.stringify(validation),
    });
  }

  // =====================================================
  // Data Stream Methods
  // =====================================================

  async createDataStream(data: Partial<DataStream>): Promise<DataStream> {
    return this.request('/api/v1/gold/analytics/data-streams', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listDataStreams(params?: {
    skip?: number;
    limit?: number;
    stream_type?: string;
    status?: string;
  }): Promise<DataStream[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request(`/api/v1/gold/analytics/data-streams?${query}`);
  }

  async getDataStream(id: string): Promise<DataStream> {
    return this.request(`/api/v1/gold/analytics/data-streams/${id}`);
  }

  async updateDataStream(id: string, data: Partial<DataStream>): Promise<DataStream> {
    return this.request(`/api/v1/gold/analytics/data-streams/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async startDataStream(id: string): Promise<DataStream> {
    return this.request(`/api/v1/gold/analytics/data-streams/${id}/start`, {
      method: 'POST',
    });
  }

  async stopDataStream(id: string): Promise<DataStream> {
    return this.request(`/api/v1/gold/analytics/data-streams/${id}/stop`, {
      method: 'POST',
    });
  }

  async deleteDataStream(id: string): Promise<void> {
    return this.request(`/api/v1/gold/analytics/data-streams/${id}`, {
      method: 'DELETE',
    });
  }

  // =====================================================
  // Analytics Alert Methods
  // =====================================================

  async createAnalyticsAlert(data: Partial<AnalyticsAlert>): Promise<AnalyticsAlert> {
    return this.request('/api/v1/gold/analytics/alerts', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listAnalyticsAlerts(params?: {
    skip?: number;
    limit?: number;
    alert_type?: string;
    severity?: string;
    is_triggered?: boolean;
    status?: string;
  }): Promise<AnalyticsAlert[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request(`/api/v1/gold/analytics/alerts?${query}`);
  }

  async getAnalyticsAlert(id: string): Promise<AnalyticsAlert> {
    return this.request(`/api/v1/gold/analytics/alerts/${id}`);
  }

  async updateAnalyticsAlert(id: string, data: Partial<AnalyticsAlert>): Promise<AnalyticsAlert> {
    return this.request(`/api/v1/gold/analytics/alerts/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async testAnalyticsAlert(id: string): Promise<AnalyticsAlert> {
    return this.request(`/api/v1/gold/analytics/alerts/${id}/test`, {
      method: 'POST',
    });
  }

  async listAlertNotifications(alertId: string, params?: {
    skip?: number;
    limit?: number;
  }): Promise<AlertNotification[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request(`/api/v1/gold/analytics/alerts/${alertId}/notifications?${query}`);
  }

  async deleteAnalyticsAlert(id: string): Promise<void> {
    return this.request(`/api/v1/gold/analytics/alerts/${id}`, {
      method: 'DELETE',
    });
  }

  // =====================================================
  // Alert Notification Methods
  // =====================================================

  async getAlertNotification(id: string): Promise<AlertNotification> {
    return this.request(`/api/v1/gold/analytics/notifications/${id}`);
  }

  async acknowledgeAlertNotification(id: string, acknowledgement: {
    resolution_notes?: string;
  }): Promise<AlertNotification> {
    return this.request(`/api/v1/gold/analytics/notifications/${id}/acknowledge`, {
      method: 'POST',
      body: JSON.stringify(acknowledgement),
    });
  }

  // =====================================================
  // Data Quality Rule Methods
  // =====================================================

  async createDataQualityRule(data: Partial<DataQualityRule>): Promise<DataQualityRule> {
    return this.request('/api/v1/gold/analytics/data-quality-rules', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listDataQualityRules(params?: {
    skip?: number;
    limit?: number;
    rule_type?: string;
    status?: string;
  }): Promise<DataQualityRule[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request(`/api/v1/gold/analytics/data-quality-rules?${query}`);
  }

  async getDataQualityRule(id: string): Promise<DataQualityRule> {
    return this.request(`/api/v1/gold/analytics/data-quality-rules/${id}`);
  }

  async updateDataQualityRule(id: string, data: Partial<DataQualityRule>): Promise<DataQualityRule> {
    return this.request(`/api/v1/gold/analytics/data-quality-rules/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async executeDataQualityRule(id: string): Promise<DataQualityRule> {
    return this.request(`/api/v1/gold/analytics/data-quality-rules/${id}/execute`, {
      method: 'POST',
    });
  }

  async deleteDataQualityRule(id: string): Promise<void> {
    return this.request(`/api/v1/gold/analytics/data-quality-rules/${id}`, {
      method: 'DELETE',
    });
  }

  // =====================================================
  // Statistics & Analytics Methods
  // =====================================================

  async getAnalyticsOverview(): Promise<AnalyticsOverview> {
    return this.request('/api/v1/gold/analytics/statistics/overview');
  }

  async getReportExecutionMetrics(params?: {
    skip?: number;
    limit?: number;
  }): Promise<any[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request(`/api/v1/gold/analytics/statistics/report-executions?${query}`);
  }

  async getMLModelPerformanceMetrics(params?: {
    skip?: number;
    limit?: number;
  }): Promise<any[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request(`/api/v1/gold/analytics/statistics/ml-model-performance?${query}`);
  }

  async getDataStreamHealth(): Promise<any[]> {
    return this.request('/api/v1/gold/analytics/statistics/stream-health');
  }
}

// Export singleton instance
export const analyticsAPI = new AnalyticsAPIClient();

// Export default
export default analyticsAPI;
