'use client'

import { useQuery } from '@tanstack/react-query'
import { useParams } from 'next/navigation'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { customerService } from '@/services/customer.service'
import { Customer360Header } from '@/components/customers/customer-360-header'
import { CustomerOverview } from '@/components/customers/customer-overview'
import { KYCManagement } from '@/components/customers/kyc-management'
import { DocumentVault } from '@/components/customers/document-vault'
import { FamilyTree } from '@/components/customers/family-tree'
import { BankAccounts } from '@/components/customers/bank-accounts'
import { CreditBureau } from '@/components/customers/credit-bureau'
import { CustomerTimelineComponent } from '@/components/customers/customer-timeline'
import { RiskProfile } from '@/components/customers/risk-profile'

export default function CustomerDetailPage() {
  const params = useParams()
  const customerId = params.id as string

  const { data: customer, isLoading } = useQuery({
    queryKey: ['customer', customerId],
    queryFn: () => customerService.getCustomer(customerId),
  })

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="space-y-6">
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-96 w-full" />
        </div>
      </DashboardLayout>
    )
  }

  if (!customer?.data) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <p className="text-gray-600">Customer not found</p>
        </div>
      </DashboardLayout>
    )
  }

  const customerData = customer.data

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Customer 360 Header */}
        <Customer360Header customer={customerData} />

        {/* Main Content Tabs */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 lg:grid-cols-9">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="kyc">KYC</TabsTrigger>
            <TabsTrigger value="documents">Documents</TabsTrigger>
            <TabsTrigger value="family">Family</TabsTrigger>
            <TabsTrigger value="accounts">Bank Accounts</TabsTrigger>
            <TabsTrigger value="bureau">Credit Bureau</TabsTrigger>
            <TabsTrigger value="risk">Risk Profile</TabsTrigger>
            <TabsTrigger value="timeline">Timeline</TabsTrigger>
            <TabsTrigger value="loans">Loans</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <CustomerOverview customer={customerData} />
          </TabsContent>

          {/* KYC Management Tab */}
          <TabsContent value="kyc" className="space-y-6">
            <KYCManagement customer={customerData} />
          </TabsContent>

          {/* Documents Tab */}
          <TabsContent value="documents" className="space-y-6">
            <DocumentVault customerId={customerId} />
          </TabsContent>

          {/* Family Tree Tab */}
          <TabsContent value="family" className="space-y-6">
            <FamilyTree customerId={customerId} />
          </TabsContent>

          {/* Bank Accounts Tab */}
          <TabsContent value="accounts" className="space-y-6">
            <BankAccounts customerId={customerId} />
          </TabsContent>

          {/* Credit Bureau Tab */}
          <TabsContent value="bureau" className="space-y-6">
            <CreditBureau customerId={customerId} />
          </TabsContent>

          {/* Risk Profile Tab */}
          <TabsContent value="risk" className="space-y-6">
            <RiskProfile customer={customerData} />
          </TabsContent>

          {/* Timeline Tab */}
          <TabsContent value="timeline" className="space-y-6">
            <CustomerTimelineComponent customerId={customerId} />
          </TabsContent>

          {/* Loans Tab (Placeholder) */}
          <TabsContent value="loans" className="space-y-6">
            <div className="text-center py-12 text-gray-500">
              <p>Loan accounts will be displayed here</p>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}
