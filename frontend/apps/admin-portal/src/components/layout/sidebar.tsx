'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  LayoutDashboard, 
  Users, 
  Wallet, 
  PiggyBank, 
  TrendingUp,
  Calculator,
  GitBranch,
  Database,
  BarChart3,
  Settings,
  ChevronDown,
  Sparkles,
  Coins,
  Landmark,
  Shield,
  AlertTriangle,
  Activity,
  FileText
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useState } from 'react'

const navigationItems = [
  {
    title: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    title: 'Customers',
    href: '/customers',
    icon: Users,
    children: [
      { title: 'Dashboard', href: '/customers' },
      { title: 'All Customers', href: '/customers/list' },
      { title: 'New Customer', href: '/customers/create' },
    ],
  },
  {
    title: 'Loans',
    href: '/loans',
    icon: Wallet,
    children: [
      { title: 'Applications', href: '/loans/applications' },
      { title: 'Accounts', href: '/loans/accounts' },
      { title: 'Products', href: '/loans/products' },
    ],
  },
  {
    title: 'Deposits',
    href: '/deposits',
    icon: PiggyBank,
    children: [
      { title: 'Accounts', href: '/deposits/accounts' },
      { title: 'Products', href: '/deposits/products' },
    ],
  },
  {
    title: 'Gold Loans',
    href: '/gold-loans',
    icon: Coins,
    children: [
      { title: 'Accounts', href: '/gold-loans' },
      { title: 'Products', href: '/gold-loans/products' },
      { title: 'Releases', href: '/gold-loans/releases' },
    ],
  },
  {
    title: 'Collections',
    href: '/collections',
    icon: TrendingUp,
  },
  {
    title: 'Treasury',
    href: '/treasury',
    icon: Landmark,
    children: [
      { title: 'Dashboard', href: '/treasury/dashboard' },
      { title: 'Bank Accounts', href: '/treasury/bank-accounts' },
      { title: 'Cash Position', href: '/treasury/cash-position' },
      { title: 'Reconciliation', href: '/treasury/reconciliation' },
      { title: 'Fund Transfers', href: '/treasury/fund-transfers' },
      { title: 'ALM (Asset-Liability)', href: '/treasury/alm' },
    ],
  },
  {
    title: 'Workflows',
    href: '/workflows',
    icon: GitBranch,
    children: [
      { title: 'My Tasks', href: '/workflows/tasks' },
      { title: 'Templates', href: '/workflows/templates' },
    ],
  },
  {
    title: 'Accounting',
    href: '/accounting',
    icon: Calculator,
    children: [
      { title: 'Chart of Accounts', href: '/accounting/chart-of-accounts' },
      { title: 'Journal Entries', href: '/accounting/journal-entries' },
      { title: 'TDS Management', href: '/accounting/tds' },
      { title: 'GST Management', href: '/accounting/gst' },
      { title: 'Asset Management', href: '/accounting/assets' },
      { title: 'NPA Management', href: '/accounting/npa' },
      { title: 'Reports', href: '/accounting/reports' },
    ],
  },
  {
    title: 'Risk Management',
    href: '/risk',
    icon: AlertTriangle,
    children: [
      { title: 'Dashboard', href: '/risk' },
      { title: 'Credit Policies', href: '/risk/policies' },
      { title: 'Risk Pricing', href: '/risk/pricing' },
      { title: 'Exposure Limits', href: '/risk/exposure' },
      { title: 'Risk Ratings', href: '/risk/ratings' },
      { title: 'Early Warning Alerts', href: '/risk/alerts' },
    ],
  },
  {
    title: 'Compliance',
    href: '/compliance',
    icon: Shield,
    children: [
      { title: 'SMA Dashboard', href: '/compliance/sma-dashboard' },
      { title: 'Large Credits', href: '/compliance/large-credits' },
      { title: 'SMA Tracking', href: '/compliance/sma-tracking' },
      { title: 'Alerts', href: '/compliance/alerts' },
      { title: 'Quarterly Reports', href: '/compliance/quarterly-reports' },
    ],
  },
  {
    title: 'RBI Returns',
    href: '/rbi-returns',
    icon: FileText,
    children: [
      { title: 'Dashboard', href: '/rbi-returns' },
      { title: 'NBS-7 Returns', href: '/rbi-returns/nbs7' },
      { title: 'Statutory Returns', href: '/rbi-returns/statutory' },
      { title: 'Compliance Calendar', href: '/rbi-returns/calendar' },
      { title: 'XBRL Generation', href: '/rbi-returns/xbrl' },
    ],
  },
  {
    title: 'Reports',
    href: '/reports',
    icon: BarChart3,
  },
  {
    title: 'Master Data',
    href: '/master-data',
    icon: Database,
  },
  {
    title: 'Settings',
    href: '/settings',
    icon: Settings,
  },
]

