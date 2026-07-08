'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { Plus, Search, Filter, Eye, TrendingUp, Clock, Percent, PiggyBank } from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { depositService } from '@/services/deposit.service'
import { formatCurrency, getStatusColor } from '@/lib/utils'
import type { DepositProduct } from '@/types'

export default function DepositProductsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['deposit-products', page, search, typeFilter],
    queryFn: () => depositService.getProducts({ 
      page, 
      page_size: 12,
      deposit_type: typeFilter || undefined
    }),
  })

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Deposit Products</h1>
            <p className="text-gray-600 mt-1">Browse available deposit schemes and interest rates</p>
          </div>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              type="search"
              placeholder="Search products by name, code..."
              className="pl-10"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="">All Types</option>
            <option value="Savings">Savings</option>
            <option value="Fixed">Fixed Deposit</option>
            <option value="Recurring">Recurring Deposit</option>
            <option value="MIS">MIS</option>
          </select>
          <Button variant="outline">
            <Filter className="h-4 w-4 mr-2" />
            More Filters
          </Button>
        </div>

        {/* Products Grid */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <Card key={i}>
                <CardHeader>
                  <Skeleton className="h-6 w-3/4" />
                  <Skeleton className="h-4 w-1/2 mt-2" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-20 w-full" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : data?.data?.items && data.data.items.length > 0 ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {data.data.items.map((product: DepositProduct) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>

            {/* Pagination */}
            {data.data.items.length > 0 && (
              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-600">
                  Showing {((page - 1) * 12) + 1} to {Math.min(page * 12, data.data.total || 0)} of {data.data.total || 0} products
                </p>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={!data.data.has_prev}
                    onClick={() => setPage(page - 1)}
                  >
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={!data.data.has_next}
                    onClick={() => setPage(page + 1)}
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </>
        ) : (
          <Card>
            <CardContent className="py-12">
              <div className="text-center text-gray-500">
                <PiggyBank className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                <p className="text-lg font-medium">No deposit products found</p>
                <p className="text-sm mt-1">Try adjusting your search or filters</p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  )
}

function ProductCard({ product }: { product: DepositProduct }) {
  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'Savings':
        return PiggyBank
      case 'Fixed':
        return TrendingUp
      case 'Recurring':
        return Clock
      case 'MIS':
        return Percent
      default:
        return PiggyBank
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'Savings':
        return 'bg-blue-100 text-blue-700'
      case 'Fixed':
        return 'bg-green-100 text-green-700'
      case 'Recurring':
        return 'bg-purple-100 text-purple-700'
      case 'MIS':
        return 'bg-orange-100 text-orange-700'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }

  const Icon = getTypeIcon(product.deposit_type)

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg mb-2">{product.product_name}</CardTitle>
            <Badge className={getTypeColor(product.deposit_type)}>
              {product.deposit_type}
            </Badge>
          </div>
          <div className={`h-12 w-12 rounded-lg ${getTypeColor(product.deposit_type)} flex items-center justify-center`}>
            <Icon className="h-6 w-6" />
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Interest Rate */}
        <div className="bg-gradient-to-r from-green-50 to-blue-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600 mb-1">Interest Rate</p>
          <p className="text-3xl font-bold text-gray-900">
            {product.interest_rate}% <span className="text-sm font-normal text-gray-600">p.a.</span>
          </p>
        </div>

        {/* Key Details */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-gray-500 mb-1">Min Amount</p>
            <p className="text-sm font-semibold text-gray-900">
              {formatCurrency(product.min_deposit_amount)}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">Max Amount</p>
            <p className="text-sm font-semibold text-gray-900">
              {product.max_deposit_amount 
                ? formatCurrency(product.max_deposit_amount)
                : 'No Limit'}
            </p>
          </div>
          
          {product.deposit_type === 'Fixed' && (
            <>
              <div>
                <p className="text-xs text-gray-500 mb-1">Min Tenure</p>
                <p className="text-sm font-semibold text-gray-900">
                  {product.min_tenure_months} months
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">Max Tenure</p>
                <p className="text-sm font-semibold text-gray-900">
                  {product.max_tenure_months} months
                </p>
              </div>
            </>
          )}

          {product.deposit_type === 'Recurring' && (
            <>
              <div>
                <p className="text-xs text-gray-500 mb-1">Min Tenure</p>
                <p className="text-sm font-semibold text-gray-900">
                  {product.min_tenure_months} months
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">Max Tenure</p>
                <p className="text-sm font-semibold text-gray-900">
                  {product.max_tenure_months} months
                </p>
              </div>
            </>
          )}
        </div>

        {/* Features */}
        <div className="space-y-2 pt-2 border-t">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Interest Type</span>
            <Badge variant="outline">{product.interest_calculation_type}</Badge>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Status</span>
            <Badge className={getStatusColor(product.status)}>
              {product.status}
            </Badge>
          </div>
        </div>

        {/* Action Button */}
        <Link href={`/deposits/accounts/new?product_id=${product.id}`}>
          <Button className="w-full" disabled={product.status !== 'Active'}>
            <Plus className="h-4 w-4 mr-2" />
            Open Account
          </Button>
        </Link>
      </CardContent>
    </Card>
  )
}
