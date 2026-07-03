/**
 * Deposits Module - Main Dashboard
 * Overview of all deposit operations and quick actions
 */

import Link from 'next/link';
import { 
  Building2, 
  TrendingUp, 
  Users, 
  Calendar,
  PiggyBank,
  BarChart3,
  Clock,
  AlertCircle,
  ArrowRight,
  Sparkles
} from 'lucide-react';

export default function DepositsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Deposit Operating System
            </h1>
            <p className="text-slate-600 mt-2">
              AI-powered deposit management with complete lifecycle tracking
            </p>
          </div>
          
          <div className="flex gap-3">
            <Link 
              href="/deposits/products"
              className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors shadow-lg shadow-blue-200"
            >
              Open Deposit
            </Link>
            <Link 
              href="/deposits/dashboard"
              className="px-6 py-3 bg-white text-slate-700 rounded-lg font-medium hover:bg-slate-50 transition-colors border border-slate-200"
            >
              View Dashboard
            </Link>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <StatCard
            icon={<PiggyBank className="w-6 h-6 text-blue-600" />}
            label="Total Deposits"
            value="₹45.2 Cr"
            change="+12.5%"
            trend="up"
          />
          <StatCard
            icon={<Users className="w-6 h-6 text-green-600" />}
            label="Active Accounts"
            value="1,247"
            change="+8.2%"
            trend="up"
          />
          <StatCard
            icon={<TrendingUp className="w-6 h-6 text-purple-600" />}
            label="Avg. Rate"
            value="7.45%"
            change="+0.25%"
            trend="up"
          />
          <StatCard
            icon={<Calendar className="w-6 h-6 text-orange-600" />}
            label="Maturing (30d)"
            value="₹2.8 Cr"
            change="124 accounts"
            trend="neutral"
          />
        </div>

        {/* Main Actions Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Deposit Products */}
          <ActionCard
            title="Deposit Products"
            description="Browse and compare FD/RD products with AI-powered recommendations"
            icon={<Building2 className="w-8 h-8" />}
            color="blue"
            href="/deposits/products"
            features={[
              "Fixed Deposits",
              "Recurring Deposits",
              "Senior Citizen Plans",
              "Rate Comparison"
            ]}
          />

          {/* Account Management */}
          <ActionCard
            title="Account Management"
            description="Manage all deposit accounts with complete lifecycle tracking"
            icon={<Users className="w-8 h-8" />}
            color="green"
            href="/deposits/accounts"
            features={[
              "Active Accounts",
              "Account Search",
              "Interest Statements",
              "Nominee Management"
            ]}
          />

          {/* Maturity Pipeline */}
          <ActionCard
            title="Maturity Management"
            description="Track upcoming maturities and process renewals"
            icon={<Calendar className="w-8 h-8" />}
            color="purple"
            href="/deposits/maturity"
            features={[
              "Maturity Pipeline",
              "Auto-Renewal",
              "Payout Processing",
              "Renewal Recommendations"
            ]}
          />

          {/* RD Management */}
          <ActionCard
            title="RD Management"
            description="Manage recurring deposit installments and collections"
            icon={<Clock className="w-8 h-8" />}
            color="orange"
            href="/deposits/rd"
            features={[
              "Installment Tracking",
              "Payment Collection",
              "Overdue Management",
              "Auto-Debit Setup"
            ]}
          />

          {/* AI Intelligence */}
          <ActionCard
            title="AI Intelligence"
            description="Get AI-powered insights and predictions for better decisions"
            icon={<Sparkles className="w-8 h-8" />}
            color="pink"
            href="/deposits/ai"
            features={[
              "Renewal Predictions",
              "Churn Analysis",
              "Product Recommendations",
              "Customer Insights"
            ]}
            badge="AI"
          />

          {/* Analytics & Reports */}
          <ActionCard
            title="Analytics & Reports"
            description="Comprehensive treasury analytics and business intelligence"
            icon={<BarChart3 className="w-8 h-8" />}
            color="indigo"
            href="/deposits/analytics"
            features={[
              "Treasury Dashboard",
              "Growth Trends",
              "Cost of Funds",
              "Branch Analytics"
            ]}
          />
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-6">
          <h2 className="text-xl font-bold text-slate-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <QuickAction
              label="Open Fixed Deposit"
              href="/deposits/fd/new"
              icon={<PiggyBank className="w-5 h-5" />}
            />
            <QuickAction
              label="Open Recurring Deposit"
              href="/deposits/rd/new"
              icon={<Clock className="w-5 h-5" />}
            />
            <QuickAction
              label="Calculate Interest"
              href="/deposits/calculator"
              icon={<TrendingUp className="w-5 h-5" />}
            />
            <QuickAction
              label="Maturity Pipeline"
              href="/deposits/maturity/pipeline"
              icon={<Calendar className="w-5 h-5" />}
            />
            <QuickAction
              label="Customer Search"
              href="/deposits/accounts/search"
              icon={<Users className="w-5 h-5" />}
            />
            <QuickAction
              label="Premature Closure"
              href="/deposits/closure"
              icon={<AlertCircle className="w-5 h-5" />}
            />
            <QuickAction
              label="AI Insights"
              href="/deposits/ai/insights"
              icon={<Sparkles className="w-5 h-5" />}
            />
            <QuickAction
              label="Reports"
              href="/deposits/reports"
              icon={<BarChart3 className="w-5 h-5" />}
            />
          </div>
        </div>

        {/* Alerts & Notifications */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <AlertCard
            type="info"
            title="Upcoming Maturities"
            message="124 deposits maturing in next 30 days worth ₹2.8 Cr"
            action="View Pipeline"
            href="/deposits/maturity/pipeline"
          />
          <AlertCard
            type="warning"
            title="Overdue RD Installments"
            message="18 overdue installments pending collection worth ₹1.2 L"
            action="View Overdue"
            href="/deposits/rd/overdue"
          />
        </div>
      </div>
    </div>
  );
}

