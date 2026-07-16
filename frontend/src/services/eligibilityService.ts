import api from './api';

class EligibilityService {
  private baseUrl = '/eligibility-rules';

  async createRule(rule: any): Promise<any> {
    const response = await api.post(this.baseUrl, rule);
    return response.data;
  }

  async listRules(filters?: any): Promise<any[]> {
    const response = await api.get(this.baseUrl, { params: filters });
    return response.data;
  }

  async getRule(ruleId: string): Promise<any> {
    const response = await api.get(`${this.baseUrl}/${ruleId}`);
    return response.data;
  }

  async getRuleByCode(ruleCode: string): Promise<any> {
    const response = await api.get(`${this.baseUrl}/by-code/${ruleCode}`);
    return response.data;
  }

  async updateRule(ruleId: string, rule: any): Promise<any> {
    const response = await api.put(`${this.baseUrl}/${ruleId}`, rule);
    return response.data;
  }

  async deleteRule(ruleId: string): Promise<void> {
    await api.delete(`${this.baseUrl}/${ruleId}`);
  }

  async cloneRule(ruleId: string, cloneData: any): Promise<any> {
    const response = await api.post(`${this.baseUrl}/${ruleId}/clone`, cloneData);
    return response.data;
  }

  async activateRule(ruleId: string): Promise<any> {
    const response = await api.post(`${this.baseUrl}/${ruleId}/activate`);
    return response.data;
  }

  async deactivateRule(ruleId: string): Promise<any> {
    const response = await api.post(`${this.baseUrl}/${ruleId}/deactivate`);
    return response.data;
  }

  async checkEligibility(request: any): Promise<any> {
    const response = await api.post(`${this.baseUrl}/check`, request);
    return response.data;
  }

  async bulkCheckEligibility(request: any): Promise<any> {
    const response = await api.post(`${this.baseUrl}/check/bulk`, request);
    return response.data;
  }

  async getStats(): Promise<any> {
    const response = await api.get(`${this.baseUrl}/stats/summary`);
    return response.data;
  }

  async validateRule(rule: any): Promise<any> {
    const response = await api.post(`${this.baseUrl}/validation/validate`, rule);
    return response.data;
  }

  async checkRuleCode(ruleCode: string): Promise<any> {
    const response = await api.get(`${this.baseUrl}/validation/check-code/${ruleCode}`);
    return response.data;
  }
}

export const eligibilityService = new EligibilityService();
