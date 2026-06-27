// CIF API Integration Layer
import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1';

interface SearchRequest {
  mobile_number?: string;
  aadhar_number?: string;
  pan_number?: string;
  email?: string;
  customer_id?: string;
}

interface SearchResponse {
  found: boolean;
  customer_id?: string;
  customer_name?: string;
  mobile?: string;
  email?: string;
  status?: string;
}

interface ProspectRequest {
  first_name: string;
  last_name: string;
  phone: string;
  email: string;
  source?: string;
  campaign?: string;
  branch_id?: string;
}

interface ProspectResponse {
  prospect_id: string;
  status: string;
  created_at: string;
}

interface BasicDetailsRequest {
  customer_type?: string;
  first_name: string;
  middle_name?: string;
  last_name: string;
  date_of_birth: string;
  gender: string;
  marital_status?: string;
  occupation?: string;
  education_level?: string;
  nationality?: string;
  resident_status?: string;
  company_name?: string;
  industry?: string;
  mother_name?: string;
  father_name?: string;
  pan?: string;
  aadhar?: string;
  passport?: string;
}

interface AddressRequest {
  address_type: string;
  street_line1: string;
  street_line2?: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  latitude?: number;
  longitude?: number;
  is_primary?: boolean;
}

interface ContactRequest {
  phone: string;
  email: string;
  whatsapp?: string;
  emergency_contact?: string;
  preferred_language?: string;
}

interface IdentityDocumentRequest {
  document_type: string;
  document_number: string;
  issue_date?: string;
  expiry_date?: string;
  document_file: File;
}

interface EmploymentRequest {
  employment_type: string;
  employer_name?: string;
  designation?: string;
  salary?: number;
  joining_date?: string;
  experience_years?: number;
}

interface FinancialProfileRequest {
  monthly_income?: number;
  monthly_expense?: number;
  annual_savings?: number;
  total_assets?: number;
  total_liabilities?: number;
  credit_score?: number;
}

interface BankingProfileRequest {
  primary_bank_account?: string;
  primary_bank_ifsc?: string;
  primary_bank_name?: string;
  primary_account_type?: string;
  average_balance?: number;
}

interface DocumentRequest {
  document_type: string;
  document_title: string;
  document_file: File;
  expiry_date?: string;
}

interface ApprovalInitiateRequest {
  initiated_by: string;
  notes?: string;
}

interface ApprovalRequest {
  workflow_instance_id: string;
  action: string;
  actor_id: string;
  actor_role: string;
  approved: boolean;
  comments?: string;
}

interface Customer360Response {
  customer_id: string;
  cif_id?: string;
  status: string;
  basic_details: any;
  addresses: any[];
  contacts: any;
  documents: any[];
  compliance: any;
  behavior_profile?: any;
  relationships: any[];
  approval_status: string;
}

