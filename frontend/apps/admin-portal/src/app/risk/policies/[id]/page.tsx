'use client'

import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { ArrowLeft, Edit, CheckCircle, XCircle, FileText } from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { riskService } from '@/services/risk.service'
import { formatDate } from '@/lib/utils'

export default function PolicyDetailsPage({ params }: { params: { id: string } }) {
  const policyId = parseInt(params.id)

  const { data: policy, isLoading } = useQuery({
    queryKey: ['credit-policy', policyId],
    queryFn: () => riskService.getCreditPolicy(policyId),
  })

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="space-y-6">
          <Skeleton className="h-10 w-64" />
          <Skeleton className="h-96 w-full" />
        </div>
      </DashboardLayout>
    )
  }

  if (!policy) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <FileText className="h-16 w-16 mx-auto text-gray-400 mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Policy Not Found</h2>
          <p className="text-gray-600 mb-4">The credit policy you're looking for doesn't exist.</p>
          <Link href="/risk/policies">
            <Button>Back to Policies</Button>
          </Link>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/risk/policies">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
            </Link>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-3xl font-bold text-gray-900">{policy.policy_name}</h1>
                {policy.is_active ? (
                  <Badge className="bg-green-100 text-green-800">
                    <CheckCircle className="h-3 w-3 mr-1" />
                    Active
                  </Badge>
                ) : (
                  <Badge variant="secondary">
                    <XCircle className="h-3 w-3 mr-1" />
                    Inactive
                  </Badge>
                )}
              </div>
              <p className="text-gray-600 mt-1">{policy.policy_code} • Version {policy.policy_version}</p>
            </div>
          </div>
          <Link href={`/risk/policies/${policyId}/edit`}>
            <Button>
              <Edit className="h-4 w-4 mr-2" />
              Edit Policy
            </Button>
          </Link>
        </div>

        {/* Basic Information */}
        <Card>
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InfoItem label="Policy Code" value={policy.policy_code} />
              <InfoItem label="Policy Version" value={policy.policy_version} />
              <InfoItem label="Effective From" value={formatDate(policy.effective_from)} />
              <InfoItem
                label="Effective To"
                value={policy.effective_to ? formatDate(policy.effective_to) : 'No end date'}
              />
            </div>
            {policy.description && (
              <div>
                <label className="text-sm font-medium text-gray-700">Description</label>
                <p className="text-gray-900 mt-1">{policy.description}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Applicability */}
        <Card>
          <CardHeader>
            <CardTitle>Applicability</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">Product Types</label>
              <div className="flex flex-wrap gap-2">
                {policy.product_types.map((product) => (
                  <Badge key={product} variant="outline">
                    {product.replace('_', ' ')}
                  </Badge>
                ))}
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">Customer Segments</label>
              <div className="flex flex-wrap gap-2">
                {policy.customer_segments.map((segment) => (
                  <Badge key={segment} variant="outline">
                    {segment.replace('_', ' ')}
                  </Badge>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Eligibility Criteria */}
        <Card>
          <CardHeader>
            <CardTitle>Eligibility Criteria</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <InfoItem label="Min CIBIL Score" value={policy.min_cibil_score} />
              <InfoItem label="Max Debt-to-Income Ratio" value={`${policy.max_debt_to_income_ratio}%`} />
              <InfoItem label="Min Monthly Income" value={`₹${policy.min_monthly_income.toLocaleString()}`} />
            </div>
          </CardContent>
        </Card>

        {/* Loan Parameters */}
        <Card>
          <CardHeader>
            <CardTitle>Loan Parameters</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InfoItem
                label="Loan Amount Range"
                value={`₹${(policy.min_loan_amount / 100000).toFixed(2)}L - ₹${(policy.max_loan_amount / 100000).toFixed(2)}L`}
              />
              <InfoItem
                label="Tenure Range"
                value={`${policy.min_tenure_months} - ${policy.max_tenure_months} months`}
              />
            </div>
          </CardContent>
        </Card>

        {/* Age & Employment Rules */}
        <Card>
          <CardHeader>
            <CardTitle>Age & Employment Rules</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InfoItem label="Age Range" value={`${policy.min_age} - ${policy.max_age} years`} />
              <InfoItem
                label="Min Years in Employment"
                value={`${policy.min_years_in_employment} years`}
              />
              <InfoItem
                label="Self-Employed Allowed"
                value={
                  <Badge variant={policy.self_employed_allowed ? 'default' : 'secondary'}>
                    {policy.self_employed_allowed ? 'Yes' : 'No'}
                  </Badge>
                }
              />
            </div>
          </CardContent>
        </Card>

        {/* Geographic Restrictions */}
        {(policy.allowed_states?.length > 0 || policy.negative_geographies?.length > 0) && (
          <Card>
            <CardHeader>
              <CardTitle>Geographic Restrictions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {policy.allowed_states && policy.allowed_states.length > 0 && (
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-2 block">
                    Allowed States ({policy.allowed_states.length})
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {policy.allowed_states.map((state) => (
                      <Badge key={state} className="bg-green-100 text-green-800">
                        {state}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
              {policy.negative_geographies && policy.negative_geographies.length > 0 && (
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-2 block">
                    Negative Geographies ({policy.negative_geographies.length})
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {policy.negative_geographies.map((state) => (
                      <Badge key={state} variant="destructive">
                        {state}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Negative Profiles */}
        {policy.negative_professions && policy.negative_professions.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Negative Profiles</CardTitle>
            </CardHeader>
            <CardContent>
              <label className="text-sm font-medium text-gray-700 mb-2 block">
                Negative Professions ({policy.negative_professions.length})
              </label>
              <div className="flex flex-wrap gap-2">
                {policy.negative_professions.map((profession) => (
                  <Badge key={profession} variant="destructive">
                    {profession}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Documentation Requirements */}
        {policy.required_documents && policy.required_documents.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Documentation Requirements</CardTitle>
            </CardHeader>
            <CardContent>
              <label className="text-sm font-medium text-gray-700 mb-2 block">
                Required Documents ({policy.required_documents.length})
              </label>
              <div className="flex flex-wrap gap-2">
                {policy.required_documents.map((doc) => (
                  <Badge key={doc} variant="outline">
                    {doc}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Audit Trail */}
        <Card>
          <CardHeader>
            <CardTitle>Audit Trail</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between py-2 border-b">
                <div>
                  <p className="text-sm font-medium">Created</p>
                  <p className="text-sm text-gray-600">{formatDate(policy.created_at)}</p>
                </div>
                <Badge variant="outline">System</Badge>
              </div>
              <div className="flex items-center justify-between py-2 border-b">
                <div>
                  <p className="text-sm font-medium">Last Updated</p>
                  <p className="text-sm text-gray-600">{formatDate(policy.updated_at)}</p>
                </div>
                <Badge variant="outline">System</Badge>
              </div>
              {policy.created_by && (
                <div className="flex items-center justify-between py-2">
                  <div>
                    <p className="text-sm font-medium">Created By</p>
                    <p className="text-sm text-gray-600">User ID: {policy.created_by}</p>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Related Pricing Rules */}
        <Card>
          <CardHeader>
            <CardTitle>Related Pricing Rules</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 text-gray-500">
              <p>No pricing rules linked to this policy yet</p>
              <Link href={`/risk/pricing?policy=${policyId}`}>
                <Button variant="link" className="mt-2">
                  Create Pricing Rule
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}

function InfoItem({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div>
      <label className="text-sm font-medium text-gray-700">{label}</label>
      <p className="text-gray-900 mt-1 font-medium">{value}</p>
    </div>
  )
}
