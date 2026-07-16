import api from './api';

export interface Product {
  id?: string;
  product_code: string;
  product_name: string;
  category: string;
  description: string;
  status: string;
  effective_date: string;
  expiry_date?: string;
  interest_config: any;
  tenure_config: any;
  amount_config: any;
  fees_config: any;
  emi_config: any;
  eligibility_criteria?: any;
  document_requirements?: any[];
  is_featured: boolean;
}

export interface ProductFilter {
  category?: string;
  status?: string;
  is_featured?: boolean;
  min_amount?: number;
  max_amount?: number;
  effective_date_from?: string;
  effective_date_to?: string;
}

export interface ProductClone {
  new_product_code: string;
  new_product_name?: string;
}

export interface ProductCalculation {
  loan_amount: number;
  tenure_months: number;
  custom_rate?: number;
}

export interface ProductStats {
  total_products: number;
  active_products: number;
  draft_products: number;
  featured_products: number;
  total_categories: number;
}

class ProductsService {
  private baseUrl = '/products';

  async createProduct(product: Product): Promise<Product> {
    const response = await api.post(this.baseUrl, product);
    return response.data;
  }

  async listProducts(filters?: ProductFilter): Promise<Product[]> {
    const params = new URLSearchParams();
    if (filters?.category) params.append('category', filters.category);
    if (filters?.status) params.append('status', filters.status);
    if (filters?.is_featured !== undefined) params.append('is_featured', String(filters.is_featured));
    if (filters?.min_amount) params.append('min_amount', String(filters.min_amount));
    if (filters?.max_amount) params.append('max_amount', String(filters.max_amount));
    if (filters?.effective_date_from) params.append('effective_date_from', filters.effective_date_from);
    if (filters?.effective_date_to) params.append('effective_date_to', filters.effective_date_to);

    const queryString = params.toString();
    const url = queryString ? `${this.baseUrl}?${queryString}` : this.baseUrl;
    const response = await api.get(url);
    return response.data;
  }

  async getProduct(productId: string): Promise<Product> {
    const response = await api.get(`${this.baseUrl}/${productId}`);
    return response.data;
  }

  async getProductByCode(productCode: string): Promise<Product> {
    const response = await api.get(`${this.baseUrl}/by-code/${productCode}`);
    return response.data;
  }

  async updateProduct(productId: string, product: Partial<Product>): Promise<Product> {
    const response = await api.put(`${this.baseUrl}/${productId}`, product);
    return response.data;
  }

  async deleteProduct(productId: string): Promise<void> {
    await api.delete(`${this.baseUrl}/${productId}`);
  }

  async cloneProduct(productId: string, cloneData: ProductClone): Promise<Product> {
    const response = await api.post(`${this.baseUrl}/${productId}/clone`, cloneData);
    return response.data;
  }

  async activateProduct(productId: string): Promise<Product> {
    const response = await api.post(`${this.baseUrl}/${productId}/activate`);
    return response.data;
  }

  async deactivateProduct(productId: string): Promise<Product> {
    const response = await api.post(`${this.baseUrl}/${productId}/deactivate`);
    return response.data;
  }

  async calculateEMI(productId: string, calculation: ProductCalculation): Promise<any> {
    const response = await api.post(`${this.baseUrl}/${productId}/calculate`, calculation);
    return response.data;
  }

  async getCategories(): Promise<string[]> {
    const response = await api.get(`${this.baseUrl}/categories/list`);
    return response.data;
  }

  async getStats(): Promise<ProductStats> {
    const response = await api.get(`${this.baseUrl}/stats/summary`);
    return response.data;
  }

  async checkProductCode(productCode: string): Promise<{ available: boolean; message: string }> {
    const response = await api.get(`${this.baseUrl}/validation/check-code/${productCode}`);
    return response.data;
  }

  // Helper methods for formatting
  formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  }

  formatPercentage(value: number): string {
    return `${value.toFixed(2)}%`;
  }

  calculateProcessingFee(amount: number, feeConfig: any): number {
    if (!feeConfig) return 0;

    let fee = 0;
    if (feeConfig.charge_type === 'FLAT') {
      fee = feeConfig.flat_amount || 0;
    } else if (feeConfig.charge_type === 'PERCENTAGE') {
      fee = (amount * (feeConfig.percentage || 0)) / 100;
      if (feeConfig.min_amount && fee < feeConfig.min_amount) {
        fee = feeConfig.min_amount;
      }
      if (feeConfig.max_amount && fee > feeConfig.max_amount) {
        fee = feeConfig.max_amount;
      }
    }

    if (feeConfig.gst_applicable) {
      fee = fee * 1.18; // Add 18% GST
    }

    return fee;
  }

  validateProductData(product: Product): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!product.product_code) {
      errors.push('Product code is required');
    }

    if (!product.product_name) {
      errors.push('Product name is required');
    }

    if (!product.category) {
      errors.push('Product category is required');
    }

    if (!product.effective_date) {
      errors.push('Effective date is required');
    }

    // Interest config validation
    if (product.interest_config) {
      if (!product.interest_config.calculation_method) {
        errors.push('Interest calculation method is required');
      }
      if (!product.interest_config.base_rate || product.interest_config.base_rate <= 0) {
        errors.push('Valid base interest rate is required');
      }
      if (product.interest_config.min_rate && product.interest_config.max_rate) {
        if (product.interest_config.min_rate > product.interest_config.max_rate) {
          errors.push('Minimum rate cannot be greater than maximum rate');
        }
      }
    } else {
      errors.push('Interest configuration is required');
    }

    // Tenure config validation
    if (product.tenure_config) {
      if (!product.tenure_config.min_tenure || product.tenure_config.min_tenure <= 0) {
        errors.push('Valid minimum tenure is required');
      }
      if (!product.tenure_config.max_tenure || product.tenure_config.max_tenure <= 0) {
        errors.push('Valid maximum tenure is required');
      }
      if (product.tenure_config.min_tenure > product.tenure_config.max_tenure) {
        errors.push('Minimum tenure cannot be greater than maximum tenure');
      }
    } else {
      errors.push('Tenure configuration is required');
    }

    // Amount config validation
    if (product.amount_config) {
      if (!product.amount_config.min_amount || product.amount_config.min_amount <= 0) {
        errors.push('Valid minimum amount is required');
      }
      if (!product.amount_config.max_amount || product.amount_config.max_amount <= 0) {
        errors.push('Valid maximum amount is required');
      }
      if (product.amount_config.min_amount > product.amount_config.max_amount) {
        errors.push('Minimum amount cannot be greater than maximum amount');
      }
      if (product.amount_config.enable_ltv && !product.amount_config.max_ltv_percentage) {
        errors.push('Maximum LTV percentage is required when LTV is enabled');
      }
    } else {
      errors.push('Amount configuration is required');
    }

    // EMI config validation
    if (!product.emi_config) {
      errors.push('EMI configuration is required');
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  getProductSummary(product: Product): string {
    const { interest_config, tenure_config, amount_config } = product;
    return `${this.formatCurrency(amount_config.min_amount)} - ${this.formatCurrency(amount_config.max_amount)} | ${tenure_config.min_tenure}-${tenure_config.max_tenure} months | ${interest_config.base_rate}% p.a.`;
  }
}

export const productsService = new ProductsService();
