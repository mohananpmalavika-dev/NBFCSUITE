/**
 * Product Lifecycle Management Service
 * Product variants, promotional products, seasonal products, and product sunset
 */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// =====================================================================
// TYPES & INTERFACES
// =====================================================================

export enum VariantType {
  STANDARD = 'STANDARD',
  PROMOTIONAL = 'PROMOTIONAL',
  SEASONAL = 'SEASONAL',
  GEOGRAPHY_SPECIFIC = 'GEOGRAPHY_SPECIFIC',
  SEGMENT_SPECIFIC = 'SEGMENT_SPECIFIC',
  LIMITED_EDITION = 'LIMITED_EDITION',
  EMPLOYEE_SPECIAL = 'EMPLOYEE_SPECIAL'
}

export enum VariantStatus {
  DRAFT = 'DRAFT',
  ACTIVE = 'ACTIVE',
  INACTIVE = 'INACTIVE',
  EXPIRED = 'EXPIRED',
  DISCONTINUED = 'DISCONTINUED'
}

export enum Season {
  SPRING = 'SPRING',
  SUMMER = 'SUMMER',
  MONSOON = 'MONSOON',
  AUTUMN = 'AUTUMN',
  WINTER = 'WINTER',
  FESTIVE = 'FESTIVE',
  YEAR_END = 'YEAR_END',
  NEW_YEAR = 'NEW_YEAR'
}

export enum CustomerSegment {
  RETAIL = 'RETAIL',
  SALARIED = 'SALARIED',
  SELF_EMPLOYED = 'SELF_EMPLOYED',
  PROFESSIONAL = 'PROFESSIONAL',
  STUDENT = 'STUDENT',
  SENIOR_CITIZEN = 'SENIOR_CITIZEN',
  WOMEN = 'WOMEN',
  RURAL = 'RURAL',
  URBAN = 'URBAN',
  PREMIUM = 'PREMIUM',
  MASS_MARKET = 'MASS_MARKET'
}

export enum SunsetStatus {
  ACTIVE = 'ACTIVE',
  ANNOUNCED = 'ANNOUNCED',
  NO_NEW_APPLICATIONS = 'NO_NEW_APPLICATIONS',
  CLOSED_FOR_NEW = 'CLOSED_FOR_NEW',
  GRANDFATHERED_ONLY = 'GRANDFATHERED_ONLY',
  FULLY_DISCONTINUED = 'FULLY_DISCONTINUED'
}

export enum MigrationStatus {
  NOT_STARTED = 'NOT_STARTED',
  IN_PROGRESS = 'IN_PROGRESS',
  MIGRATED = 'MIGRATED',
  DECLINED = 'DECLINED',
  FAILED = 'FAILED'
}


// Product Variant Interfaces
export interface ProductVariant {
  id: string;
  tenant_id: string;
  base_product_id: string;
  variant_code: string;
  variant_name: string;
  variant_type: VariantType;
  description?: string;
  status: VariantStatus;
  is_active: boolean;
  valid_from: string;
  valid_to?: string;
  interest_rate_override?: {
    base?: number;
    min?: number;
    max?: number;
  };
  tenure_override?: {
    min?: number;
    max?: number;
  };
  amount_override?: {
    min?: number;
    max?: number;
  };
  fee_override?: Record<string, number>;
  eligibility_override?: Record<string, any>;
  priority: number;
  marketing_name?: string;
  tagline?: string;
  promotional_message?: string;
  banner_image_url?: string;
  terms_and_conditions?: string;
  application_count: number;
  disbursement_count: number;
  total_disbursed_amount: number;
  created_at: string;
  updated_at: string;
}

export interface ProductVariantCreate {
  base_product_id: string;
  variant_code: string;
  variant_name: string;
  variant_type: VariantType;
  description?: string;
  valid_from: string;
  valid_to?: string;
  interest_rate_override?: Record<string, any>;
  tenure_override?: Record<string, any>;
  amount_override?: Record<string, any>;
  fee_override?: Record<string, any>;
  eligibility_override?: Record<string, any>;
  priority?: number;
  marketing_name?: string;
  tagline?: string;
  promotional_message?: string;
  terms_and_conditions?: string;
}

