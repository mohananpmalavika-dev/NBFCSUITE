'use client'

import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { 
  Shield, AlertTriangle, TrendingUp, Users, 
  FileText, Activity, ArrowRight, DollarSign 
} from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { riskService } from '@/services/risk.service'

export default function RiskManagementDashboard() {
  const { data: summary, isLoading } = useQuery({
    queryKey: ['risk-dashboard-summary'],
    queryFn: () => riskService.getDashboardSummary(),
  })

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <Shield className="h-8 w-8 text-blue-600" />
            Risk Management & Credit Policy
          </h1>
          <p className="text-gray-600 mt-1">
            Comprehensive risk management, credit policies, and portfolio monitoring
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatCard
            title="Total Rated Customers"
            value={summary?.risk_ratings?.total_rated_customers || 0}
            icon={Users}
            color="blue"
            isLoading={isLoading}
          />
          <StatCard
            title="High Risk Customers"
            value={summary?.risk_ratings?.high_risk_count || 0}
            subtitle={`${summary?.risk_ratings?.high_risk_percentage?.toFixed(1) || 0}%`}
            icon={AlertTriangle}
            color="red"
            isLoading={isLoading}
          />
          <StatCard
            title="Open Alerts"
            value={summary?.early_warning_alerts?.open_alerts || 0}
            subtitle={`${summary?.early_warning_alerts?.critical_alerts || 0} critical`}
            icon={Activity}
            color="yellow"
            isLoading={isLoading}
          />
          <StatCard
            title="Breached Limits"
            value={summary?.exposure_limits?.breached_limits || 0}
            subtitle={`of ${summary?.exposure_limits?.total_limits || 0} limits`}
            icon={DollarSign}
            color="orange"
            isLoading={isLoading}
          />
        </div>

        {/* Main Modules */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <ModuleCard
            title="Credit Policies"
            description="Define and manage credit policies with eligibility criteria"
            icon={FileText}
            href="/risk/policies"
            color="blue"
            features={[
              'Credit score requirements',
              'DTI & income criteria',
              'Product applicability',
              'Policy evaluation'
            ]}
          />

          <ModuleCard
            title="Risk-Based Pricing"
            description="Configure dynamic pricing rules based on risk factors"
            icon={TrendingUp}
            href="/risk/pricing"
            color="green"
            features={[
              'Risk-adjusted rates',
              'Multi-factor rules',
              'Fee adjustments',
              'Incentives & discounts'
            ]}
          />

          <ModuleCard
            title="Exposure Limits"
            description="Monitor and manage concentration risk across portfolio"
            icon={DollarSign}
            href="/risk/exposure"
            color="purple"
            features={[
              'Customer/group limits',
              'Industry exposure',
              'Geographic limits',
              'Breach alerts'
            ]}
          />

          <ModuleCard
            title="Risk Ratings"
            description="Assess and track customer risk profiles"
            icon={Shield}
            href="/risk/ratings"
            color="indigo"
            features={[
              'Scorecard-based rating',
              'PD/LGD/EAD metrics',
              'Portfolio analytics',
              'Rating overrides'
            ]}
          />

          <ModuleCard
            title="Early Warning Signals"
            description="Proactive monitoring and alert management"
            icon={AlertTriangle}
            href="/risk/alerts"
            color="red"
            features={[
              'Signal configuration',
              'Automatic detection',
              'Alert workflow',
              'Escalation management'
            ]}
          />

          <ModuleCard
            title="Risk Analytics"
            description="Comprehensive risk reporting and insights"
            icon={Activity}
            href="/risk/analytics"
            color="cyan"
            features={[
              'Portfolio distribution',
              'Trend analysis',
              'Compliance reports',
              'Executive dashboards'
            ]}
          />
        </div>

        {/* Risk Rating Distribution */}
        {summary?.risk_ratings && (
          <Card>
            <CardHeader>
              <CardTitle>Risk Rating Distribution</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-7 gap-4">
                {Object.entries(summary.risk_ratings.rating_distribution).map(([grade, count]) => (
                  <div key={grade} className="text-center">
                    <div className={`text-2xl font-bold ${getRatingColor(grade)}`}>
                      {count}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">{grade}</div>
                  </div>
                ))}
              </div>
              <div className="mt-4 text-sm text-gray-600">
                Average Risk Score: {summary.risk_ratings.average_score?.toFixed(0) || 'N/A'}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  )
}

function StatCard({ 
  title, 
  value, 
  subtitle,
  icon: Icon, 
  color,
  isLoading 
}: { 
  title: string
  value: number | string
  subtitle?: string
  icon: any
  color: string
  isLoading?: boolean
}) {
  const colors = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    red: 'bg-red-100 text-red-600',
    purple: 'bg-purple-100 text-purple-600',
    orange: 'bg-orange-100 text-orange-600',
    indigo: 'bg-indigo-100 text-indigo-600',
    cyan: 'bg-cyan-100 text-cyan-600',
  }

  if (isLoading) {
    return (
      <Card>
        <CardContent className="pt-6">
          <Skeleton className="h-20 w-full" />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600 mb-1">{title}</p>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
            {subtitle && (
              <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
            )}
          </div>
          <div className={`h-12 w-12 rounded-lg ${colors[color as keyof typeof colors]} flex items-center justify-center`}>
            <Icon className="h-6 w-6" />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function ModuleCard({
  title,
  description,
  icon: Icon,
  href,
  color,
  features
}: {
  title: string
  description: string
  icon: any
  href: string
  color: string
  features: string[]
}) {
  const colors = {
    blue: 'bg-blue-50 text-blue-600 border-blue-200',
    green: 'bg-green-50 text-green-600 border-green-200',
    purple: 'bg-purple-50 text-purple-600 border-purple-200',
    indigo: 'bg-indigo-50 text-indigo-600 border-indigo-200',
    red: 'bg-red-50 text-red-600 border-red-200',
    cyan: 'bg-cyan-50 text-cyan-600 border-cyan-200',
  }

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardContent className="pt-6">
        <div className={`h-12 w-12 rounded-lg ${colors[color as keyof typeof colors]} border flex items-center justify-center mb-4`}>
          <Icon className="h-6 w-6" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
        <p className="text-sm text-gray-600 mb-4">{description}</p>
        <ul className="space-y-2 mb-4">
          {features.map((feature, index) => (
            <li key={index} className="text-sm text-gray-600 flex items-center gap-2">
              <div className="h-1.5 w-1.5 rounded-full bg-gray-400" />
              {feature}
            </li>
          ))}
        </ul>
        <Link href={href}>
          <Button className="w-full" variant="outline">
            Open Module
            <ArrowRight className="h-4 w-4 ml-2" />
          </Button>
        </Link>
      </CardContent>
    </Card>
  )
}

function getRatingColor(grade: string): string {
  const colors: Record<string, string> = {
    'A+': 'text-green-600',
    'A': 'text-green-500',
    'B+': 'text-blue-600',
    'B': 'text-blue-500',
    'C+': 'text-yellow-600',
    'C': 'text-orange-600',
    'D': 'text-red-600',
  }
  return colors[grade] || 'text-gray-600'
}