// Components

function StatCard({ 
  icon, 
  label, 
  value, 
  change, 
  trend 
}: { 
  icon: React.ReactNode; 
  label: string; 
  value: string; 
  change: string;
  trend: 'up' | 'down' | 'neutral';
}) {
  return (
    <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="p-3 bg-slate-50 rounded-lg">
          {icon}
        </div>
        <span className={`text-sm font-medium ${
          trend === 'up' ? 'text-green-600' :
          trend === 'down' ? 'text-red-600' :
          'text-slate-600'
        }`}>
          {change}
        </span>
      </div>
      <p className="text-slate-600 text-sm mb-1">{label}</p>
      <p className="text-2xl font-bold text-slate-900">{value}</p>
    </div>
  );
}

function ActionCard({ 
  title, 
  description, 
  icon, 
  color, 
  href, 
  features,
  badge 
}: {
  title: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  href: string;
  features: string[];
  badge?: string;
}) {
  const colorClasses = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600',
    purple: 'from-purple-500 to-purple-600',
    orange: 'from-orange-500 to-orange-600',
    pink: 'from-pink-500 to-pink-600',
    indigo: 'from-indigo-500 to-indigo-600',
  }[color];

  return (
    <Link href={href}>
      <div className="group bg-white rounded-xl shadow-lg border border-slate-200 p-6 hover:shadow-xl transition-all cursor-pointer h-full">
        <div className="flex items-start justify-between mb-4">
          <div className={`p-3 bg-gradient-to-br ${colorClasses} rounded-xl text-white`}>
            {icon}
          </div>
          {badge && (
            <span className="px-3 py-1 bg-gradient-to-r from-purple-500 to-pink-500 text-white text-xs font-bold rounded-full">
              {badge}
            </span>
          )}
        </div>
        
        <h3 className="text-xl font-bold text-slate-900 mb-2 group-hover:text-blue-600 transition-colors">
          {title}
        </h3>
        <p className="text-slate-600 text-sm mb-4">
          {description}
        </p>
        
        <ul className="space-y-2 mb-4">
          {features.map((feature, index) => (
            <li key={index} className="flex items-center text-sm text-slate-600">
              <div className="w-1.5 h-1.5 rounded-full bg-slate-400 mr-2" />
              {feature}
            </li>
          ))}
        </ul>
        
        <div className="flex items-center text-blue-600 font-medium text-sm group-hover:gap-2 transition-all">
          Explore
          <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
        </div>
      </div>
    </Link>
  );
}

function QuickAction({ 
  label, 
  href, 
  icon 
}: { 
  label: string; 
  href: string; 
  icon: React.ReactNode;
}) {
  return (
    <Link href={href}>
      <div className="flex items-center gap-3 p-4 rounded-lg border border-slate-200 hover:border-blue-300 hover:bg-blue-50/50 transition-all cursor-pointer group">
        <div className="p-2 bg-slate-100 rounded-lg group-hover:bg-blue-100 transition-colors">
          {icon}
        </div>
        <span className="text-sm font-medium text-slate-700 group-hover:text-blue-600 transition-colors">
          {label}
        </span>
      </div>
    </Link>
  );
}

function AlertCard({ 
  type, 
  title, 
  message, 
  action, 
  href 
}: {
  type: 'info' | 'warning' | 'error';
  title: string;
  message: string;
  action: string;
  href: string;
}) {
  const styles = {
    info: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      icon: 'text-blue-600',
      button: 'bg-blue-600 hover:bg-blue-700'
    },
    warning: {
      bg: 'bg-orange-50',
      border: 'border-orange-200',
      icon: 'text-orange-600',
      button: 'bg-orange-600 hover:bg-orange-700'
    },
    error: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      icon: 'text-red-600',
      button: 'bg-red-600 hover:bg-red-700'
    }
  }[type];

  return (
    <div className={`${styles.bg} ${styles.border} border rounded-xl p-6`}>
      <div className="flex items-start gap-4">
        <AlertCircle className={`w-6 h-6 ${styles.icon} flex-shrink-0 mt-1`} />
        <div className="flex-1">
          <h3 className="font-bold text-slate-900 mb-1">{title}</h3>
          <p className="text-slate-600 text-sm mb-4">{message}</p>
          <Link href={href}>
            <button className={`px-4 py-2 ${styles.button} text-white rounded-lg text-sm font-medium transition-colors`}>
              {action}
            </button>
          </Link>
        </div>
      </div>
    </div>
  );
}
