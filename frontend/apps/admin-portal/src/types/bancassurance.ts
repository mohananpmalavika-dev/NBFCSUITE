/**
 * Bancassurance Module Types
 * Shared types and enums for Insurance & Bancassurance
 */

export enum PolicyType {
  LIFE = 'life',
  HEALTH = 'health',
  GENERAL = 'general',
  MOTOR = 'motor',
  ENDOWMENT = 'endowment',
  TERM = 'term',
  ULIP = 'ulip',
  PENSION = 'pension',
}

export enum PolicyStatus {
  DRAFT = 'draft',
  ACTIVE = 'active',
  LAPSED = 'lapsed',
  SURRENDERED = 'surrendered',
  MATURED = 'matured',
  CANCELLED = 'cancelled',
}

export enum PremiumFrequency {
  MONTHLY = 'monthly',
  QUARTERLY = 'quarterly',
  HALF_YEARLY = 'half_yearly',
  ANNUALLY = 'annually',
  SINGLE = 'single',
}

export enum PremiumStatus {
  DUE = 'due',
  PAID = 'paid',
  OVERDUE = 'overdue',
  WAIVED = 'waived',
  CANCELLED = 'cancelled',
}

export enum ClaimType {
  DEATH = 'death',
  MATURITY = 'maturity',
  SURRENDER = 'surrender',
  HEALTH = 'health',
  ACCIDENT = 'accident',
  DAMAGE = 'damage',
  THEFT = 'theft',
  OTHER = 'other',
}

export enum ClaimStatus {
  REGISTERED = 'registered',
  UNDER_REVIEW = 'under_review',
  DOCUMENTS_PENDING = 'documents_pending',
  ASSESSMENT_COMPLETE = 'assessment_complete',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  SETTLED = 'settled',
  CANCELLED = 'cancelled',
}

export enum CommissionType {
  FIRST_YEAR = 'first_year',
  RENEWAL = 'renewal',
  PERFORMANCE = 'performance',
}

export enum CommissionStatus {
  PENDING = 'pending',
  CALCULATED = 'calculated',
  APPROVED = 'approved',
  PAID = 'paid',
  CANCELLED = 'cancelled',
}

export enum PaymentMethod {
  CASH = 'cash',
  CHEQUE = 'cheque',
  ONLINE = 'online',
  NEFT = 'neft',
  RTGS = 'rtgs',
  UPI = 'upi',
}

// Display labels
export const POLICY_TYPE_LABELS: Record<PolicyType, string> = {
  [PolicyType.LIFE]: 'Life Insurance',
  [PolicyType.HEALTH]: 'Health Insurance',
  [PolicyType.GENERAL]: 'General Insurance',
  [PolicyType.MOTOR]: 'Motor Insurance',
  [PolicyType.ENDOWMENT]: 'Endowment Policy',
  [PolicyType.TERM]: 'Term Insurance',
  [PolicyType.ULIP]: 'ULIP',
  [PolicyType.PENSION]: 'Pension Plan',
}

export const POLICY_STATUS_LABELS: Record<PolicyStatus, string> = {
  [PolicyStatus.DRAFT]: 'Draft',
  [PolicyStatus.ACTIVE]: 'Active',
  [PolicyStatus.LAPSED]: 'Lapsed',
  [PolicyStatus.SURRENDERED]: 'Surrendered',
  [PolicyStatus.MATURED]: 'Matured',
  [PolicyStatus.CANCELLED]: 'Cancelled',
}

export const PREMIUM_FREQUENCY_LABELS: Record<PremiumFrequency, string> = {
  [PremiumFrequency.MONTHLY]: 'Monthly',
  [PremiumFrequency.QUARTERLY]: 'Quarterly',
  [PremiumFrequency.HALF_YEARLY]: 'Half-Yearly',
  [PremiumFrequency.ANNUALLY]: 'Annually',
  [PremiumFrequency.SINGLE]: 'Single Premium',
}

export const PREMIUM_STATUS_LABELS: Record<PremiumStatus, string> = {
  [PremiumStatus.DUE]: 'Due',
  [PremiumStatus.PAID]: 'Paid',
  [PremiumStatus.OVERDUE]: 'Overdue',
  [PremiumStatus.WAIVED]: 'Waived',
  [PremiumStatus.CANCELLED]: 'Cancelled',
}