export interface ProductVariantUpdate {
  variant_name?: string;
  description?: string;
  status?: VariantStatus;
  valid_to?: string;
  interest_rate_override?: Record<string, any>;
  tenure_override?: Record<string, any>;
  amount_override?: Record<string, any>;
  fee_override?: Record<string, any>;
  priority?: number;
  marketing_name?: string;
  tagline?: string;
  promotional_message?: string;
}

// Promotional Product Interfaces
export interface PromotionalProduct {
  id: string;
  variant_id: string;
  tenant_id: string;
  promotion_code?: string;
  promotion_name: string;
  campaign_name?: string;
  promotion_start_date: string;
  promotion_end_date: string;
  special_rate_discount?: number;
  fee_waiver?: Record<string, number>;
  cashback_amount?: number;
  cashback_percentage?: number;
  max_applications?: number;
  max_disbursement_amount?: number;
  applications_per_customer: number;
  current_applications: number;
  current_disbursement_amount: number;
  min_credit_score?: number;
  min_loan_amount?: number;
  requires_referral_code: boolean;
  auto_approve_eligible: boolean;
  partner_code?: string;
  partner_commission_percentage?: number;
  created_at: string;
  updated_at: string;
}

export interface PromotionalProductCreate {
  promotion_code?: string;
  promotion_name: string;
  campaign_name?: string;
  promotion_start_date: string;
  promotion_end_date: string;
  special_rate_discount?: number;
  fee_waiver?: Record<string, number>;
  cashback_amount?: number;
  cashback_percentage?: number;
  max_applications?: number;
  max_disbursement_amount?: number;
  applications_per_customer?: number;
  min_credit_score?: number;
  min_loan_amount?: number;
  requires_referral_code?: boolean;
  auto_approve_eligible?: boolean;
  partner_code?: string;
  partner_commission_percentage?: number;
}


// Seasonal Product Interfaces
export interface SeasonalProduct {
  id: string;
  variant_id: string;
  tenant_id: string;
  season: Season;
  season_year: number;
  season_start_date: string;
  season_end_date: string;
  seasonal_rate_adjustment?: number;
  seasonal_amount_boost?: number;
  seasonal_tenure_extension?: number;
  festive_bonus?: number;
  holiday_moratorium: boolean;
  moratorium_months?: number;
  target_applications?: number;
  target_disbursement?: number;
  auto_renew_next_year: boolean;
  created_at: string;
  updated_at: string;
}

export interface SeasonalProductCreate {
  season: Season;
  season_year: number;
  season_start_date: string;
  season_end_date: string;
  seasonal_rate_adjustment?: number;
  seasonal_amount_boost?: number;
  seasonal_tenure_extension?: number;
  festive_bonus?: number;
  holiday_moratorium?: boolean;
  moratorium_months?: number;
  target_applications?: number;
  target_disbursement?: number;
  auto_renew_next_year?: boolean;
}

// Geography-Specific Product Interfaces
export interface GeographySpecificProduct {
  id: string;
  variant_id: string;
  tenant_id: string;
  allowed_states?: string[];
  allowed_cities?: string[];
  allowed_pincodes?: string[];
  excluded_areas?: string[];
  is_metro?: boolean;
  is_tier1?: boolean;
  is_tier2?: boolean;
  is_tier3?: boolean;
  is_rural?: boolean;
  regional_rate_adjustment?: number;
  regional_amount_adjustment?: number;
  regional_ltv_adjustment?: number;
  local_regulations?: Record<string, any>;
  requires_local_verification: boolean;
  local_documentation?: string[];
  requires_branch_presence: boolean;
  available_branch_codes?: string[];
  created_at: string;
  updated_at: string;
}

export interface GeographySpecificProductCreate {
  allowed_states?: string[];
  allowed_cities?: string[];
  allowed_pincodes?: string[];
  excluded_areas?: string[];
  is_metro?: boolean;
  is_tier1?: boolean;
  is_tier2?: boolean;
  is_tier3?: boolean;
  is_rural?: boolean;
  regional_rate_adjustment?: number;
  regional_amount_adjustment?: number;
  regional_ltv_adjustment?: number;
  local_regulations?: Record<string, any>;
  requires_local_verification?: boolean;
  local_documentation?: string[];
  requires_branch_presence?: boolean;
  available_branch_codes?: string[];
}

