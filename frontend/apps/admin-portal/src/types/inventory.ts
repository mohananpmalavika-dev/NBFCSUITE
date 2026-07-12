/**
 * Inventory & Store Management TypeScript Types
 * Matching backend schemas
 */

// ============================================================================
// Enums
// ============================================================================

export enum ItemType {
  RAW_MATERIAL = "raw_material",
  FINISHED_GOODS = "finished_goods",
  WORK_IN_PROGRESS = "work_in_progress",
  CONSUMABLES = "consumables",
  SPARE_PARTS = "spare_parts",
  TRADING_GOODS = "trading_goods",
  PACKING_MATERIAL = "packing_material",
  TOOLS = "tools",
  ASSETS = "assets",
  OTHER = "other",
}

export enum ItemStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
  DISCONTINUED = "discontinued",
  OBSOLETE = "obsolete",
}

export enum UnitOfMeasure {
  PIECE = "piece",
  KG = "kg",
  GRAM = "gram",
  LITER = "liter",
  MILLILITER = "milliliter",
  METER = "meter",
  CENTIMETER = "centimeter",
  SQUARE_METER = "square_meter",
  CUBIC_METER = "cubic_meter",
  BOX = "box",
  CARTON = "carton",
  PALLET = "pallet",
  DOZEN = "dozen",
  PAIR = "pair",
  SET = "set",
  UNIT = "unit",
}

export enum TransactionType {
  PURCHASE_RECEIPT = "purchase_receipt",
  SALES_ISSUE = "sales_issue",
  STOCK_TRANSFER_IN = "stock_transfer_in",
  STOCK_TRANSFER_OUT = "stock_transfer_out",
  STOCK_ADJUSTMENT_IN = "stock_adjustment_in",
  STOCK_ADJUSTMENT_OUT = "stock_adjustment_out",
  PRODUCTION_RECEIPT = "production_receipt",
  PRODUCTION_ISSUE = "production_issue",
  RETURN_FROM_CUSTOMER = "return_from_customer",
  RETURN_TO_SUPPLIER = "return_to_supplier",
  OPENING_STOCK = "opening_stock",
  PHYSICAL_VERIFICATION = "physical_verification",
  DAMAGE = "damage",
  WASTAGE = "wastage",
  THEFT = "theft",
}


export enum TransactionStatus {
  DRAFT = "draft",
  SUBMITTED = "submitted",
  APPROVED = "approved",
  REJECTED = "rejected",
  POSTED = "posted",
  CANCELLED = "cancelled",
}

export enum ValuationMethod {
  FIFO = "fifo",
  LIFO = "lifo",
  WEIGHTED_AVERAGE = "weighted_average",
  MOVING_AVERAGE = "moving_average",
  STANDARD_COST = "standard_cost",
  SPECIFIC_IDENTIFICATION = "specific_identification",
}

export enum VerificationStatus {
  PLANNED = "planned",
  IN_PROGRESS = "in_progress",
  COMPLETED = "completed",
  VARIANCE_FOUND = "variance_found",
  RECONCILED = "reconciled",
  CANCELLED = "cancelled",
}

// ============================================================================
// Item Master Types
// ============================================================================

export interface ItemMaster {
  id: string;
  tenant_id: number;
  item_code: string;
  item_name: string;
  item_description?: string;
  item_type: ItemType;
  item_status: ItemStatus;
  
  // Category
  category?: string;
  sub_category?: string;
  brand?: string;
  manufacturer?: string;
  
  // Unit
  base_unit: UnitOfMeasure;
  alternate_unit?: UnitOfMeasure;
  conversion_factor: number;
  
  // Barcode & SKU
  barcode?: string;
  sku?: string;
  hsn_code?: string;
  
  // Pricing
  standard_cost: number;
  average_cost: number;
  last_purchase_price: number;
  selling_price: number;
  
