/**
 * Facility & Administration Management Types
 */

// ============================================================================
// BUILDING MANAGEMENT TYPES
// ============================================================================

export interface Building {
  id: number;
  tenant_id: string;
  building_code: string;
  building_name: string;
  building_type: 'office' | 'warehouse' | 'factory' | 'retail' | 'residential' | 'mixed_use';
  status: 'active' | 'under_construction' | 'maintenance' | 'inactive';
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  pincode?: string;
  total_floors: number;
  total_area_sqft?: number;
  built_year?: number;
  has_elevator: boolean;
  has_parking: boolean;
  parking_capacity: number;
  contact_number?: string;
  created_at: string;
  updated_at?: string;
}

export interface Floor {
  id: number;
  building_id: number;
  floor_number: number;
  floor_name?: string;
  floor_area_sqft?: number;
  total_rooms: number;
  has_restroom: boolean;
  has_pantry: boolean;
  created_at: string;
}

export interface Room {
  id: number;
  building_id: number;
  floor_id: number;
  room_number: string;
  room_name?: string;
  room_type: 'office' | 'conference_room' | 'cabin' | 'cubicle' | 'meeting_room' | 'cafeteria' | 'restroom' | 'storage' | 'server_room' | 'reception' | 'lobby' | 'pantry' | 'other';
  status: 'available' | 'occupied' | 'under_maintenance' | 'reserved' | 'out_of_service';
  area_sqft?: number;
  seating_capacity?: number;
  has_ac: boolean;
  has_projector: boolean;
  created_at: string;
}

// ============================================================================
// HOUSEKEEPING TYPES
// ============================================================================

export interface HousekeepingTask {
  id: number;
  task_code: string;
  task_type: string;
  task_name: string;
  building_id: number;
  floor_id?: number;
  room_id?: number;
  scheduled_date: string;
  scheduled_time?: string;
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled' | 'on_hold';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  assigned_to_employee_id?: number;
  completed_at?: string;
  description?: string;
  created_at: string;
}

export interface HousekeepingSupply {
  id: number;
  item_code: string;
  item_name: string;
  category: string;
  unit_of_measure: string;
  current_stock: number;
  minimum_stock: number;
  reorder_quantity: number;
  unit_price: number;
  supplier_name: string;
}

// ============================================================================
// CAFETERIA TYPES
// ============================================================================

export interface MenuItem {
  id: number;
  item_code: string;
  item_name: string;
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snacks' | 'beverages';
  category: string;
  price: number;
  employee_price?: number;
  is_available: boolean;
  is_vegetarian: boolean;
  calories?: number;
  image_url?: string;
  created_at: string;
}

export interface OrderItem {
  menu_item_id: number;
  quantity: number;
  special_instructions?: string;
}

export interface CafeteriaOrder {
  id: number;
  order_number: string;
  order_date: string;
  order_time: string;
  employee_id: number;
  employee_name: string;
  meal_type: string;
  status: 'pending' | 'confirmed' | 'preparing' | 'ready' | 'served' | 'cancelled';
  total_amount: number;
  net_amount: number;
  delivery_location?: string;
  created_at: string;
}

// ============================================================================
// TRANSPORT TYPES
// ============================================================================

export interface Vehicle {
  id: number;
  vehicle_number: string;
  vehicle_type: 'car' | 'suv' | 'van' | 'bus' | 'truck' | 'two_wheeler';
  make_model?: string;
  seating_capacity?: number;
  status: 'available' | 'in_use' | 'maintenance' | 'out_of_service';
  current_mileage_km: number;
  fuel_type?: string;
  ownership: string;
  created_at: string;
}

export interface Trip {
  id: number;
  trip_number: string;
  vehicle_id: number;
  driver_id: number;
  trip_date: string;
  start_location: string;
  end_location: string;
  purpose?: string;
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  passenger_count: number;
  distance_km?: number;
  created_at: string;
}

export interface VehicleMaintenance {
  id: number;
  maintenance_code: string;
  vehicle_id: number;
  maintenance_type: string;
  scheduled_date: string;
  actual_date?: string;
  service_provider: string;
  total_cost: number;
  work_description: string;
}

// ============================================================================
// VISITOR MANAGEMENT TYPES
// ============================================================================

export interface Visitor {
  id: number;
  visitor_pass_number: string;
  visitor_name: string;
  visitor_type: 'customer' | 'vendor' | 'candidate' | 'contractor' | 'guest' | 'official' | 'other';
  company_name?: string;
  mobile_number: string;
  email?: string;
  purpose: 'meeting' | 'interview' | 'delivery' | 'maintenance' | 'training' | 'audit' | 'inspection' | 'other';
  host_employee_id: number;
  host_employee_name: string;
  visit_date: string;
  status: 'scheduled' | 'checked_in' | 'in_meeting' | 'checked_out' | 'cancelled';
  check_in_time?: string;
  check_out_time?: string;
  badge_number?: string;
  created_at: string;
}

// ============================================================================
// API RESPONSE TYPES
// ============================================================================

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: {
    code: string;
    message: string;
  };
}

// ============================================================================
// FORM TYPES
// ============================================================================

export interface BuildingFormData {
  building_code: string;
  building_name: string;
  building_type: string;
  status?: string;
  address_line1?: string;
  city?: string;
  state?: string;
  pincode?: string;
  total_area_sqft?: number;
  contact_number?: string;
}

export interface FloorFormData {
  floor_number: number;
  floor_name?: string;
  floor_area_sqft?: number;
  has_restroom?: boolean;
  has_pantry?: boolean;
}

export interface RoomFormData {
  room_number: string;
  room_name?: string;
  room_type: string;
  status?: string;
  area_sqft?: number;
  seating_capacity?: number;
}

export interface TaskFormData {
  task_type: string;
  task_name: string;
  building_id: number;
  floor_id?: number;
  room_id?: number;
  scheduled_date: string;
  scheduled_time?: string;
  priority?: string;
  description?: string;
}

export interface MenuItemFormData {
  item_code: string;
  item_name: string;
  meal_type: string;
  category?: string;
  price: number;
  employee_price?: number;
  is_vegetarian?: boolean;
}

export interface OrderFormData {
  employee_id: number;
  meal_type: string;
  delivery_location?: string;
  items: OrderItem[];
}

export interface VehicleFormData {
  vehicle_number: string;
  vehicle_type: string;
  make_model?: string;
  seating_capacity?: number;
  fuel_type?: string;
  ownership?: string;
}

export interface TripFormData {
  vehicle_id: number;
  driver_id: number;
  trip_date: string;
  start_location: string;
  end_location: string;
  purpose?: string;
  passenger_count?: number;
}

export interface VisitorFormData {
  visitor_name: string;
  visitor_type: string;
  company_name?: string;
  mobile_number: string;
  email?: string;
  purpose: string;
  host_employee_id: number;
  visit_date: string;
  expected_in_time?: string;
  id_proof_type?: string;
  id_proof_number?: string;
}