// Segment-Specific Product Interfaces
export interface SegmentSpecificProduct {
  id: string;
  variant_id: string;
  tenant_id: string;
  target_segments: string[];
  min_age?: number;
  max_age?: number;
  min_income?: number;
  max_income?: number;
  employment_types?: string[];
  allowed_industries?: string[];
  allowed_professions?: string[];
  excluded_industries?: string[];
  segment_rate_benefit?: number;
  segment_fee_waiver?: Record<string, number>;
  priority_processing: boolean;
  dedicated_relationship_manager: boolean;
  special_features?: Record<string, boolean>;
  loyalty_benefits?: Record<string, any>;
  referral_bonus?: number;
  max_segment_exposure?: number;
  current_segment_exposure: number;
  created_at: string;
  updated_at: string;
}

export interface SegmentSpecificProductCreate {
  target_segments: string[];
  min_age?: number;
  max_age?: number;
  min_income?: number;
  max_income?: number;
  employment_types?: string[];
  allowed_industries?: string[];
  allowed_professions?: string[];
  excluded_industries?: string[];
  segment_rate_benefit?: number;
  segment_fee_waiver?: Record<string, number>;
  priority_processing?: boolean;
  dedicated_relationship_manager?: boolean;
  special_features?: Record<string, boolean>;
  loyalty_benefits?: Record<string, any>;
  referral_bonus?: number;
  max_segment_exposure?: number;
}


// Product Sunset Interfaces
export interface ProductSunset {
  id: string;
  tenant_id: string;
  product_id: string;
  sunset_reason: string;
  sunset_description?: string;
  sunset_category?: string;
  announcement_date: string;
  no_new_applications_date: string;
  existing_customers_cutoff_date?: string;
  full_discontinuation_date?: string;
  sunset_status: SunsetStatus;
  grandfather_existing_customers: boolean;
  grandfather_in_pipeline: boolean;
  pipeline_cutoff_stage?: string;
  total_active_accounts: number;
  total_outstanding_amount: number;
  applications_in_pipeline: number;
  has_migration_plan: boolean;
  target_product_id?: string;
  auto_migrate_eligible: boolean;
  migration_deadline?: string;
  migration_incentive?: Record<string, any>;
  customer_notification_sent: boolean;
  notification_date?: string;
  notification_channels?: string[];
  customer_support_info?: string;
  faq_document_url?: string;
  customers_notified: number;
  customers_migrated: number;
  customers_remaining: number;
  regulatory_approval_required: boolean;
  regulatory_approval_date?: string;
  regulatory_reference_number?: string;
  created_at: string;
  updated_at: string;
}

export interface ProductSunsetCreate {
  product_id: string;
  sunset_reason: string;
  sunset_description?: string;
  sunset_category?: string;
  announcement_date: string;
  no_new_applications_date: string;
  existing_customers_cutoff_date?: string;
  full_discontinuation_date?: string;
  grandfather_existing_customers?: boolean;
  grandfather_in_pipeline?: boolean;
  pipeline_cutoff_stage?: string;
  has_migration_plan?: boolean;
  target_product_id?: string;
  auto_migrate_eligible?: boolean;
  migration_deadline?: string;
  migration_incentive?: Record<string, any>;
  notification_channels?: string[];
  customer_support_info?: string;
  regulatory_approval_required?: boolean;
}

export interface ProductSunsetUpdate {
  sunset_status?: SunsetStatus;
  no_new_applications_date?: string;
  existing_customers_cutoff_date?: string;
  full_discontinuation_date?: string;
  migration_deadline?: string;
  customer_notification_sent?: boolean;
  notification_date?: string;
  regulatory_approval_date?: string;
  regulatory_reference_number?: string;
}

// Customer Migration Interfaces
export interface CustomerMigration {
  id: string;
  sunset_id: string;
  tenant_id: string;
  customer_id: string;
  old_account_id: string;
  from_product_id: string;
  to_product_id: string;
  migration_status: MigrationStatus;
  eligible_from: string;
  migration_deadline?: string;
  customer_contacted_date?: string;
  customer_consent_date?: string;
  migration_completed_date?: string;
  outstanding_balance?: number;
  new_account_id?: string;
  migration_terms?: Record<string, any>;
  customer_accepted_terms: boolean;
  rate_benefit_offered?: number;
  fee_waiver_offered?: Record<string, number>;
  special_conditions?: Record<string, any>;
  communication_log?: Record<string, any>;
  customer_response?: string;
  decline_reason?: string;
  migration_approved_by?: string;
  approval_date?: string;
  created_at: string;
  updated_at: string;
}

