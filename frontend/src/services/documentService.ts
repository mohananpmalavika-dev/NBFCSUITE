import api from './api';

export interface DocumentChecklist {
  id?: string;
  checklist_code: string;
  checklist_name: string;
  description: string;
  status: string;
  product_id?: string;
  product_code?: string;
  apply_to_all_products: boolean;
  requirements: DocumentRequirement[];
  effective_date: string;
  expiry_date?: string;
  priority: number;
}

export interface DocumentRequirement {
  id?: string;
  document_type: string;
  document_name: string;
  template_id?: string;
  mandatory: boolean;
  conditional: boolean;
  conditional_rule?: ConditionalRule;
  customer_types: string[];
  min_count: number;
  max_count: number;
  check_validity: boolean;
  validity_days?: number;
  instructions?: string;
  display_order: number;
}

export interface ConditionalRule {
  conditions: DocumentCondition[];
  logic: 'AND' | 'OR';
}

export interface DocumentCondition {
  field: string;
  operator: string;
  value: any;
}

export interface DocumentTemplate {
  id?: string;
  template_code: string;
  template_name: string;
  document_type: string;
  allowed_formats: string[];
  max_file_size_mb: number;
  ocr_fields: OCRField[];
  verification_checklist?: any;
  status: string;
}

export interface OCRField {
  field_name: string;
  field_type: string;
  required: boolean;
  validation_regex?: string;
}

export interface EvaluationContext {
  customer_type: string;
  employment_type?: string;
  loan_amount?: number;
  loan_type?: string;
  custom_fields?: Record<string, any>;
}

class DocumentService {
  private baseUrl = '/document-checklists';

  // Checklist CRUD
  async createChecklist(checklist: DocumentChecklist): Promise<DocumentChecklist> {
    const response = await api.post(this.baseUrl, checklist);
    return response.data;
  }

  async listChecklists(filters?: any): Promise<DocumentChecklist[]> {
    const response = await api.get(this.baseUrl, { params: filters });
    return response.data;
  }

  async getChecklist(checklistId: string): Promise<DocumentChecklist> {
    const response = await api.get(`${this.baseUrl}/${checklistId}`);
    return response.data;
  }

  async getChecklistByCode(checklistCode: string): Promise<DocumentChecklist> {
    const response = await api.get(`${this.baseUrl}/by-code/${checklistCode}`);
    return response.data;
  }

  async updateChecklist(checklistId: string, checklist: Partial<DocumentChecklist>): Promise<DocumentChecklist> {
    const response = await api.put(`${this.baseUrl}/${checklistId}`, checklist);
    return response.data;
  }

  async deleteChecklist(checklistId: string): Promise<void> {
    await api.delete(`${this.baseUrl}/${checklistId}`);
  }

  // Checklist operations
  async cloneChecklist(checklistId: string, cloneData: any): Promise<DocumentChecklist> {
    const response = await api.post(`${this.baseUrl}/${checklistId}/clone`, cloneData);
    return response.data;
  }

  async activateChecklist(checklistId: string): Promise<DocumentChecklist> {
    const response = await api.post(`${this.baseUrl}/${checklistId}/activate`);
    return response.data;
  }

  async deactivateChecklist(checklistId: string): Promise<DocumentChecklist> {
    const response = await api.post(`${this.baseUrl}/${checklistId}/deactivate`);
    return response.data;
  }

  // Evaluation
  async evaluateChecklist(checklistId: string, context: EvaluationContext): Promise<any> {
    const response = await api.post(`${this.baseUrl}/${checklistId}/evaluate`, context);
    return response.data;
  }

  // Templates
  async createTemplate(template: DocumentTemplate): Promise<DocumentTemplate> {
    const response = await api.post(`${this.baseUrl}/templates`, template);
    return response.data;
  }

  async listTemplates(filters?: any): Promise<DocumentTemplate[]> {
    const response = await api.get(`${this.baseUrl}/templates`, { params: filters });
    return response.data;
  }

  async getTemplate(templateId: string): Promise<DocumentTemplate> {
    const response = await api.get(`${this.baseUrl}/templates/${templateId}`);
    return response.data;
  }

  async updateTemplate(templateId: string, template: Partial<DocumentTemplate>): Promise<DocumentTemplate> {
    const response = await api.put(`${this.baseUrl}/templates/${templateId}`, template);
    return response.data;
  }

  async deleteTemplate(templateId: string): Promise<void> {
    await api.delete(`${this.baseUrl}/templates/${templateId}`);
  }

  // Statistics
  async getStats(): Promise<any> {
    const response = await api.get(`${this.baseUrl}/stats/summary`);
    return response.data;
  }

  // Validation
  async validateChecklist(checklist: any): Promise<any> {
    const response = await api.post(`${this.baseUrl}/validation/validate`, checklist);
    return response.data;
  }

  async checkChecklistCode(checklistCode: string): Promise<any> {
    const response = await api.get(`${this.baseUrl}/validation/check-code/${checklistCode}`);
    return response.data;
  }
}

export const documentService = new DocumentService();