class CIFApi {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth token to requests
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  // Stage 1: Customer Search
  async searchCustomer(params: SearchRequest): Promise<SearchResponse> {
    try {
      const payload = {
        mobile_number: params.mobile_number,
        aadhar: params.aadhar_number,
        pan: params.pan_number,
        email: params.email,
        customer_id: params.customer_id,
      };
      const response = await this.api.post('/search', payload);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async searchFuzzy(params: SearchRequest): Promise<SearchResponse[]> {
    try {
      const response = await this.api.get('/search/fuzzy', {
        params: {
          name: params.mobile_number || params.email || params.customer_id || params.pan_number || params.aadhar_number,
        },
      });
      return response.data.potential_duplicates || [];
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Stage 2: Prospect Creation
  async createProspect(data: ProspectRequest): Promise<ProspectResponse> {
    try {
      const response = await this.api.post('/prospect', data);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getProspect(prospectId: string): Promise<any> {
    try {
      const response = await this.api.get(`/prospect/${prospectId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async convertProspectToCustomer(prospectId: string): Promise<any> {
    try {
      const response = await this.api.post(`/prospect/${prospectId}/convert`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Stage 3: Basic Details
  async addBasicDetails(customerId: string, data: BasicDetailsRequest): Promise<any> {
    try {
      const payload = {
        customer_type: data.customer_type || 'individual',
        first_name: data.first_name,
        middle_name: data.middle_name,
        last_name: data.last_name,
        date_of_birth: data.date_of_birth,
        gender: data.gender,
        marital_status: data.marital_status,
        occupation: data.occupation,
        education_level: data.education_level,
        nationality: data.nationality,
        resident_status: data.resident_status,
        company_name: data.company_name,
        industry: data.industry,
      };
      const response = await this.api.post(`/customer/${customerId}/basic-details`, payload);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Stage 4: Identity Documents
  async addIdentityDocument(customerId: string, data: IdentityDocumentRequest): Promise<any> {
    try {
      const formData = new FormData();
      formData.append('document_type', data.document_type);
      formData.append('file', data.document_file);
      if (data.document_number) formData.append('document_number', data.document_number);
      if (data.expiry_date) formData.append('expiry_date', data.expiry_date);

      const response = await this.api.post(`/customer/${customerId}/identity-document`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Stage 5: Address
  async addAddress(customerId: string, data: AddressRequest): Promise<any> {
    try {
      const payload = {
        address_type: data.address_type,
        street_line1: data.street_line1,
        street_line2: data.street_line2,
        city: data.city,
        state: data.state,
        postal_code: data.postal_code,
        country: data.country,
        latitude: data.latitude,
        longitude: data.longitude,
        is_primary: data.is_primary,
      };
      const response = await this.api.post(`/customer/${customerId}/address`, payload);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getAddresses(customerId: string): Promise<any[]> {
    try {
      const response = await this.api.get(`/customer/${customerId}/addresses`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Stage 6: Contacts
  async addContact(customerId: string, data: ContactRequest): Promise<any> {
    try {
      const payload = {
        mobile_primary: data.phone,
        mobile_alternate: undefined,
        email_primary: data.email,
        email_alternate: undefined,
        whatsapp_number: data.whatsapp,
        emergency_contact_name: undefined,
        emergency_contact_mobile: undefined,
        preferred_contact_method: 'mobile',
        preferred_language: data.preferred_language || 'en',
      };
      const response = await this.api.post(`/customer/${customerId}/contact`, payload);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Stage 8: Employment
  async addEmployment(customerId: string, data: EmploymentRequest): Promise<any> {
    try {
      const payload = {
        employment_type: data.employment_type,
        employer_name: data.employer_name,
        designation: data.designation,
        current_salary: data.salary,
        salary_frequency: 'monthly',
        years_in_current_job: data.experience_years,
        total_years_experience: data.experience_years,
      };
      const response = await this.api.post(`/customer/${customerId}/employment`, payload);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Stage 10: Financial Profile
  async addFinancialProfile(customerId: string, data: FinancialProfileRequest): Promise<any> {
    try {
      const payload = {
        annual_income: data.monthly_income ? data.monthly_income * 12 : undefined,
        monthly_income: data.monthly_income,
        monthly_expenses: data.monthly_expense,
        total_assets: data.total_assets,
        total_liabilities: data.total_liabilities,
        credit_score: data.credit_score,
      };
      const response = await this.api.post(`/customer/${customerId}/financial-profile`, payload);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Stage 11: Banking Profile
  async addBankingProfile(customerId: string, data: BankingProfileRequest): Promise<any> {
    try {
      const payload = {
        primary_bank_account_number: data.primary_bank_account,
        primary_bank_ifsc: data.primary_bank_ifsc,
        primary_bank_name: data.primary_bank_name,
        primary_account_type: data.primary_account_type,
        average_balance: data.average_balance,
      };
      const response = await this.api.post(`/customer/${customerId}/banking-profile`, payload);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Stage 15: Documents
  async addDocument(customerId: string, data: DocumentRequest): Promise<any> {
    try {
      const formData = new FormData();
      formData.append('file', data.document_file);
      if (data.expiry_date) formData.append('expiry_date', data.expiry_date);

      const response = await this.api.post(
        `/customer/${customerId}/document`,
        formData,
        {
          params: {
            document_category: data.document_type,
            document_type: data.document_type,
            document_title: data.document_title,
            uploaded_by: 'system',
          },
          headers: { 'Content-Type': 'multipart/form-data' },
        }
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getDocuments(customerId: string): Promise<any[]> {
    try {
      const response = await this.api.get(`/customer/${customerId}/documents`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Stage 12: Compliance
  async initiateCompliance(customerId: string): Promise<any> {
    try {
      const response = await this.api.post(`/customer/${customerId}/compliance/initiate`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async verifyPan(customerId: string): Promise<any> {
    try {
      const response = await this.api.post(`/customer/${customerId}/compliance/verify-pan`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async verifyAadhar(customerId: string): Promise<any> {
    try {
      const response = await this.api.post(`/customer/${customerId}/compliance/verify-aadhar`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async runAmlCheck(customerId: string): Promise<any> {
    try {
      const response = await this.api.post(`/customer/${customerId}/compliance/run-aml`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Stage 13: Behavior Analysis
  async analyzeBehavior(customerId: string): Promise<any> {
    try {
      const response = await this.api.post(`/customer/${customerId}/analyze-behavior`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Stage 16: Approval Workflow
  async initiateApproval(customerId: string, data: ApprovalInitiateRequest): Promise<any> {
    try {
      const response = await this.api.post(
        `/customer/${customerId}/approval/initiate`,
        undefined,
        {
          params: { initiated_by: data.initiated_by },
        }
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async transitionApproval(customerId: string, data: ApprovalRequest): Promise<any> {
    try {
      const response = await this.api.post(
        `/customer/${customerId}/approval/${data.workflow_instance_id}/transition`,
        { approved: data.approved, comments: data.comments },
        {
          params: {
            action: data.action,
            actor_id: data.actor_id,
            actor_role: data.actor_role,
          },
        }
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Stage 14: Relationship Mapping
  async linkRelationship(
    customerId: string,
    relatedCustomerId: string,
    relationshipType: string
  ): Promise<any> {
    try {
      const response = await this.api.post(
        `/customer/${customerId}/relationship/${relatedCustomerId}`,
        undefined,
        {
          params: { relationship_type: relationshipType },
        }
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getRelationshipNetwork(customerId: string): Promise<any> {
    try {
      const response = await this.api.get(`/customer/${customerId}/network`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Stage 18: Customer 360
  async getCustomer360(customerId: string): Promise<Customer360Response> {
    try {
      const response = await this.api.get(`/customer/${customerId}/360`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Progress tracking
  async getOnboardingProgress(customerId: string): Promise<any> {
    try {
      const response = await this.api.get(`/customer/${customerId}/onboarding-progress`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  private handleError(error: any): Error {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.detail || error.message;
      return new Error(message);
    }
    return error;
  }
}

export const cifApi = new CIFApi();