// Eligibility Check Responses
export interface EligibilityResponse {
  eligible: boolean;
  reason?: string;
  benefits?: Record<string, any>;
  adjustments?: Record<string, any>;
  [key: string]: any;
}

// Variant Recommendation
export interface VariantRecommendation {
  variant_id: string;
  variant_code: string;
  variant_name: string;
  variant_type: string;
  marketing_name?: string;
  tagline?: string;
  score: number;
  benefits: string[];
  eligibility_reasons: string[];
  interest_rate_override?: Record<string, any>;
  amount_override?: Record<string, any>;
  tenure_override?: Record<string, any>;
}

// Dashboard Metrics
export interface LifecycleDashboard {
  variants: {
    total: number;
    active: number;
    by_type: Record<string, number>;
    by_status: Record<string, number>;
    total_applications: number;
    total_disbursements: number;
    total_disbursed_amount: number;
  };
  sunsets: {
    total: number;
    by_status: Record<string, number>;
    total_affected_accounts: number;
    total_outstanding: number;
    total_migrations: number;
  };
}

// Variant Performance
export interface VariantPerformance {
  variant_id: string;
  variant_code: string;
  variant_name: string;
  status: string;
  is_active: boolean;
  validity: {
    valid_from: string;
    valid_to?: string;
    days_active: number;
  };
  usage: {
    application_count: number;
    disbursement_count: number;
    total_disbursed_amount: number;
    conversion_rate: number;
    average_disbursement: number;
  };
  promotional?: {
    promotion_name: string;
    current_applications: number;
    max_applications?: number;
    utilization_rate: number;
    current_disbursement: number;
    max_disbursement?: number;
  };
}

// Migration Statistics
export interface MigrationStatistics {
  total_customers: number;
  by_status: Record<string, number>;
  completion_rate: number;
  decline_rate: number;
}


// =====================================================================
// SERVICE CLASS
// =====================================================================

class ProductLifecycleService {
  private getAuthHeaders() {
    const token = localStorage.getItem('token');
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  }

  // =====================================================================
  // PRODUCT VARIANT CRUD
  // =====================================================================

