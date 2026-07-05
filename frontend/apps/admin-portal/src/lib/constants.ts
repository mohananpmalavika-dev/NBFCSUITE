/**
 * Application constants
 */

// Navigation
export const NAVIGATION_ITEMS = [
  {
    title: 'Dashboard',
    href: '/dashboard',
    icon: 'LayoutDashboard',
  },
  {
    title: 'Customers',
    href: '/customers',
    icon: 'Users',
  },
  {
    title: 'Loans',
    href: '/loans',
    icon: 'Wallet',
    children: [
      {
        title: 'Applications',
        href: '/loans/applications',
      },
      {
        title: 'Accounts',
        href: '/loans/accounts',
      },
      {
        title: 'Products',
        href: '/loans/products',
      },
    ],
  },
  {
    title: 'Deposits',
    href: '/deposits',
    icon: 'PiggyBank',
    children: [
      {
        title: 'Accounts',
        href: '/deposits/accounts',
      },
      {
        title: 'Products',
        href: '/deposits/products',
      },
    ],
  },
  {
    title: 'Collections',
    href: '/collections',
    icon: 'TrendingUp',
  },
  {
    title: 'Accounting',
    href: '/accounting',
    icon: 'Calculator',
    children: [
      {
        title: 'Chart of Accounts',
        href: '/accounting/chart-of-accounts',
      },
      {
        title: 'Journal Entries',
        href: '/accounting/journal-entries',
      },
      {
        title: 'Reports',
        href: '/accounting/reports',
      },
    ],
  },
  {
    title: 'Workflows',
    href: '/workflows',
    icon: 'GitBranch',
    children: [
      {
        title: 'My Tasks',
        href: '/workflows/tasks',
      },
      {
        title: 'Templates',
        href: '/workflows/templates',
      },
    ],
  },
  {
    title: 'Master Data',
    href: '/master-data',
    icon: 'Database',
  },
  {
    title: 'Reports',
    href: '/reports',
    icon: 'BarChart3',
  },
  {
    title: 'Settings',
    href: '/settings',
    icon: 'Settings',
  },
]

// Application Status
export const APPLICATION_STATUS = {
  DRAFT: 'Draft',
  SUBMITTED: 'Submitted',
  UNDER_REVIEW: 'Under Review',
  APPROVED: 'Approved',
  REJECTED: 'Rejected',
  CANCELLED: 'Cancelled',
} as const

// Loan Status
export const LOAN_STATUS = {
  ACTIVE: 'Active',
  CLOSED: 'Closed',
  WRITTEN_OFF: 'Written Off',
  NPA: 'NPA',
} as const

// Account Status
export const ACCOUNT_STATUS = {
  ACTIVE: 'Active',
  INACTIVE: 'Inactive',
  BLOCKED: 'Blocked',
  CLOSED: 'Closed',
} as const

// KYC Status
export const KYC_STATUS = {
  PENDING: 'Pending',
  VERIFIED: 'Verified',
  REJECTED: 'Rejected',
} as const

// Gender Options
export const GENDER_OPTIONS = [
  { value: 'Male', label: 'Male' },
  { value: 'Female', label: 'Female' },
  { value: 'Other', label: 'Other' },
]

// Marital Status Options
export const MARITAL_STATUS_OPTIONS = [
  { value: 'Single', label: 'Single' },
  { value: 'Married', label: 'Married' },
  { value: 'Divorced', label: 'Divorced' },
  { value: 'Widowed', label: 'Widowed' },
]

// Address Type Options
export const ADDRESS_TYPE_OPTIONS = [
  { value: 'Permanent', label: 'Permanent' },
  { value: 'Current', label: 'Current' },
  { value: 'Office', label: 'Office' },
]

// Payment Mode Options
export const PAYMENT_MODE_OPTIONS = [
  { value: 'Cash', label: 'Cash' },
  { value: 'Cheque', label: 'Cheque' },
  { value: 'NEFT', label: 'NEFT' },
  { value: 'RTGS', label: 'RTGS' },
  { value: 'IMPS', label: 'IMPS' },
  { value: 'UPI', label: 'UPI' },
  { value: 'Online', label: 'Online' },
]

// Deposit Type Options
export const DEPOSIT_TYPE_OPTIONS = [
  { value: 'Savings', label: 'Savings Account' },
  { value: 'Fixed', label: 'Fixed Deposit' },
  { value: 'Recurring', label: 'Recurring Deposit' },
  { value: 'MIS', label: 'Monthly Income Scheme' },
]

// Notification Channel Options
export const NOTIFICATION_CHANNEL_OPTIONS = [
  { value: 'SMS', label: 'SMS' },
  { value: 'Email', label: 'Email' },
  { value: 'WhatsApp', label: 'WhatsApp' },
]

// Priority Options
export const PRIORITY_OPTIONS = [
  { value: 'high', label: 'High' },
  { value: 'medium', label: 'Medium' },
  { value: 'low', label: 'Low' },
]

// Pagination
export const DEFAULT_PAGE_SIZE = 20
export const PAGE_SIZE_OPTIONS = [10, 20, 50, 100]

// Date Formats
export const DATE_FORMAT = 'dd MMM yyyy'
export const DATE_TIME_FORMAT = 'dd MMM yyyy, hh:mm a'
export const API_DATE_FORMAT = 'yyyy-MM-dd'

// Currency
export const CURRENCY_SYMBOL = '₹'
export const CURRENCY_CODE = 'INR'

// Validation Patterns
export const PATTERNS = {
  PAN: /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/,
  AADHAAR: /^\d{12}$/,
  MOBILE: /^[6-9]\d{9}$/,
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PINCODE: /^\d{6}$/,
}

// Error Messages
export const ERROR_MESSAGES = {
  REQUIRED: 'This field is required',
  INVALID_EMAIL: 'Please enter a valid email address',
  INVALID_MOBILE: 'Please enter a valid 10-digit mobile number',
  INVALID_PAN: 'Please enter a valid PAN number (e.g., ABCDE1234F)',
  INVALID_AADHAAR: 'Please enter a valid 12-digit Aadhaar number',
  INVALID_PINCODE: 'Please enter a valid 6-digit pincode',
  MIN_AMOUNT: 'Amount must be greater than minimum',
  MAX_AMOUNT: 'Amount exceeds maximum limit',
  MIN_LENGTH: 'Minimum length not met',
  MAX_LENGTH: 'Maximum length exceeded',
}
