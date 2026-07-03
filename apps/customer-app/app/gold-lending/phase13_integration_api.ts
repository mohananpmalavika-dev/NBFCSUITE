/**
 * Phase 13 - Integration Hub API Client
 * Handles external integrations, webhooks, API keys, and message queue
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ===== Types =====

export interface IntegrationProvider {
  provider_id: number;
  provider_code: string;
  provider_name: string;
  category: string;
  description?: string;
  base_url?: string;
  auth_type?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface IntegrationConfiguration {
  config_id: number;
  provider_id: number;
  config_name: string;
  environment: string;
  base_url: string;
  auth_config: any;
  timeout_seconds: number;
  retry_config: any;
  rate_limit_config?: any;
  status: string;
  created_by: number;
  approved_by?: number;
  approved_at?: string;
  last_health_check?: string;
  created_at: string;
  updated_at: string;
}

export interface IntegrationEndpoint {
  endpoint_id: number;
  config_id: number;
  endpoint_name: string;
  path: string;
  method: string;
  description?: string;
  request_schema?: any;
  response_schema?: any;
  timeout_seconds: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface IntegrationLog {
  log_id: number;
  config_id: number;
  endpoint_id?: number;
  correlation_id?: string;
  request_method: string;
  request_url: string;
  request_headers?: any;
  request_body?: any;
  response_status?: number;
  response_body?: any;
  response_time?: number;
  status: string;
  error_message?: string;
  request_timestamp: string;
  response_timestamp?: string;
}

export interface APIKey {
  key_id: number;
  config_id: number;
  key_name: string;
  key_value: string;
  key_prefix?: string;
  permissions: any;
  expires_at?: string;
  last_used_at?: string;
  is_active: boolean;
  revoked_at?: string;
  last_rotated?: string;
  created_by: number;
  created_at: string;
}

export interface Webhook {
  webhook_id: number;
  config_id: number;
  webhook_url: string;
  event_type: string;
  secret_key?: string;
  retry_policy: any;
  headers?: any;
  is_active: boolean;
  last_triggered?: string;
  created_at: string;
  updated_at: string;
}

export interface WebhookDelivery {
  delivery_id: number;
  webhook_id: number;
  payload: any;
  status: string;
  http_status?: number;
  response_body?: any;
  response_time?: number;
  error_message?: string;
  retry_count: number;
  next_retry?: string;
  sent_at: string;
  delivered_at?: string;
}

export interface MessageQueue {
  message_id: number;
  config_id: number;
  message_type: string;
  payload: any;
  priority: string;
  status: string;
  retry_count: number;
  max_retries: number;
  error_message?: string;
  created_at: string;
  processed_at?: string;
  completed_at?: string;
}

export interface IntegrationStatistics {
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  average_response_time: number;
  active_configurations: number;
  active_webhooks: number;
  pending_messages: number;
}

export interface ProviderPerformance {
  provider_id: number;
  provider_name: string;
  total_calls: number;
  successful_calls: number;
  success_rate: number;
  average_response_time: number;
}

export interface WebhookHealth {
  total_deliveries: number;
  successful_deliveries: number;
  failed_deliveries: number;
  pending_deliveries: number;
  success_rate: number;
  average_response_time: number;
  total_retries: number;
}

export interface QueueSummary {
  total_messages: number;
  pending_messages: number;
  processing_messages: number;
  completed_messages: number;
  failed_messages: number;
  high_priority_pending: number;
  oldest_pending_age: number;
  average_processing_time: number;
}

// ===== Integration Provider API =====

export async function createIntegrationProvider(data: Partial<IntegrationProvider>) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/providers`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to create integration provider');
  return response.json();
}

export async function getIntegrationProviders(params?: {
  skip?: number;
  limit?: number;
  category?: string;
  is_active?: boolean;
}) {
  const query = new URLSearchParams();
  if (params?.skip) query.set('skip', params.skip.toString());
  if (params?.limit) query.set('limit', params.limit.toString());
  if (params?.category) query.set('category', params.category);
  if (params?.is_active !== undefined) query.set('is_active', params.is_active.toString());
  
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/providers?${query}`);
  if (!response.ok) throw new Error('Failed to fetch integration providers');
  return response.json();
}

export async function getIntegrationProvider(providerId: number) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/providers/${providerId}`);
  if (!response.ok) throw new Error('Failed to fetch integration provider');
  return response.json();
}

export async function getIntegrationProviderByCode(providerCode: string) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/providers/code/${providerCode}`);
  if (!response.ok) throw new Error('Failed to fetch integration provider');
  return response.json();
}

export async function updateIntegrationProvider(providerId: number, data: Partial<IntegrationProvider>) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/providers/${providerId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to update integration provider');
  return response.json();
}

export async function deleteIntegrationProvider(providerId: number) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/providers/${providerId}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete integration provider');
}

// ===== Integration Configuration API =====


export async function createIntegrationConfiguration(data: Partial<IntegrationConfiguration>) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/configurations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to create integration configuration');
  return response.json();
}

export async function getIntegrationConfigurations(params?: {
  skip?: number;
  limit?: number;
  provider_id?: number;
  status?: string;
  environment?: string;
}) {
  const query = new URLSearchParams();
  if (params?.skip) query.set('skip', params.skip.toString());
  if (params?.limit) query.set('limit', params.limit.toString());
  if (params?.provider_id) query.set('provider_id', params.provider_id.toString());
  if (params?.status) query.set('status', params.status);
  if (params?.environment) query.set('environment', params.environment);
  
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/configurations?${query}`);
  if (!response.ok) throw new Error('Failed to fetch integration configurations');
  return response.json();
}

export async function getIntegrationConfiguration(configId: number) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/configurations/${configId}`);
  if (!response.ok) throw new Error('Failed to fetch integration configuration');
  return response.json();
}

export async function updateIntegrationConfiguration(configId: number, data: Partial<IntegrationConfiguration>) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/configurations/${configId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to update integration configuration');
  return response.json();
}

export async function deleteIntegrationConfiguration(configId: number) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/configurations/${configId}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete integration configuration');
}

export async function approveIntegrationConfiguration(configId: number, approvedBy: number) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/configurations/${configId}/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ approved_by: approvedBy }),
  });
  if (!response.ok) throw new Error('Failed to approve integration configuration');
  return response.json();
}

export async function checkConfigurationHealth(configId: number) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/configurations/${configId}/health-check`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to check configuration health');
  return response.json();
}

// ===== Integration Endpoint API =====

export async function createIntegrationEndpoint(data: Partial<IntegrationEndpoint>) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/endpoints`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to create integration endpoint');
  return response.json();
}

export async function getIntegrationEndpoints(params?: {
  skip?: number;
  limit?: number;
  config_id?: number;
  method?: string;
  is_active?: boolean;
}) {
  const query = new URLSearchParams();
  if (params?.skip) query.set('skip', params.skip.toString());
  if (params?.limit) query.set('limit', params.limit.toString());
  if (params?.config_id) query.set('config_id', params.config_id.toString());
  if (params?.method) query.set('method', params.method);
  if (params?.is_active !== undefined) query.set('is_active', params.is_active.toString());
  
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/endpoints?${query}`);
  if (!response.ok) throw new Error('Failed to fetch integration endpoints');
  return response.json();
}

export async function getIntegrationEndpoint(endpointId: number) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/endpoints/${endpointId}`);
  if (!response.ok) throw new Error('Failed to fetch integration endpoint');
  return response.json();
}

export async function updateIntegrationEndpoint(endpointId: number, data: Partial<IntegrationEndpoint>) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/endpoints/${endpointId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to update integration endpoint');
  return response.json();
}

export async function deleteIntegrationEndpoint(endpointId: number) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/endpoints/${endpointId}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete integration endpoint');
}

// ===== Integration Log API =====

export async function createIntegrationLog(data: Partial<IntegrationLog>) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/logs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to create integration log');
  return response.json();
}

export async function getIntegrationLogs(params?: {
  skip?: number;
  limit?: number;
  config_id?: number;
  endpoint_id?: number;
  status?: string;
  start_date?: string;
  end_date?: string;
}) {
  const query = new URLSearchParams();
  if (params?.skip) query.set('skip', params.skip.toString());
  if (params?.limit) query.set('limit', params.limit.toString());
  if (params?.config_id) query.set('config_id', params.config_id.toString());
  if (params?.endpoint_id) query.set('endpoint_id', params.endpoint_id.toString());
  if (params?.status) query.set('status', params.status);
  if (params?.start_date) query.set('start_date', params.start_date);
  if (params?.end_date) query.set('end_date', params.end_date);
  
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/logs?${query}`);
  if (!response.ok) throw new Error('Failed to fetch integration logs');
  return response.json();
}

export async function getIntegrationLog(logId: number) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/logs/${logId}`);
  if (!response.ok) throw new Error('Failed to fetch integration log');
  return response.json();
}


export async function getLogsByCorrelation(correlationId: string) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/logs/correlation/${correlationId}`);
  if (!response.ok) throw new Error('Failed to fetch logs by correlation');
  return response.json();
}

export async function getLogStatistics(params?: {
  start_date?: string;
  end_date?: string;
  config_id?: number;
}) {
  const query = new URLSearchParams();
  if (params?.start_date) query.set('start_date', params.start_date);
  if (params?.end_date) query.set('end_date', params.end_date);
  if (params?.config_id) query.set('config_id', params.config_id.toString());
  
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/logs/statistics/summary?${query}`);
  if (!response.ok) throw new Error('Failed to fetch log statistics');
  return response.json();
}

// ===== API Key API =====

export async function createAPIKey(data: Partial<APIKey>) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/api-keys`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to create API key');
  return response.json();
}

export async function getAPIKeys(params?: {
  skip?: number;
  limit?: number;
  config_id?: number;
  is_active?: boolean;
}) {
  const query = new URLSearchParams();
  if (params?.skip) query.set('skip', params.skip.toString());
  if (params?.limit) query.set('limit', params.limit.toString());
  if (params?.config_id) query.set('config_id', params.config_id.toString());
  if (params?.is_active !== undefined) query.set('is_active', params.is_active.toString());
  
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/api-keys?${query}`);
  if (!response.ok) throw new Error('Failed to fetch API keys');
  return response.json();
}

export async function getAPIKey(keyId: number) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/api-keys/${keyId}`);
  if (!response.ok) throw new Error('Failed to fetch API key');
  return response.json();
}

export async function updateAPIKey(keyId: number, data: Partial<APIKey>) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/api-keys/${keyId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to update API key');
  return response.json();
}

export async function deleteAPIKey(keyId: number) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/api-keys/${keyId}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete API key');
}

export async function revokeAPIKey(keyId: number) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/api-keys/${keyId}/revoke`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to revoke API key');
  return response.json();
}

export async function rotateAPIKey(keyId: number, newKeyValue: string) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/api-keys/${keyId}/rotate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ new_key_value: newKeyValue }),
  });
  if (!response.ok) throw new Error('Failed to rotate API key');
  return response.json();
}

// ===== Webhook API =====

export async function createWebhook(data: Partial<Webhook>) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/webhooks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to create webhook');
  return response.json();
}

export async function getWebhooks(params?: {
  skip?: number;
  limit?: number;
  config_id?: number;
  event_type?: string;
  is_active?: boolean;
}) {
  const query = new URLSearchParams();
  if (params?.skip) query.set('skip', params.skip.toString());
  if (params?.limit) query.set('limit', params.limit.toString());
  if (params?.config_id) query.set('config_id', params.config_id.toString());
  if (params?.event_type) query.set('event_type', params.event_type);
  if (params?.is_active !== undefined) query.set('is_active', params.is_active.toString());
  
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/webhooks?${query}`);
  if (!response.ok) throw new Error('Failed to fetch webhooks');
  return response.json();
}

export async function getWebhook(webhookId: number) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/webhooks/${webhookId}`);
  if (!response.ok) throw new Error('Failed to fetch webhook');
  return response.json();
}

export async function updateWebhook(webhookId: number, data: Partial<Webhook>) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/webhooks/${webhookId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to update webhook');
  return response.json();
}

export async function deleteWebhook(webhookId: number) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/webhooks/${webhookId}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete webhook');
}

export async function testWebhook(webhookId: number, testPayload: any) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/webhooks/${webhookId}/test`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(testPayload),
  });
  if (!response.ok) throw new Error('Failed to test webhook');
  return response.json();
}

// ===== Webhook Delivery API =====

export async function createWebhookDelivery(data: Partial<WebhookDelivery>) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/webhook-deliveries`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to create webhook delivery');
  return response.json();
}

export async function getWebhookDeliveries(params?: {
  skip?: number;
  limit?: number;
  webhook_id?: number;
  status?: string;
  start_date?: string;
  end_date?: string;
}) {
  const query = new URLSearchParams();
  if (params?.skip) query.set('skip', params.skip.toString());
  if (params?.limit) query.set('limit', params.limit.toString());
  if (params?.webhook_id) query.set('webhook_id', params.webhook_id.toString());
  if (params?.status) query.set('status', params.status);
  if (params?.start_date) query.set('start_date', params.start_date);
  if (params?.end_date) query.set('end_date', params.end_date);
  
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/webhook-deliveries?${query}`);
  if (!response.ok) throw new Error('Failed to fetch webhook deliveries');
  return response.json();
}

export async function getWebhookDelivery(deliveryId: number) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/webhook-deliveries/${deliveryId}`);
  if (!response.ok) throw new Error('Failed to fetch webhook delivery');
  return response.json();
}

export async function retryWebhookDelivery(deliveryId: number) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/webhook-deliveries/${deliveryId}/retry`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to retry webhook delivery');
  return response.json();
}

// ===== Message Queue API =====

export async function createMessage(data: Partial<MessageQueue>) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/message-queue`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to create message');
  return response.json();
}

export async function getMessages(params?: {
  skip?: number;
  limit?: number;
  config_id?: number;
  message_type?: string;
  status?: string;
  priority?: string;
}) {
  const query = new URLSearchParams();
  if (params?.skip) query.set('skip', params.skip.toString());
  if (params?.limit) query.set('limit', params.limit.toString());
  if (params?.config_id) query.set('config_id', params.config_id.toString());
  if (params?.message_type) query.set('message_type', params.message_type);
  if (params?.status) query.set('status', params.status);
  if (params?.priority) query.set('priority', params.priority);
  
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/message-queue?${query}`);
  if (!response.ok) throw new Error('Failed to fetch messages');
  return response.json();
}

export async function getMessage(messageId: number) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/message-queue/${messageId}`);
  if (!response.ok) throw new Error('Failed to fetch message');
  return response.json();
}

export async function updateMessage(messageId: number, data: Partial<MessageQueue>) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/message-queue/${messageId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to update message');
  return response.json();
}

export async function processMessage(messageId: number) {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/message-queue/${messageId}/process`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to process message');
  return response.json();
}

export async function getPendingMessages(params?: {
  limit?: number;
  priority?: string;
}) {
  const query = new URLSearchParams();
  if (params?.limit) query.set('limit', params.limit.toString());
  if (params?.priority) query.set('priority', params.priority);
  
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/message-queue/pending/list?${query}`);
  if (!response.ok) throw new Error('Failed to fetch pending messages');
  return response.json();
}

// ===== Statistics and Monitoring API =====

export async function getIntegrationStatistics(params?: {
  start_date?: string;
  end_date?: string;
  provider_id?: number;
}) {
  const query = new URLSearchParams();
  if (params?.start_date) query.set('start_date', params.start_date);
  if (params?.end_date) query.set('end_date', params.end_date);
  if (params?.provider_id) query.set('provider_id', params.provider_id.toString());
  
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/statistics/integration?${query}`);
  if (!response.ok) throw new Error('Failed to fetch integration statistics');
  return response.json();
}

export async function getProviderPerformance(params?: {
  start_date?: string;
  end_date?: string;
}) {
  const query = new URLSearchParams();
  if (params?.start_date) query.set('start_date', params.start_date);
  if (params?.end_date) query.set('end_date', params.end_date);
  
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/statistics/provider-performance?${query}`);
  if (!response.ok) throw new Error('Failed to fetch provider performance');
  return response.json();
}

export async function getWebhookHealth(params?: {
  start_date?: string;
  end_date?: string;
}) {
  const query = new URLSearchParams();
  if (params?.start_date) query.set('start_date', params.start_date);
  if (params?.end_date) query.set('end_date', params.end_date);
  
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/statistics/webhook-health?${query}`);
  if (!response.ok) throw new Error('Failed to fetch webhook health');
  return response.json();
}

export async function getQueueSummary() {
  const response = await fetch(`${API_BASE}/api/v1/gold/integration/statistics/queue-summary`);
  if (!response.ok) throw new Error('Failed to fetch queue summary');
  return response.json();
}