  async createVariant(variantData: ProductVariantCreate): Promise<ProductVariant> {
    const response = await axios.post(
      `${API_BASE_URL}/api/product-lifecycle/variants`,
      variantData,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async listVariants(params?: {
    base_product_id?: string;
    variant_type?: VariantType;
    status?: VariantStatus;
    is_active?: boolean;
    skip?: number;
    limit?: number;
  }): Promise<ProductVariant[]> {
    const response = await axios.get(
      `${API_BASE_URL}/api/product-lifecycle/variants`,
      {
        params,
        headers: this.getAuthHeaders()
      }
    );
    return response.data;
  }

  async getVariant(variantId: string): Promise<ProductVariant> {
    const response = await axios.get(
      `${API_BASE_URL}/api/product-lifecycle/variants/${variantId}`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async updateVariant(
    variantId: string,
    variantData: ProductVariantUpdate
  ): Promise<ProductVariant> {
    const response = await axios.put(
      `${API_BASE_URL}/api/product-lifecycle/variants/${variantId}`,
      variantData,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async activateVariant(variantId: string): Promise<ProductVariant> {
    const response = await axios.post(
      `${API_BASE_URL}/api/product-lifecycle/variants/${variantId}/activate`,
      {},
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async deactivateVariant(variantId: string): Promise<ProductVariant> {
    const response = await axios.post(
      `${API_BASE_URL}/api/product-lifecycle/variants/${variantId}/deactivate`,
      {},
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async deleteVariant(variantId: string): Promise<void> {
    await axios.delete(
      `${API_BASE_URL}/api/product-lifecycle/variants/${variantId}`,
      { headers: this.getAuthHeaders() }
    );
  }

  async cloneVariant(
    variantId: string,
    newCode: string,
    newName: string
  ): Promise<ProductVariant> {
    const response = await axios.post(
      `${API_BASE_URL}/api/product-lifecycle/variants/${variantId}/clone`,
      null,
      {
        params: { new_code: newCode, new_name: newName },
        headers: this.getAuthHeaders()
      }
    );
    return response.data;
  }

  async getVariantPerformance(variantId: string): Promise<VariantPerformance> {
    const response = await axios.get(
      `${API_BASE_URL}/api/product-lifecycle/variants/${variantId}/performance`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  // =====================================================================
  // PROMOTIONAL PRODUCT
  // =====================================================================

  async createPromotionalProduct(
    variantId: string,
    promoData: PromotionalProductCreate
  ): Promise<PromotionalProduct> {
    const response = await axios.post(
      `${API_BASE_URL}/api/product-lifecycle/variants/${variantId}/promotional`,
      promoData,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async getPromotionalProduct(variantId: string): Promise<PromotionalProduct> {
    const response = await axios.get(
      `${API_BASE_URL}/api/product-lifecycle/variants/${variantId}/promotional`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async checkPromotionalEligibility(
    variantId: string,
    customerId: string,
    loanAmount: number,
    creditScore?: number
  ): Promise<EligibilityResponse> {
    const response = await axios.post(
      `${API_BASE_URL}/api/product-lifecycle/variants/${variantId}/promotional/check-eligibility`,
      null,
      {
        params: {
          customer_id: customerId,
          loan_amount: loanAmount,
          credit_score: creditScore
        },
        headers: this.getAuthHeaders()
      }
    );
    return response.data;
  }

  // =====================================================================
  // SEASONAL PRODUCT
  // =====================================================================

  async createSeasonalProduct(
    variantId: string,
    seasonalData: SeasonalProductCreate
  ): Promise<SeasonalProduct> {
    const response = await axios.post(
      `${API_BASE_URL}/api/product-lifecycle/variants/${variantId}/seasonal`,
      seasonalData,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async getSeasonalProduct(variantId: string): Promise<SeasonalProduct> {
    const response = await axios.get(
      `${API_BASE_URL}/api/product-lifecycle/variants/${variantId}/seasonal`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async getActiveSeasonalProducts(season?: Season): Promise<SeasonalProduct[]> {
    const response = await axios.get(
      `${API_BASE_URL}/api/product-lifecycle/seasonal/active`,
      {
        params: { season },
        headers: this.getAuthHeaders()
      }
    );
    return response.data;
  }

  // =====================================================================
  // GEOGRAPHY-SPECIFIC PRODUCT
  // =====================================================================

  async createGeographySpecificProduct(
    variantId: string,
    geoData: GeographySpecificProductCreate
  ): Promise<GeographySpecificProduct> {
    const response = await axios.post(
      `${API_BASE_URL}/api/product-lifecycle/variants/${variantId}/geography`,
      geoData,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async getGeographySpecificProduct(variantId: string): Promise<GeographySpecificProduct> {
    const response = await axios.get(
      `${API_BASE_URL}/api/product-lifecycle/variants/${variantId}/geography`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async checkGeographyEligibility(
    variantId: string,
    state?: string,
    city?: string,
    pincode?: string
  ): Promise<EligibilityResponse> {
    const response = await axios.post(
      `${API_BASE_URL}/api/product-lifecycle/variants/${variantId}/geography/check-eligibility`,
      null,
      {
        params: { state, city, pincode },
        headers: this.getAuthHeaders()
      }
    );
    return response.data;
  }

  // =====================================================================
  // SEGMENT-SPECIFIC PRODUCT
  // =====================================================================

  async createSegmentSpecificProduct(
    variantId: string,
    segmentData: SegmentSpecificProductCreate
  ): Promise<SegmentSpecificProduct> {
    const response = await axios.post(
      `${API_BASE_URL}/api/product-lifecycle/variants/${variantId}/segment`,
      segmentData,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async getSegmentSpecificProduct(variantId: string): Promise<SegmentSpecificProduct> {
    const response = await axios.get(
      `${API_BASE_URL}/api/product-lifecycle/variants/${variantId}/segment`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async checkSegmentEligibility(
    variantId: string,
    customerSegment: string,
    age?: number,
    income?: number,
    employmentType?: string,
    industry?: string
  ): Promise<EligibilityResponse> {
    const response = await axios.post(
      `${API_BASE_URL}/api/product-lifecycle/variants/${variantId}/segment/check-eligibility`,
      null,
      {
        params: {
          customer_segment: customerSegment,
          age,
          income,
          employment_type: employmentType,
          industry
        },
        headers: this.getAuthHeaders()
      }
    );
    return response.data;
  }

  // =====================================================================
  // VARIANT RECOMMENDATIONS
  // =====================================================================

  async getVariantRecommendations(
    baseProductId: string,
    customerData: Record<string, any>
  ): Promise<VariantRecommendation[]> {
    const response = await axios.post(
      `${API_BASE_URL}/api/product-lifecycle/variants/recommend`,
      {
        base_product_id: baseProductId,
        customer_data: customerData
      },
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  // =====================================================================
  // PRODUCT SUNSET
  // =====================================================================

  async createProductSunset(sunsetData: ProductSunsetCreate): Promise<ProductSunset> {
    const response = await axios.post(
      `${API_BASE_URL}/api/product-lifecycle/sunsets`,
      sunsetData,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async listProductSunsets(params?: {
    product_id?: string;
    status?: SunsetStatus;
    skip?: number;
    limit?: number;
  }): Promise<ProductSunset[]> {
    const response = await axios.get(
      `${API_BASE_URL}/api/product-lifecycle/sunsets`,
      {
        params,
        headers: this.getAuthHeaders()
      }
    );
    return response.data;
  }

  async getProductSunset(sunsetId: string): Promise<ProductSunset> {
    const response = await axios.get(
      `${API_BASE_URL}/api/product-lifecycle/sunsets/${sunsetId}`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async updateProductSunset(
    sunsetId: string,
    sunsetData: ProductSunsetUpdate
  ): Promise<ProductSunset> {
    const response = await axios.put(
      `${API_BASE_URL}/api/product-lifecycle/sunsets/${sunsetId}`,
      sunsetData,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async announceSunset(sunsetId: string): Promise<ProductSunset> {
    const response = await axios.post(
      `${API_BASE_URL}/api/product-lifecycle/sunsets/${sunsetId}/announce`,
      {},
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async closeForNewApplications(sunsetId: string): Promise<ProductSunset> {
    const response = await axios.post(
      `${API_BASE_URL}/api/product-lifecycle/sunsets/${sunsetId}/close-new-applications`,
      {},
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async completeSunset(sunsetId: string): Promise<ProductSunset> {
    const response = await axios.post(
      `${API_BASE_URL}/api/product-lifecycle/sunsets/${sunsetId}/complete`,
      {},
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async getSunsetImpactAssessment(sunsetId: string): Promise<Record<string, any>> {
    const response = await axios.get(
      `${API_BASE_URL}/api/product-lifecycle/sunsets/${sunsetId}/impact-assessment`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }


  // =====================================================================
  // CUSTOMER MIGRATION
  // =====================================================================

  async createCustomerMigration(
    sunsetId: string,
    customerId: string,
    oldAccountId: string,
    fromProductId: string,
    toProductId: string,
    migrationTerms?: Record<string, any>
  ): Promise<CustomerMigration> {
    const response = await axios.post(
      `${API_BASE_URL}/api/product-lifecycle/migrations`,
      null,
      {
        params: {
          sunset_id: sunsetId,
          customer_id: customerId,
          old_account_id: oldAccountId,
          from_product_id: fromProductId,
          to_product_id: toProductId,
          migration_terms: migrationTerms ? JSON.stringify(migrationTerms) : undefined
        },
        headers: this.getAuthHeaders()
      }
    );
    return response.data;
  }

  async listCustomerMigrations(params?: {
    sunset_id?: string;
    customer_id?: string;
    migration_status?: MigrationStatus;
    skip?: number;
    limit?: number;
  }): Promise<CustomerMigration[]> {
    const response = await axios.get(
      `${API_BASE_URL}/api/product-lifecycle/migrations`,
      {
        params,
        headers: this.getAuthHeaders()
      }
    );
    return response.data;
  }

  async getCustomerMigration(migrationId: string): Promise<CustomerMigration> {
    const response = await axios.get(
      `${API_BASE_URL}/api/product-lifecycle/migrations/${migrationId}`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async initiateMigration(
    migrationId: string,
    outstandingBalance: number,
    rateBenefit?: number,
    feeWaiver?: Record<string, number>
  ): Promise<CustomerMigration> {
    const response = await axios.post(
      `${API_BASE_URL}/api/product-lifecycle/migrations/${migrationId}/initiate`,
      null,
      {
        params: {
          outstanding_balance: outstandingBalance,
          rate_benefit: rateBenefit,
          fee_waiver: feeWaiver ? JSON.stringify(feeWaiver) : undefined
        },
        headers: this.getAuthHeaders()
      }
    );
    return response.data;
  }

  async completeMigration(
    migrationId: string,
    newAccountId: string
  ): Promise<CustomerMigration> {
    const response = await axios.post(
      `${API_BASE_URL}/api/product-lifecycle/migrations/${migrationId}/complete`,
      null,
      {
        params: { new_account_id: newAccountId },
        headers: this.getAuthHeaders()
      }
    );
    return response.data;
  }

  async declineMigration(
    migrationId: string,
    declineReason: string
  ): Promise<CustomerMigration> {
    const response = await axios.post(
      `${API_BASE_URL}/api/product-lifecycle/migrations/${migrationId}/decline`,
      null,
      {
        params: { decline_reason: declineReason },
        headers: this.getAuthHeaders()
      }
    );
    return response.data;
  }

  async getMigrationStatistics(sunsetId: string): Promise<MigrationStatistics> {
    const response = await axios.get(
      `${API_BASE_URL}/api/product-lifecycle/migrations/statistics/${sunsetId}`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  // =====================================================================
  // ANALYTICS & DASHBOARD
  // =====================================================================

  async getLifecycleDashboard(): Promise<LifecycleDashboard> {
    const response = await axios.get(
      `${API_BASE_URL}/api/product-lifecycle/dashboard`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  // =====================================================================
  // HELPER METHODS
  // =====================================================================

  formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  }

  formatPercentage(value: number, decimals: number = 2): string {
    return `${value.toFixed(decimals)}%`;
  }

  formatDate(dateString?: string): string {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }

  getVariantTypeLabel(type: VariantType): string {
    const labels: Record<VariantType, string> = {
      [VariantType.STANDARD]: 'Standard',
      [VariantType.PROMOTIONAL]: 'Promotional',
      [VariantType.SEASONAL]: 'Seasonal',
      [VariantType.GEOGRAPHY_SPECIFIC]: 'Geography-Specific',
      [VariantType.SEGMENT_SPECIFIC]: 'Segment-Specific',
      [VariantType.LIMITED_EDITION]: 'Limited Edition',
      [VariantType.EMPLOYEE_SPECIAL]: 'Employee Special'
    };
    return labels[type] || type;
  }

  getVariantStatusColor(status: VariantStatus): string {
    switch (status) {
      case VariantStatus.ACTIVE:
        return 'success';
      case VariantStatus.DRAFT:
        return 'default';
      case VariantStatus.INACTIVE:
        return 'warning';
      case VariantStatus.EXPIRED:
        return 'error';
      case VariantStatus.DISCONTINUED:
        return 'error';
      default:
        return 'default';
    }
  }

  getSunsetStatusColor(status: SunsetStatus): string {
    switch (status) {
      case SunsetStatus.ACTIVE:
        return 'success';
      case SunsetStatus.ANNOUNCED:
        return 'info';
      case SunsetStatus.NO_NEW_APPLICATIONS:
        return 'warning';
      case SunsetStatus.CLOSED_FOR_NEW:
        return 'warning';
      case SunsetStatus.GRANDFATHERED_ONLY:
        return 'warning';
      case SunsetStatus.FULLY_DISCONTINUED:
        return 'error';
      default:
        return 'default';
    }
  }

  getMigrationStatusColor(status: MigrationStatus): string {
    switch (status) {
      case MigrationStatus.NOT_STARTED:
        return 'default';
      case MigrationStatus.IN_PROGRESS:
        return 'info';
      case MigrationStatus.MIGRATED:
        return 'success';
      case MigrationStatus.DECLINED:
        return 'warning';
      case MigrationStatus.FAILED:
        return 'error';
      default:
        return 'default';
    }
  }

  getSeasonLabel(season: Season): string {
    const labels: Record<Season, string> = {
      [Season.SPRING]: 'Spring',
      [Season.SUMMER]: 'Summer',
      [Season.MONSOON]: 'Monsoon',
      [Season.AUTUMN]: 'Autumn',
      [Season.WINTER]: 'Winter',
      [Season.FESTIVE]: 'Festive',
      [Season.YEAR_END]: 'Year End',
      [Season.NEW_YEAR]: 'New Year'
    };
    return labels[season] || season;
  }

  getCustomerSegmentLabel(segment: CustomerSegment): string {
    const labels: Record<CustomerSegment, string> = {
      [CustomerSegment.RETAIL]: 'Retail',
      [CustomerSegment.SALARIED]: 'Salaried',
      [CustomerSegment.SELF_EMPLOYED]: 'Self-Employed',
      [CustomerSegment.PROFESSIONAL]: 'Professional',
      [CustomerSegment.STUDENT]: 'Student',
      [CustomerSegment.SENIOR_CITIZEN]: 'Senior Citizen',
      [CustomerSegment.WOMEN]: 'Women',
      [CustomerSegment.RURAL]: 'Rural',
      [CustomerSegment.URBAN]: 'Urban',
      [CustomerSegment.PREMIUM]: 'Premium',
      [CustomerSegment.MASS_MARKET]: 'Mass Market'
    };
    return labels[segment] || segment;
  }

  calculateConversionRate(disbursements: number, applications: number): number {
    if (applications === 0) return 0;
    return (disbursements / applications) * 100;
  }

  calculateUtilizationRate(current: number, max: number): number {
    if (max === 0) return 0;
    return (current / max) * 100;
  }

  isVariantActive(variant: ProductVariant): boolean {
    const today = new Date();
    const validFrom = new Date(variant.valid_from);
    const validTo = variant.valid_to ? new Date(variant.valid_to) : null;

    return (
      variant.is_active &&
      variant.status === VariantStatus.ACTIVE &&
      today >= validFrom &&
      (!validTo || today <= validTo)
    );
  }

  isPromotionActive(promo: PromotionalProduct): boolean {
    const today = new Date();
    const startDate = new Date(promo.promotion_start_date);
    const endDate = new Date(promo.promotion_end_date);

    return today >= startDate && today <= endDate;
  }

  isSeasonActive(seasonal: SeasonalProduct): boolean {
    const today = new Date();
    const startDate = new Date(seasonal.season_start_date);
    const endDate = new Date(seasonal.season_end_date);

    return today >= startDate && today <= endDate;
  }

  getSunsetStatusLabel(status: SunsetStatus): string {
    const labels: Record<SunsetStatus, string> = {
      [SunsetStatus.ACTIVE]: 'Active',
      [SunsetStatus.ANNOUNCED]: 'Announced',
      [SunsetStatus.NO_NEW_APPLICATIONS]: 'No New Applications',
      [SunsetStatus.CLOSED_FOR_NEW]: 'Closed for New',
      [SunsetStatus.GRANDFATHERED_ONLY]: 'Grandfathered Only',
      [SunsetStatus.FULLY_DISCONTINUED]: 'Fully Discontinued'
    };
    return labels[status] || status;
  }

  getMigrationStatusLabel(status: MigrationStatus): string {
    const labels: Record<MigrationStatus, string> = {
      [MigrationStatus.NOT_STARTED]: 'Not Started',
      [MigrationStatus.IN_PROGRESS]: 'In Progress',
      [MigrationStatus.MIGRATED]: 'Migrated',
      [MigrationStatus.DECLINED]: 'Declined',
      [MigrationStatus.FAILED]: 'Failed'
    };
    return labels[status] || status;
  }

  // Validation helpers
  validateVariantCode(code: string): boolean {
    return /^[A-Z0-9-]+$/.test(code);
  }

  validateDateRange(startDate: string, endDate: string): boolean {
    return new Date(startDate) < new Date(endDate);
  }

  validatePercentage(value: number): boolean {
    return value >= 0 && value <= 100;
  }

  validateAmount(value: number): boolean {
    return value > 0;
  }
}

export default new ProductLifecycleService();