interface SidebarProps {
  collapsed: boolean
}

export function Sidebar({ collapsed }: SidebarProps) {
  const pathname = usePathname()
  const [expandedItems, setExpandedItems] = useState<string[]>([])

  const toggleExpand = (title: string) => {
    setExpandedItems(prev =>
      prev.includes(title)
        ? prev.filter(item => item !== title)
        : [...prev, title]
    )
  }

  const isActive = (href: string) => {
    if (href === '/dashboard') {
      return pathname === href
    }
    return pathname.startsWith(href)
  }

  return (
    <div
      className={cn(
        'bg-white border-r border-gray-200 flex flex-col transition-all duration-300',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Logo */}
      <div className="h-16 flex items-center justify-center border-b border-gray-200 px-4">
        {collapsed ? (
          <Sparkles className="h-8 w-8 text-blue-600" />
        ) : (
          <div className="flex items-center gap-2">
            <Sparkles className="h-8 w-8 text-blue-600" />
            <span className="text-xl font-bold text-gray-900">NBFC Suite</span>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-4 space-y-1">
        {navigationItems.map((item) => {
          const Icon = item.icon
          const isItemActive = isActive(item.href)
          const isExpanded = expandedItems.includes(item.title)

          return (
            <div key={item.title}>
              {/* Main Item */}
              {item.children ? (
                <button
                  onClick={() => !collapsed && toggleExpand(item.title)}
                  className={cn(
                    'w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                    isItemActive
                      ? 'bg-blue-50 text-blue-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  )}
                >
                  <div className="flex items-center gap-3">
                    <Icon className="h-5 w-5 shrink-0" />
                    {!collapsed && <span>{item.title}</span>}
                  </div>
                  {!collapsed && item.children && (
                    <ChevronDown
                      className={cn(
                        'h-4 w-4 transition-transform',
                        isExpanded && 'transform rotate-180'
                      )}
                    />
                  )}
                </button>
              ) : (
                <Link
                  href={item.href}
                  className={cn(
                    'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                    isItemActive
                      ? 'bg-blue-50 text-blue-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  )}
                  title={collapsed ? item.title : undefined}
                >
                  <Icon className="h-5 w-5 shrink-0" />
                  {!collapsed && <span>{item.title}</span>}
                </Link>
              )}

              {/* Sub Items */}
              {!collapsed && item.children && isExpanded && (
                <div className="ml-8 mt-1 space-y-1">
                  {item.children.map((child) => (
                    <Link
                      key={child.href}
                      href={child.href}
                      className={cn(
                        'block px-3 py-1.5 rounded-lg text-sm transition-colors',
                        pathname === child.href
                          ? 'text-blue-700 bg-blue-50 font-medium'
                          : 'text-gray-600 hover:bg-gray-100'
                      )}
                    >
                      {child.title}
                    </Link>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </nav>

      {/* Footer */}
      {!collapsed && (
        <div className="p-4 border-t border-gray-200">
          <div className="text-xs text-gray-500">
            <p className="font-semibold">NBFC Suite v2.0</p>
            <p className="mt-1">Tier-1 Enterprise Platform</p>
          </div>
        </div>
      )}
    </div>
  )
}
