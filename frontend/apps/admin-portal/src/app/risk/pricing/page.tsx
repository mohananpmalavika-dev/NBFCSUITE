'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, Edit, Trash2, Calculator, TrendingUp } from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Skeleton } from '@/components/ui/skeleton'
import { riskService } from '@/services/risk.service'
import { toast } from 'sonner'

export default function PricingRulesPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [policyFilter, setPolicyFilter] = useState<number | undefined>()
  const [showModal, setShowModal] = useState(false)
  const [showCalculator, setShowCalculator] = useState(false)
  const [editingRule, setEditingRule] = useState<any>(null)
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['pricing-rules', page, policyFilter],
    queryFn: () => riskService.getPricingRules({
      page,
      page_size: 20,
      policy_id: policyFilter,
    }),
  })

  const { data: policies } = useQuery({
    queryKey: ['credit-policies-list'],
    queryFn: () => riskService.getCreditPolicies({ page: 1, page_size: 100 }),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => riskService.deletePricingRule(id),
    onSuccess: () => {
      toast.success('Pricing rule deleted successfully')
      queryClient.invalidateQueries({ queryKey: ['pricing-rules'] })
    },
    onError: () => {
      toast.error('Failed to delete pricing rule')
    },
  })

  const handleDelete = (id: number, name: string) => {
    if (confirm(`Are you sure you want to delete the rule "${name}"?`)) {
      deleteMutation.mutate(id)
    }
  }

  const handleEdit = (rule: any) => {
    setEditingRule(rule)
    setShowModal(true)
  }

  const handleCreate = () => {
    setEditingRule(null)
    setShowModal(true)
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Risk-Based Pricing</h1>
            <p className="text-gray-600 mt-1">Define pricing rules based on risk parameters</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => setShowCalculator(true)}>
              <Calculator className="h-4 w-4 mr-2" />
              Calculator
            </Button>
            <Button onClick={handleCreate}>
              <Plus className="h-4 w-4 mr-2" />
              New Rule
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatCard label="Total Rules" value={data?.total || 0} icon={TrendingUp} />
          <StatCard label="Active Rules" value={data?.items.filter(r => r.is_active).length || 0} color="green" />
          <StatCard label="Avg Rate Adjustment" value="+1.25%" color="blue" />
          <StatCard label="Policies" value={policies?.total || 0} color="purple" />
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              type="search"
              placeholder="Search rules..."
              className="pl-10"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <select
            value={policyFilter || ''}
            onChange={(e) => setPolicyFilter(e.target.value ? parseInt(e.target.value) : undefined)}
            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="">All Policies</option>
            {policies?.items.map(policy => (
              <option key={policy.id} value={policy.id}>{policy.policy_name}</option>
            ))}
          </select>
        </div>

        {/* Table */}
        <div className="bg-white rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Rule Code</TableHead>
                <TableHead>Rule Name</TableHead>
                <TableHead>Priority</TableHead>
                <TableHead>Credit Policy</TableHead>
                <TableHead>Risk Grade Range</TableHead>
                <TableHead>CIBIL Range</TableHead>
                <TableHead>DTI Range</TableHead>
                <TableHead>Rate Adjustment</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                [...Array(5)].map((_, i) => (
                  <TableRow key={i}>
                    {[...Array(10)].map((_, j) => (
                      <TableCell key={j}><Skeleton className="h-4 w-20" /></TableCell>
                    ))}
                  </TableRow>
                ))
              ) : data?.items && data.items.length > 0 ? (
                data.items.map((rule) => (
                  <TableRow key={rule.id}>
                    <TableCell className="font-medium">{rule.rule_code}</TableCell>
                    <TableCell>{rule.rule_name}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{rule.priority}</Badge>
                    </TableCell>
                    <TableCell className="text-sm">{rule.policy_id}</TableCell>
                    <TableCell>
                      {rule.min_risk_grade && rule.max_risk_grade
                        ? `${rule.min_risk_grade} - ${rule.max_risk_grade}`
                        : '-'}
                    </TableCell>
                    <TableCell>
                      {rule.min_cibil_score && rule.max_cibil_score
                        ? `${rule.min_cibil_score} - ${rule.max_cibil_score}`
                        : '-'}
                    </TableCell>
                    <TableCell>
                      {rule.min_dti_ratio !== null && rule.max_dti_ratio !== null
                        ? `${rule.min_dti_ratio}% - ${rule.max_dti_ratio}%`
                        : '-'}
                    </TableCell>
                    <TableCell>
                      <span className={rule.rate_adjustment >= 0 ? 'text-red-600' : 'text-green-600'}>
                        {rule.rate_adjustment >= 0 ? '+' : ''}{rule.rate_adjustment}%
                      </span>
                    </TableCell>
                    <TableCell>
                      {rule.is_active ? (
                        <Badge className="bg-green-100 text-green-800">Active</Badge>
                      ) : (
                        <Badge variant="secondary">Inactive</Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEdit(rule)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-red-600"
                          onClick={() => handleDelete(rule.id, rule.rule_name)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={10} className="text-center py-8 text-gray-500">
                    No pricing rules found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>

          {/* Pagination */}
          {data && data.items.length > 0 && (
            <div className="flex items-center justify-between px-6 py-4 border-t">
              <p className="text-sm text-gray-600">
                Showing {((page - 1) * 20) + 1} to {Math.min(page * 20, data.total)} of {data.total} rules
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page === 1}
                  onClick={() => setPage(page - 1)}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page * 20 >= data.total}
                  onClick={() => setPage(page + 1)}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Rule Form Modal */}
      {showModal && (
        <RuleFormModal
          rule={editingRule}
          policies={policies?.items || []}
          onClose={() => {
            setShowModal(false)
            setEditingRule(null)
          }}
          onSuccess={() => {
            queryClient.invalidateQueries({ queryKey: ['pricing-rules'] })
          }}
        />
      )}

      {/* Pricing Calculator */}
      {showCalculator && (
        <PricingCalculator onClose={() => setShowCalculator(false)} />
      )}
    </DashboardLayout>
  )
}

function StatCard({ label, value, color = 'blue', icon: Icon = TrendingUp }: any) {
  const colors = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
  }

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">{label}</p>
            <p className="text-2xl font-bold mt-1">{value}</p>
          </div>
          <div className={`h-12 w-12 rounded-lg ${colors[color as keyof typeof colors]} flex items-center justify-center`}>
            <Icon className="h-6 w-6" />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function RuleFormModal({ rule, policies, onClose, onSuccess }: any) {
  const [formData, setFormData] = useState({
    rule_code: rule?.rule_code || '',
    rule_name: rule?.rule_name || '',
    policy_id: rule?.policy_id || '',
    priority: rule?.priority || 100,
    min_risk_grade: rule?.min_risk_grade || '',
    max_risk_grade: rule?.max_risk_grade || '',
    min_cibil_score: rule?.min_cibil_score || '',
    max_cibil_score: rule?.max_cibil_score || '',
    min_dti_ratio: rule?.min_dti_ratio || '',
    max_dti_ratio: rule?.max_dti_ratio || '',
    rate_adjustment: rule?.rate_adjustment || 0,
    is_active: rule?.is_active ?? true,
  })

  const mutation = useMutation({
    mutationFn: (data: any) =>
      rule
        ? riskService.updatePricingRule(rule.id, data)
        : riskService.createPricingRule(data),
    onSuccess: () => {
      toast.success(`Pricing rule ${rule ? 'updated' : 'created'} successfully`)
      onSuccess()
      onClose()
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to save pricing rule')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate(formData)
  }

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{rule ? 'Edit' : 'Create'} Pricing Rule</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium mb-1 block">Rule Code *</label>
              <Input
                value={formData.rule_code}
                onChange={(e) => setFormData({ ...formData, rule_code: e.target.value })}
                required
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Rule Name *</label>
              <Input
                value={formData.rule_name}
                onChange={(e) => setFormData({ ...formData, rule_name: e.target.value })}
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium mb-1 block">Credit Policy *</label>
              <select
                value={formData.policy_id}
                onChange={(e) => setFormData({ ...formData, policy_id: parseInt(e.target.value) })}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                required
              >
                <option value="">Select Policy</option>
                {policies.map((p: any) => (
                  <option key={p.id} value={p.id}>{p.policy_name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Priority *</label>
              <Input
                type="number"
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) })}
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium mb-1 block">Min Risk Grade</label>
              <Input
                value={formData.min_risk_grade}
                onChange={(e) => setFormData({ ...formData, min_risk_grade: e.target.value })}
                placeholder="A+"
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Max Risk Grade</label>
              <Input
                value={formData.max_risk_grade}
                onChange={(e) => setFormData({ ...formData, max_risk_grade: e.target.value })}
                placeholder="B"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium mb-1 block">Min CIBIL Score</label>
              <Input
                type="number"
                value={formData.min_cibil_score}
                onChange={(e) => setFormData({ ...formData, min_cibil_score: parseInt(e.target.value) })}
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Max CIBIL Score</label>
              <Input
                type="number"
                value={formData.max_cibil_score}
                onChange={(e) => setFormData({ ...formData, max_cibil_score: parseInt(e.target.value) })}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium mb-1 block">Min DTI Ratio (%)</label>
              <Input
                type="number"
                step="0.1"
                value={formData.min_dti_ratio}
                onChange={(e) => setFormData({ ...formData, min_dti_ratio: parseFloat(e.target.value) })}
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Max DTI Ratio (%)</label>
              <Input
                type="number"
                step="0.1"
                value={formData.max_dti_ratio}
                onChange={(e) => setFormData({ ...formData, max_dti_ratio: parseFloat(e.target.value) })}
              />
            </div>
          </div>

          <div>
            <label className="text-sm font-medium mb-1 block">Rate Adjustment (%) *</label>
            <Input
              type="number"
              step="0.01"
              value={formData.rate_adjustment}
              onChange={(e) => setFormData({ ...formData, rate_adjustment: parseFloat(e.target.value) })}
              required
            />
            <p className="text-xs text-gray-500 mt-1">Positive = premium, Negative = discount</p>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="is_active"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              className="h-4 w-4 rounded border-gray-300"
            />
            <label htmlFor="is_active" className="text-sm font-medium">Active</label>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? 'Saving...' : 'Save Rule'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

function PricingCalculator({ onClose }: { onClose: () => void }) {
  const [inputs, setInputs] = useState({
    policy_id: '',
    cibil_score: 750,
    dti_ratio: 40,
    risk_grade: 'B+',
  })
  const [result, setResult] = useState<any>(null)

  const handleCalculate = () => {
    // Simulate pricing calculation
    const baseRate = 12.5
    const adjustment = 1.25
    setResult({
      base_rate: baseRate,
      total_adjustment: adjustment,
      final_rate: baseRate + adjustment,
      matched_rules: [
        { rule_name: 'CIBIL 700-800 Premium', adjustment: 0.75 },
        { rule_name: 'DTI 35-45 Adjustment', adjustment: 0.5 },
      ],
    })
  }

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Pricing Calculator</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium mb-1 block">CIBIL Score</label>
            <Input
              type="number"
              value={inputs.cibil_score}
              onChange={(e) => setInputs({ ...inputs, cibil_score: parseInt(e.target.value) })}
            />
          </div>
          <div>
            <label className="text-sm font-medium mb-1 block">DTI Ratio (%)</label>
            <Input
              type="number"
              value={inputs.dti_ratio}
              onChange={(e) => setInputs({ ...inputs, dti_ratio: parseFloat(e.target.value) })}
            />
          </div>
          <div>
            <label className="text-sm font-medium mb-1 block">Risk Grade</label>
            <Input
              value={inputs.risk_grade}
              onChange={(e) => setInputs({ ...inputs, risk_grade: e.target.value })}
            />
          </div>
          <Button onClick={handleCalculate} className="w-full">
            Calculate
          </Button>

          {result && (
            <Card className="bg-blue-50">
              <CardContent className="pt-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Base Rate:</span>
                    <span className="font-medium">{result.base_rate}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Total Adjustment:</span>
                    <span className="font-medium text-red-600">+{result.total_adjustment}%</span>
                  </div>
                  <div className="flex justify-between text-lg font-bold border-t pt-2">
                    <span>Final Rate:</span>
                    <span className="text-blue-600">{result.final_rate}%</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