export const CLAIM_TYPE_LABELS: Record<ClaimType, string> = {
  [ClaimType.DEATH]: 'Death Claim',
  [ClaimType.MATURITY]: 'Maturity Claim',
  [ClaimType.SURRENDER]: 'Surrender',
  [ClaimType.HEALTH]: 'Health Claim',
  [ClaimType.ACCIDENT]: 'Accident',
  [ClaimType.DAMAGE]: 'Damage',
  [ClaimType.THEFT]: 'Theft',
  [ClaimType.OTHER]: 'Other',
}

export const CLAIM_STATUS_LABELS: Record<ClaimStatus, string> = {
  [ClaimStatus.REGISTERED]: 'Registered',
  [ClaimStatus.UNDER_REVIEW]: 'Under Review',
  [ClaimStatus.DOCUMENTS_PENDING]: 'Documents Pending',
  [ClaimStatus.ASSESSMENT_COMPLETE]: 'Assessment Complete',
  [ClaimStatus.APPROVED]: 'Approved',
  [ClaimStatus.REJECTED]: 'Rejected',
  [ClaimStatus.SETTLED]: 'Settled',
  [ClaimStatus.CANCELLED]: 'Cancelled',
}

export const COMMISSION_TYPE_LABELS: Record<CommissionType, string> = {
  [CommissionType.FIRST_YEAR]: 'First Year',
  [CommissionType.RENEWAL]: 'Renewal',
  [CommissionType.PERFORMANCE]: 'Performance',
}

export const COMMISSION_STATUS_LABELS: Record<CommissionStatus, string> = {
  [CommissionStatus.PENDING]: 'Pending',
  [CommissionStatus.CALCULATED]: 'Calculated',
  [CommissionStatus.APPROVED]: 'Approved',
  [CommissionStatus.PAID]: 'Paid',
  [CommissionStatus.CANCELLED]: 'Cancelled',
}

// Status colors for badges
export const POLICY_STATUS_COLORS: Record<PolicyStatus, string> = {
  [PolicyStatus.DRAFT]: 'gray',
  [PolicyStatus.ACTIVE]: 'green',
  [PolicyStatus.LAPSED]: 'orange',
  [PolicyStatus.SURRENDERED]: 'purple',
  [PolicyStatus.MATURED]: 'blue',
  [PolicyStatus.CANCELLED]: 'red',
}

export const PREMIUM_STATUS_COLORS: Record<PremiumStatus, string> = {
  [PremiumStatus.DUE]: 'yellow',
  [PremiumStatus.PAID]: 'green',
  [PremiumStatus.OVERDUE]: 'red',
  [PremiumStatus.WAIVED]: 'gray',
  [PremiumStatus.CANCELLED]: 'gray',
}

export const CLAIM_STATUS_COLORS: Record<ClaimStatus, string> = {
  [ClaimStatus.REGISTERED]: 'blue',
  [ClaimStatus.UNDER_REVIEW]: 'yellow',
  [ClaimStatus.DOCUMENTS_PENDING]: 'orange',
  [ClaimStatus.ASSESSMENT_COMPLETE]: 'purple',
  [ClaimStatus.APPROVED]: 'green',
  [ClaimStatus.REJECTED]: 'red',
  [ClaimStatus.SETTLED]: 'green',
  [ClaimStatus.CANCELLED]: 'gray',
}

export const COMMISSION_STATUS_COLORS: Record<CommissionStatus, string> = {
  [CommissionStatus.PENDING]: 'gray',
  [CommissionStatus.CALCULATED]: 'blue',
  [CommissionStatus.APPROVED]: 'green',
  [CommissionStatus.PAID]: 'green',
  [CommissionStatus.CANCELLED]: 'red',
}

// Helper functions
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(new Date(date))
}

export function formatDateTime(date: string | Date): string {
  return new Intl.DateTimeFormat('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date))
}

export function getDaysRemaining(dueDate: string): number {
  const today = new Date()
  const due = new Date(dueDate)
  const diff = due.getTime() - today.getTime()
  return Math.ceil(diff / (1000 * 60 * 60 * 24))
}

export function isOverdue(dueDate: string): boolean {
  return getDaysRemaining(dueDate) < 0
}
