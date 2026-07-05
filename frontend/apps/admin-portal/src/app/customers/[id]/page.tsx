'use client'

import { useQuery } from '@tanstack/react-query'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { 
  ArrowLeft, 
  Edit, 
  Phone, 
  Mail, 
  MapPin, 
  Calendar,
  FileText,
  CreditCard,
  User
} from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { customerService } from '@/services/customer.service'
import { formatDate, formatPhone, getStatusColor, maskString } from '@/lib/utils'

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
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-48 w-full" />
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
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/customers">
              <Button variant="ghost" size="icon">
                <ArrowLeft className="h-5 w-5" />
              </Button>
            </Link>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {customerData.full_name}
              </h1>
              <p className="text-gray-600 mt-1">
                Customer Code: {customerData.customer_code}
              </p>
            </div>
          </div>
          <Link href={`/customers/${customerId}/edit`}>
            <Button>
              <Edit className="h-4 w-4 mr-2" />
              Edit Customer
            </Button>
          </Link>
        </div>

        {/* Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Customer Status</p>
                  <Badge className={`mt-2 ${getStatusColor(customerData.customer_status)}`}>
                    {customerData.customer_status}
                  </Badge>
                </div>
                <User className="h-8 w-8 text-gray-400" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">KYC Status</p>
                  <Badge className={`mt-2 ${getStatusColor(customerData.kyc_status)}`}>
                    {customerData.kyc_status}
                  </Badge>
                </div>
                <FileText className="h-8 w-8 text-gray-400" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Registered On</p>
                  <p className="text-lg font-semibold mt-1">
                    {formatDate(customerData.created_at)}
                  </p>
                </div>
                <Calendar className="h-8 w-8 text-gray-400" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="personal" className="space-y-6">
          <TabsList>
            <TabsTrigger value="personal">Personal Information</TabsTrigger>
            <TabsTrigger value="contact">Contact Details</TabsTrigger>
            <TabsTrigger value="documents">Documents</TabsTrigger>
            <TabsTrigger value="accounts">Accounts</TabsTrigger>
          </TabsList>

          {/* Personal Information */}
          <TabsContent value="personal" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Basic Details</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <InfoItem label="Full Name" value={customerData.full_name} />
                  <InfoItem label="First Name" value={customerData.first_name} />
                  <InfoItem label="Middle Name" value={customerData.middle_name || '-'} />
                  <InfoItem label="Last Name" value={customerData.last_name} />
                  <InfoItem label="Date of Birth" value={formatDate(customerData.date_of_birth)} />
                  <InfoItem label="Gender" value={customerData.gender} />
                  <InfoItem label="Marital Status" value={customerData.marital_status} />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Identity Information</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <InfoItem 
                    label="PAN Number" 
                    value={customerData.pan_number ? maskString(customerData.pan_number, 4) : '-'}
                    icon={CreditCard}
                  />
                  <InfoItem 
                    label="Aadhaar Number" 
                    value={customerData.aadhaar_number ? maskString(customerData.aadhaar_number, 4) : '-'}
                    icon={CreditCard}
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Contact Details */}
          <TabsContent value="contact" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Contact Information</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <InfoItem 
                    label="Mobile Number" 
                    value={formatPhone(customerData.mobile_number)}
                    icon={Phone}
                  />
                  <InfoItem 
                    label="Email Address" 
                    value={customerData.email || '-'}
                    icon={Mail}
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Address</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-start gap-3">
                  <MapPin className="h-5 w-5 text-gray-400 mt-1" />
                  <div>
                    <p className="text-gray-900">No address information available</p>
                    <p className="text-sm text-gray-500 mt-1">
                      Add address details in customer profile
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Documents */}
          <TabsContent value="documents">
            <Card>
              <CardHeader>
                <CardTitle>Uploaded Documents</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-gray-500">
                  <FileText className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                  <p>No documents uploaded</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Accounts */}
          <TabsContent value="accounts">
            <Card>
              <CardHeader>
                <CardTitle>Loan & Deposit Accounts</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-gray-500">
                  <CreditCard className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                  <p>No accounts found</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}

function InfoItem({ 
  label, 
  value, 
  icon: Icon 
}: { 
  label: string
  value: string
  icon?: any 
}) {
  return (
    <div>
      <p className="text-sm text-gray-600 mb-1">{label}</p>
      <div className="flex items-center gap-2">
        {Icon && <Icon className="h-4 w-4 text-gray-400" />}
        <p className="text-gray-900 font-medium">{value}</p>
      </div>
    </div>
  )
}
