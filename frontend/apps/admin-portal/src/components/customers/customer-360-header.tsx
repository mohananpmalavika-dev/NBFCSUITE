'use client'

import { ArrowLeft, Edit, Phone, Mail, Shield, AlertTriangle } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import type { Customer } from '@/types/customer.types'

interface Customer360HeaderProps {
  customer: Customer
  onEdit?: () => void
}

export function Customer360Header({ customer, onEdit }: Customer360HeaderProps) {
  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  const getKYCColor = (status: string) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      in_progress: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
    }
    return colors[status.toLowerCase()] || colors.pending
  }

  const getRiskColor = (rating: string) => {
    const colors = {
      low: 'bg-green-100 text-green-800',
      medium: 'bg-yellow-100 text-yellow-800',
      high: 'bg-orange-100 text-orange-800',
      very_high: 'bg-red-100 text-red-800',
    }
    return colors[rating.toLowerCase()] || colors.medium
  }

  return (
    <div className="bg-white border-b">
      <div className="px-6 py-4">
        <div className="flex items-start justify-between">
          {/* Left Section */}
          <div className="flex items-start gap-4">
            <Link href="/customers">
              <Button variant="ghost" size="icon">
                <ArrowLeft className="h-5 w-5" />
              </Button>
            </Link>

            <Avatar className="h-16 w-16">
              <AvatarFallback className="text-lg font-semibold bg-primary/10 text-primary">
                {getInitials(customer.full_name)}
              </AvatarFallback>
            </Avatar>

            <div className="flex-1">
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-bold text-gray-900">
                  {customer.full_name}
                </h1>
                {customer.is_blacklisted && (
                  <Badge variant="destructive" className="gap-1">
                    <AlertTriangle className="h-3 w-3" />
                    Blacklisted
                  </Badge>
                )}
                {!customer.is_active && (
                  <Badge variant="secondary">Inactive</Badge>
                )}
              </div>

              <p className="text-sm text-gray-600 mt-1">
                Customer Code: <span className="font-mono font-medium">{customer.customer_code}</span>
              </p>

              <div className="flex items-center gap-4 mt-3">
                {customer.mobile && (
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Phone className="h-4 w-4" />
                    <span>{customer.mobile}</span>
                  </div>
                )}
                {customer.email && (
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Mail className="h-4 w-4" />
                    <span>{customer.email}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Right Section */}
          <div className="flex items-center gap-3">
            {onEdit && (
              <Button onClick={onEdit}>
                <Edit className="h-4 w-4 mr-2" />
                Edit
              </Button>
            )}
          </div>
        </div>

        {/* Status Bar */}
        <div className="flex items-center gap-4 mt-4 pt-4 border-t">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">KYC Status:</span>
            <Badge className={getKYCColor(customer.kyc_status)}>
              {customer.kyc_status.replace('_', ' ')}
            </Badge>
          </div>

          <div className="flex items-center gap-2">
            <Shield className="h-4 w-4 text-gray-400" />
            <span className="text-sm text-gray-600">Risk Rating:</span>
            <Badge className={getRiskColor(customer.risk_rating)}>
              {customer.risk_rating.replace('_', ' ')}
            </Badge>
          </div>

          {customer.cibil_score && (
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">CIBIL Score:</span>
              <span className="text-sm font-semibold text-gray-900">
                {customer.cibil_score}
              </span>
            </div>
          )}

          {customer.age && (
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">Age:</span>
              <span className="text-sm font-medium text-gray-900">
                {customer.age} years
              </span>
            </div>
          )}

          {customer.pan_number && (
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">PAN:</span>
              <span className="text-sm font-mono font-medium text-gray-900">
                {customer.pan_number}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
