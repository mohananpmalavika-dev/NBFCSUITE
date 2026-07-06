'use client'

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  Shield, 
  TrendingUp, 
  TrendingDown,
  AlertTriangle,
  CheckCircle2
} from 'lucide-react'
import type { Customer } from '@/types/customer.types'

interface RiskProfileProps {
  customer: Customer
}

export function RiskProfile({ customer }: RiskProfileProps) {
  const getRiskColor = (rating: string) => {
    switch (rating.toLowerCase()) {
      case 'low':
        return 'bg-green-100 text-green-800 border-green-300'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-300'
      case 'very_high':
        return 'bg-red-100 text-red-800 border-red-300'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  const getRiskScore = (rating: string) => {
    switch (rating.toLowerCase()) {
      case 'low': return 85
      case 'medium': return 60
      case 'high': return 35
      case 'very_high': return 15
      default: return 50
    }
  }

  const riskScore = getRiskScore(customer.risk_rating)

  // Calculate risk factors
  const riskFactors = []

  if (!customer.is_kyc_verified) {
    riskFactors.push({
      factor: 'KYC Not Verified',
      severity: 'high' as const,
      description: 'Customer KYC verification is incomplete',
    })
  }

  if (!customer.cibil_score || customer.cibil_score < 650) {
    riskFactors.push({
      factor: 'Low Credit Score',
      severity: customer.cibil_score && customer.cibil_score < 550 ? 'high' : 'medium' as const,
      description: `CIBIL score is ${customer.cibil_score || 'not available'}`,
    })
  }

  if (customer.is_blacklisted) {
    riskFactors.push({
      factor: 'Blacklisted',
      severity: 'high' as const,
      description: customer.blacklist_reason || 'Customer is blacklisted',
    })
  }

  if (!customer.pan_number) {
    riskFactors.push({
      factor: 'PAN Not Provided',
      severity: 'medium' as const,
      description: 'PAN number not available',
    })
  }

  if (!customer.current_address_line1) {
    riskFactors.push({
      factor: 'Address Not Verified',
      severity: 'medium' as const,
      description: 'Customer address not provided',
    })
  }

  // Positive factors
  const positiveFactors = []

  if (customer.is_kyc_verified) {
    positiveFactors.push('KYC Verified')
  }

  if (customer.cibil_score && customer.cibil_score >= 750) {
    positiveFactors.push('Excellent Credit Score')
  }

  if (customer.pan_number && customer.aadhaar_number) {
    positiveFactors.push('Complete Identity Documents')
  }

  return (
    <div className="space-y-6">
      {/* Risk Score Card */}
      <Card className={`border-2 ${getRiskColor(customer.risk_rating)}`}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Risk Profile
          </CardTitle>
          <CardDescription>
            Overall risk assessment and score
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-3">
                <span className="text-5xl font-bold">{riskScore}</span>
                <div>
                  <Badge className={getRiskColor(customer.risk_rating)}>
                    {customer.risk_rating.replace('_', ' ').toUpperCase()}
                  </Badge>
                  <p className="text-sm text-gray-600 mt-1">Risk Rating</p>
                </div>
              </div>
            </div>
            <div className="text-right">
              {riskScore >= 70 ? (
                <TrendingUp className="h-12 w-12 text-green-600" />
              ) : (
                <TrendingDown className="h-12 w-12 text-red-600" />
              )}
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Risk Score</span>
              <span className="text-sm text-gray-600">{riskScore}/100</span>
            </div>
            <Progress value={riskScore} className="h-3" />
          </div>
        </CardContent>
      </Card>

      {/* Risk Factors */}
      {riskFactors.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              Risk Factors
            </CardTitle>
            <CardDescription>
              Factors contributing to risk rating
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {riskFactors.map((factor, index) => (
              <div
                key={index}
                className="flex items-start gap-3 p-3 border rounded-lg"
              >
                <AlertTriangle
                  className={`h-5 w-5 flex-shrink-0 mt-0.5 ${
                    factor.severity === 'high'
                      ? 'text-red-600'
                      : factor.severity === 'medium'
                      ? 'text-yellow-600'
                      : 'text-gray-600'
                  }`}
                />
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h4 className="font-medium text-gray-900">{factor.factor}</h4>
                    <Badge
                      variant="outline"
                      className={
                        factor.severity === 'high'
                          ? 'border-red-300 text-red-700'
                          : factor.severity === 'medium'
                          ? 'border-yellow-300 text-yellow-700'
                          : 'border-gray-300 text-gray-700'
                      }
                    >
                      {factor.severity}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">{factor.description}</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Positive Factors */}
      {positiveFactors.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-green-600" />
              Positive Factors
            </CardTitle>
            <CardDescription>
              Factors reducing risk
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {positiveFactors.map((factor, index) => (
                <div
                  key={index}
                  className="flex items-center gap-2 text-sm text-gray-700"
                >
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  <span>{factor}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Risk Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Credit Score</p>
              <p className="text-2xl font-bold text-gray-900">
                {customer.cibil_score || 'N/A'}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">KYC Status</p>
              <Badge className={customer.is_kyc_verified ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}>
                {customer.is_kyc_verified ? 'Verified' : 'Pending'}
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Account Status</p>
              <Badge className={customer.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                {customer.is_active ? 'Active' : 'Inactive'}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
