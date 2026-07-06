'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { User, MapPin, Calendar, Briefcase, IndianRupee } from 'lucide-react'
import type { Customer } from '@/types/customer.types'
import { formatDate } from '@/lib/utils'

interface CustomerOverviewProps {
  customer: Customer
}

export function CustomerOverview({ customer }: CustomerOverviewProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Personal Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            Personal Information
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <InfoRow label="Full Name" value={customer.full_name} />
          <InfoRow label="First Name" value={customer.first_name || '-'} />
          <InfoRow label="Middle Name" value={customer.middle_name || '-'} />
          <InfoRow label="Last Name" value={customer.last_name || '-'} />
          <InfoRow label="Date of Birth" value={customer.date_of_birth ? formatDate(customer.date_of_birth) : '-'} />
          <InfoRow label="Age" value={customer.age ? `${customer.age} years` : '-'} />
          <InfoRow label="Gender" value={customer.gender || '-'} />
          <InfoRow label="Marital Status" value={customer.marital_status ? customer.marital_status.replace('_', ' ') : '-'} />
          <InfoRow label="Father's Name" value={customer.father_name || '-'} />
          <InfoRow label="Mother's Name" value={customer.mother_name || '-'} />
        </CardContent>
      </Card>

      {/* Contact Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MapPin className="h-5 w-5" />
            Contact & Address
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <InfoRow label="Mobile Number" value={customer.mobile} />
          <InfoRow label="Alternate Mobile" value={customer.alternate_mobile || '-'} />
          <InfoRow label="Email Address" value={customer.email || '-'} />
          <div className="pt-2 border-t">
            <p className="text-sm font-medium text-gray-700 mb-2">Current Address</p>
            {customer.current_address_line1 ? (
              <>
                <InfoRow label="Address" value={customer.current_address_line1} />
                {customer.current_address_line2 && (
                  <InfoRow label="" value={customer.current_address_line2} />
                )}
                <InfoRow label="City" value={customer.current_city_name || '-'} />
                <InfoRow label="State" value={customer.current_state_name || '-'} />
                <InfoRow label="Pincode" value={customer.current_pincode || '-'} />
              </>
            ) : (
              <p className="text-sm text-gray-500">No address information available</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Identity Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Identity & KYC
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <InfoRow label="Customer Type" value={customer.customer_type.replace('_', ' ')} />
          {customer.business_name && (
            <InfoRow label="Business Name" value={customer.business_name} />
          )}
          <InfoRow label="PAN Number" value={customer.pan_number || 'Not provided'} />
          <InfoRow 
            label="Aadhaar Number" 
            value={customer.aadhaar_number ? `XXXX XXXX ${customer.aadhaar_number.slice(-4)}` : 'Not provided'} 
          />
          <InfoRow label="KYC Verified" value={customer.is_kyc_verified ? 'Yes' : 'No'} />
          <InfoRow label="Account Status" value={customer.is_active ? 'Active' : 'Inactive'} />
          {customer.is_blacklisted && (
            <>
              <InfoRow label="Blacklist Status" value="Blacklisted" className="text-red-600" />
              {customer.blacklist_reason && (
                <InfoRow label="Blacklist Reason" value={customer.blacklist_reason} />
              )}
            </>
          )}
        </CardContent>
      </Card>

      {/* Financial Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <IndianRupee className="h-5 w-5" />
            Financial Profile
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <InfoRow label="Occupation" value={customer.occupation_name || '-'} />
          <InfoRow label="Industry" value={customer.industry_name || '-'} />
          <InfoRow 
            label="Monthly Income" 
            value={customer.monthly_income ? `₹${customer.monthly_income.toLocaleString('en-IN')}` : '-'} 
          />
          <InfoRow 
            label="Annual Income" 
            value={customer.annual_income ? `₹${customer.annual_income.toLocaleString('en-IN')}` : '-'} 
          />
          <InfoRow label="CIBIL Score" value={customer.cibil_score?.toString() || 'Not available'} />
          <InfoRow label="Risk Rating" value={customer.risk_rating.replace('_', ' ').toUpperCase()} />
        </CardContent>
      </Card>

      {/* System Information */}
      <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Briefcase className="h-5 w-5" />
            System Information
          </CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <InfoRow label="Customer Code" value={customer.customer_code} />
          <InfoRow label="Created On" value={formatDate(customer.created_at)} />
          <InfoRow label="Last Updated" value={customer.updated_at ? formatDate(customer.updated_at) : 'Never'} />
        </CardContent>
      </Card>
    </div>
  )
}

function InfoRow({ 
  label, 
  value, 
  className = '' 
}: { 
  label: string
  value: string
  className?: string 
}) {
  return (
    <div className="flex justify-between items-start">
      <span className="text-sm text-gray-600">{label}</span>
      <span className={`text-sm font-medium text-gray-900 text-right ${className}`}>
        {value}
      </span>
    </div>
  )
}