  // Stock Levels
  minimum_stock: number;
  maximum_stock: number;
  reorder_level: number;
  reorder_quantity: number;
  
  // Current Stock
  current_stock: number;
  reserved_stock: number;
  available_stock: number;
  
  // Valuation
  valuation_method: ValuationMethod;
  total_value: number;
  
  // Storage
  warehouse_location?: string;
  rack_number?: string;
  bin_number?: string;
  
  // Supplier
  preferred_supplier_id?: string;
  lead_time_days: number;
  
  // Tax
  is_taxable: boolean;
  gst_rate: number;
  
  // Tracking
  is_batch_tracked: boolean;
  is_serial_tracked: boolean;
  is_expiry_tracked: boolean;
  shelf_life_days?: number;
  
  // Additional
  specification?: string;
  remarks?: string;
  image_url?: string;
  
  // Audit
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
}

export interface ItemMasterFormData {
  item_code?: string;
  item_name: string;
  item_description?: string;
  item_type: ItemType;
  item_status: ItemStatus;
  category?: string;
  sub_category?: string;
  brand?: string;
  manufacturer?: string;
  base_unit: UnitOfMeasure;
  alternate_unit?: UnitOfMeasure;
  conversion_factor?: number;
  barcode?: string;
  sku?: string;
  hsn_code?: string;
  standard_cost?: number;
  selling_price?: number;
  minimum_stock?: number;
  maximum_stock?: number;
  reorder_level?: number;
  reorder_quantity?: number;
  valuation_method: ValuationMethod;
  warehouse_location?: string;
  rack_number?: string;
  bin_number?: string;
  preferred_supplier_id?: string;
  lead_time_days?: number;
  is_taxable?: boolean;
  gst_rate?: number;
  is_batch_tracked?: boolean;
  is_serial_tracked?: boolean;
  is_expiry_tracked?: boolean;
  shelf_life_days?: number;
  specification?: string;
  remarks?: string;
  image_url?: string;
}


// ============================================================================
// Stock Transaction Types
// ============================================================================

export interface StockTransaction {
  id: string;
  tenant_id: number;
  transaction_number: string;
  transaction_date: string;
  transaction_type: TransactionType;
  transaction_status: TransactionStatus;
  
  item_id: string;
  quantity: number;
  unit: UnitOfMeasure;
  rate: number;
  amount: number;
  
  // Location
  from_warehouse?: string;
  to_warehouse?: string;
  from_location?: string;
  to_location?: string;
  
  // Batch & Serial
  batch_number?: string;
  serial_number?: string;
  expiry_date?: string;
  
  // Reference
  reference_type?: string;
  reference_number?: string;
  reference_id?: string;
  
  // Purpose
  purpose?: string;
  remarks?: string;
  
  // Approval
  approved_by?: string;
  approved_at?: string;
  rejection_reason?: string;
  
  // Posting
  is_posted: boolean;
  posted_at?: string;
  posted_by?: string;
  
  // Audit
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
}

export interface StockTransactionFormData {
  transaction_date: string;
  transaction_type: TransactionType;
  item_id: string;
  quantity: number;
  unit: UnitOfMeasure;
  rate: number;
  from_warehouse?: string;
  to_warehouse?: string;
  from_location?: string;
  to_location?: string;
  batch_number?: string;
  serial_number?: string;
  expiry_date?: string;
  reference_type?: string;
  reference_number?: string;
  reference_id?: string;
  purpose?: string;
  remarks?: string;
}

// ============================================================================
// Stock Verification Types
// ============================================================================

export interface StockVerificationItem {
  id: string;
  verification_id: string;
  item_id: string;
  
  system_quantity: number;
  system_rate: number;
  system_value: number;
  
  physical_quantity?: number;
  physical_rate?: number;
  physical_value?: number;
  
  variance_quantity: number;
  variance_value: number;
  variance_percentage: number;
  
  is_verified: boolean;
  has_variance: boolean;
  
  batch_number?: string;
  serial_number?: string;
  
  is_reconciled: boolean;
  reconciliation_notes?: string;
  reconciled_by?: string;
  reconciled_at?: string;
  
  verified_at?: string;
  verified_by?: string;
  remarks?: string;
}

export interface StockVerification {
  id: string;
  tenant_id: number;
  verification_number: string;
  verification_date: string;
  verification_status: VerificationStatus;
  
  scheduled_date: string;
  completed_date?: string;
  
  warehouse?: string;
  location?: string;
  item_category?: string;
  
  verification_team?: string;
  supervisor_id?: string;
  supervisor_name?: string;
  
  total_items: number;
  items_verified: number;
  items_with_variance: number;
  total_variance_value: number;
  
  purpose?: string;
  remarks?: string;
  
  items: StockVerificationItem[];
  
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
}

export interface StockVerificationFormData {
  verification_date: string;
  scheduled_date: string;
  warehouse?: string;
  location?: string;
  item_category?: string;
  supervisor_id?: string;
  supervisor_name?: string;
  purpose?: string;
  remarks?: string;
  items: Array<{
    item_id: string;
    system_quantity: number;
    physical_quantity?: number;
    batch_number?: string;
    serial_number?: string;
    remarks?: string;
  }>;
}


// ============================================================================
// Inventory Valuation Types
// ============================================================================

export interface InventoryValuationItem {
  id: string;
  valuation_id: string;
  item_id: string;
  item_code: string;
  item_name: string;
  item_type: ItemType;
  quantity: number;
  unit: UnitOfMeasure;
  rate: number;
  value: number;
  valuation_method: ValuationMethod;
  warehouse?: string;
  location?: string;
  batch_number?: string;
  serial_number?: string;
}

export interface InventoryValuation {
  id: string;
  tenant_id: number;
  valuation_number: string;
  valuation_date: string;
  financial_year: number;
  financial_period?: string;
  
  warehouse?: string;
  item_category?: string;
  item_type?: ItemType;
  valuation_method: ValuationMethod;
  
  total_items: number;
  total_quantity: number;
  total_value: number;
  
  raw_material_value: number;
  finished_goods_value: number;
  wip_value: number;
  consumables_value: number;
  other_value: number;
  
  is_finalized: boolean;
  finalized_at?: string;
  finalized_by?: string;
  
  remarks?: string;
  
  items: InventoryValuationItem[];
  
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
}

export interface InventoryValuationFormData {
  valuation_date: string;
  financial_year: number;
  financial_period?: string;
  warehouse?: string;
  item_category?: string;
  item_type?: ItemType;
  valuation_method: ValuationMethod;
  remarks?: string;
}

// ============================================================================
// Dashboard & Reports Types
// ============================================================================

export interface InventoryDashboardMetrics {
  total_items: number;
  active_items: number;
  total_stock_value: number;
  low_stock_items: number;
  out_of_stock_items: number;
  pending_transactions: number;
  pending_verifications: number;
  raw_material_value: number;
  finished_goods_value: number;
  wip_value: number;
  consumables_value: number;
  transactions_today: number;
  transactions_this_week: number;
  transactions_this_month: number;
}

export interface StockLedgerEntry {
  transaction_date: string;
  transaction_number: string;
  transaction_type: TransactionType;
  opening_quantity: number;
  in_quantity: number;
  out_quantity: number;
  closing_quantity: number;
  rate: number;
  opening_value: number;
  in_value: number;
  out_value: number;
  closing_value: number;
}

export interface LowStockAlert {
  item_id: string;
  item_code: string;
  item_name: string;
  current_stock: number;
  minimum_stock: number;
  reorder_level: number;
  reorder_quantity: number;
  unit: UnitOfMeasure;
  warehouse_location?: string;
  preferred_supplier_id?: string;
  lead_time_days: number;
}

// ============================================================================
// API Response Types
// ============================================================================

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
