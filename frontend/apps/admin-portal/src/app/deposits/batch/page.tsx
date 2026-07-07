'use client'

import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { 
  PlayCircle, 
  Calendar, 
  DollarSign,
  AlertCircle,
  RefreshCw,
  CheckCircle,
  XCircle,
  Clock,
  FileText
} from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { depositService } from '@/services/deposit.service'
import { useToast } from '@/hooks/use-toast'
import { format } from 'date-fns'
import { Alert, AlertDescription } from '@/components/ui/alert'

export default function BatchOperationsPage() {
  const { toast } = useToast()
  const [activeTab, setActiveTab] = useState('maturity')

  // Maturity processing state
  const [maturityDate, setMaturityDate] = useState(format(new Date(), 'yyyy-MM-dd'))
  const [autoRenew, setAutoRenew] = useState(false)
  const [maturityDryRun, setMaturityDryRun] = useState(true)

  // TDS calculation state
  const [tdsQuarter, setTdsQuarter] = useState(1)
  const [tdsFinancialYear, setTdsFinancialYear] = useState('2025-26')
  const [tdsDryRun, setTdsDryRun] = useState(true)

  // Dormancy check state
  const [dormancyDate, setDormancyDate] = useState(format(new Date(), 'yyyy-MM-dd'))
  const [dormancyPeriod, setDormancyPeriod] = useState(24)

  // Penalty application state
  const [penaltyDate, setPenaltyDate] = useState(format(new Date(), 'yyyy-MM-dd'))
  const [penaltyTypes, setPenaltyTypes] = useState<string[]>([])

  // MIS payout state
  const [misPayoutMonth, setMisPayoutMonth] = useState(format(new Date(), 'yyyy-MM'))
  const [misDryRun, setMisDryRun] = useState(true)

  // Process maturity batch mutation
  const processMaturityMutation = useMutation({
    mutationFn: () =>
      depositService.processMaturityBatch({
        maturity_date: maturityDate,
        auto_renew: autoRenew,
        dry_run: maturityDryRun,
      }),
    onSuccess: (data) => {
      toast({
        title: 'Success',
        description: maturityDryRun
          ? `Dry run completed. ${data.data?.accounts_to_process || 0} accounts identified.`
          : `Maturity processing completed successfully.`,
      })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to process maturity batch',
        variant: 'destructive',
      })
    },
  })

  // Calculate TDS batch mutation
  const calculateTDSMutation = useMutation({
    mutationFn: () =>
      depositService.calculateTDSBatch({
        quarter: tdsQuarter,
        financial_year: tdsFinancialYear,
        dry_run: tdsDryRun,
      }),
    onSuccess: (data) => {
      toast({
        title: 'Success',
        description: tdsDryRun
          ? `Dry run completed. TDS to be deducted: ₹${data.data?.total_tds || 0}`
          : `TDS calculation completed successfully.`,
      })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to calculate TDS',
        variant: 'destructive',
      })
    },
  })

  // Check dormancy batch mutation
  const checkDormancyMutation = useMutation({
    mutationFn: () =>
      depositService.checkDormancyBatch({
        check_date: dormancyDate,
        dormancy_period_months: dormancyPeriod,
      }),
    onSuccess: (data) => {
      toast({
        title: 'Success',
        description: `Dormancy check completed. ${data.data?.dormant_accounts || 0} dormant accounts identified.`,
      })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to check dormancy',
        variant: 'destructive',
      })
    },
  })

  // Apply penalties batch mutation
  const applyPenaltiesMutation = useMutation({
    mutationFn: () =>
      depositService.applyPenaltiesBatch({
        penalty_date: penaltyDate,
        penalty_types: penaltyTypes.length > 0 ? penaltyTypes : undefined,
      }),
    onSuccess: (data) => {
      toast({
        title: 'Success',
        description: `Penalties applied successfully. ${data.data?.penalties_applied || 0} penalties processed.`,
      })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to apply penalties',
        variant: 'destructive',
      })
    },
  })

  // Process MIS payout batch mutation
  const processMISPayoutMutation = useMutation({
    mutationFn: () =>
      depositService.processMISPayoutBatch({
        payout_month: misPayoutMonth,
        dry_run: misDryRun,
      }),
    onSuccess: (data) => {
      toast({
        title: 'Success',
        description: misDryRun
          ? `Dry run completed. ${data.data?.accounts_to_process || 0} MIS accounts identified.`
          : `MIS payout processing completed successfully.`,
      })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to process MIS payout',
        variant: 'destructive',
      })
    },
  })

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Batch Operations</h1>
            <p className="text-gray-600 mt-1">
              Automated processing for maturity, TDS, dormancy, and penalties
            </p>
          </div>
        </div>

        {/* Warning Card */}
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            <strong>Important:</strong> Always run in "Dry Run" mode first to preview changes before
            executing actual batch operations. Dry run mode will show you what will happen without
            making any changes.
          </AlertDescription>
        </Alert>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="maturity">
              <Calendar className="h-4 w-4 mr-2" />
              Maturity
            </TabsTrigger>
            <TabsTrigger value="tds">
              <DollarSign className="h-4 w-4 mr-2" />
              TDS
            </TabsTrigger>
            <TabsTrigger value="dormancy">
              <Clock className="h-4 w-4 mr-2" />
              Dormancy
            </TabsTrigger>
            <TabsTrigger value="penalties">
              <AlertCircle className="h-4 w-4 mr-2" />
              Penalties
            </TabsTrigger>
            <TabsTrigger value="mis">
              <RefreshCw className="h-4 w-4 mr-2" />
              MIS Payout
            </TabsTrigger>
          </TabsList>

          {/* Maturity Processing Tab */}
          <TabsContent value="maturity" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Maturity Processing</CardTitle>
                <p className="text-sm text-gray-600 mt-1">
                  Process accounts reaching maturity date
                </p>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="maturityDate">Maturity Date</Label>
                  <Input
                    id="maturityDate"
                    type="date"
                    value={maturityDate}
                    onChange={(e) => setMaturityDate(e.target.value)}
                    max={format(new Date(), 'yyyy-MM-dd')}
                  />
                  <p className="text-xs text-gray-500">
                    Process all accounts maturing on this date
                  </p>
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="autoRenew"
                    checked={autoRenew}
                    onChange={(e) => setAutoRenew(e.target.checked)}
                    className="rounded border-gray-300"
                  />
                  <Label htmlFor="autoRenew" className="cursor-pointer">
                    Auto-renew eligible accounts (if configured)
                  </Label>
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="maturityDryRun"
                    checked={maturityDryRun}
                    onChange={(e) => setMaturityDryRun(e.target.checked)}
                    className="rounded border-gray-300"
                  />
                  <Label htmlFor="maturityDryRun" className="cursor-pointer">
                    Dry run mode (preview without executing)
                  </Label>
                </div>

                {maturityDryRun && (
                  <Alert className="bg-blue-50 border-blue-200">
                    <AlertCircle className="h-4 w-4 text-blue-600" />
                    <AlertDescription className="text-blue-800">
                      Dry run mode is enabled. This will show you which accounts will be processed without
                      making any actual changes.
                    </AlertDescription>
                  </Alert>
                )}

                <Button
                  onClick={() => processMaturityMutation.mutate()}
                  disabled={processMaturityMutation.isPending}
                  className="w-full"
                  size="lg"
                >
                  {processMaturityMutation.isPending ? (
                    <>
                      <RefreshCw className="h-5 w-5 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <PlayCircle className="h-5 w-5 mr-2" />
                      {maturityDryRun ? 'Run Dry Run' : 'Process Maturity'}
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* TDS Calculation Tab */}
          <TabsContent value="tds" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>TDS Calculation</CardTitle>
                <p className="text-sm text-gray-600 mt-1">
                  Calculate and deduct TDS for a quarter
                </p>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="tdsFinancialYear">Financial Year</Label>
                    <Select
                      value={tdsFinancialYear}
                      onValueChange={setTdsFinancialYear}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {['2025-26', '2024-25', '2023-24'].map((fy) => (
                          <SelectItem key={fy} value={fy}>
                            FY {fy}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="tdsQuarter">Quarter</Label>
                    <Select
                      value={tdsQuarter.toString()}
                      onValueChange={(value) => setTdsQuarter(parseInt(value))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1">Q1 (Apr - Jun)</SelectItem>
                        <SelectItem value="2">Q2 (Jul - Sep)</SelectItem>
                        <SelectItem value="3">Q3 (Oct - Dec)</SelectItem>
                        <SelectItem value="4">Q4 (Jan - Mar)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="tdsDryRun"
                    checked={tdsDryRun}
                    onChange={(e) => setTdsDryRun(e.target.checked)}
                    className="rounded border-gray-300"
                  />
                  <Label htmlFor="tdsDryRun" className="cursor-pointer">
                    Dry run mode (preview TDS calculation)
                  </Label>
                </div>

                {tdsDryRun && (
                  <Alert className="bg-blue-50 border-blue-200">
                    <AlertCircle className="h-4 w-4 text-blue-600" />
                    <AlertDescription className="text-blue-800">
                      Dry run will calculate TDS amounts without deducting them from accounts.
                    </AlertDescription>
                  </Alert>
                )}

                <Button
                  onClick={() => calculateTDSMutation.mutate()}
                  disabled={calculateTDSMutation.isPending}
                  className="w-full"
                  size="lg"
                >
                  {calculateTDSMutation.isPending ? (
                    <>
                      <RefreshCw className="h-5 w-5 mr-2 animate-spin" />
                      Calculating...
                    </>
                  ) : (
                    <>
                      <PlayCircle className="h-5 w-5 mr-2" />
                      {tdsDryRun ? 'Calculate TDS (Dry Run)' : 'Calculate & Deduct TDS'}
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Dormancy Check Tab */}
          <TabsContent value="dormancy" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Dormancy Check</CardTitle>
                <p className="text-sm text-gray-600 mt-1">
                  Identify and mark dormant accounts
                </p>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="dormancyDate">Check Date</Label>
                  <Input
                    id="dormancyDate"
                    type="date"
                    value={dormancyDate}
                    onChange={(e) => setDormancyDate(e.target.value)}
                    max={format(new Date(), 'yyyy-MM-dd')}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="dormancyPeriod">Dormancy Period (Months)</Label>
                  <Select
                    value={dormancyPeriod.toString()}
                    onValueChange={(value) => setDormancyPeriod(parseInt(value))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="12">12 months</SelectItem>
                      <SelectItem value="18">18 months</SelectItem>
                      <SelectItem value="24">24 months (default)</SelectItem>
                      <SelectItem value="36">36 months</SelectItem>
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-gray-500">
                    Accounts with no transactions for this period will be marked as dormant
                  </p>
                </div>

                <Alert className="bg-yellow-50 border-yellow-200">
                  <AlertCircle className="h-4 w-4 text-yellow-600" />
                  <AlertDescription className="text-yellow-800">
                    Dormant accounts identified will be marked but not frozen. Review the list before
                    taking any action.
                  </AlertDescription>
                </Alert>

                <Button
                  onClick={() => checkDormancyMutation.mutate()}
                  disabled={checkDormancyMutation.isPending}
                  className="w-full"
                  size="lg"
                >
                  {checkDormancyMutation.isPending ? (
                    <>
                      <RefreshCw className="h-5 w-5 mr-2 animate-spin" />
                      Checking...
                    </>
                  ) : (
                    <>
                      <PlayCircle className="h-5 w-5 mr-2" />
                      Check for Dormant Accounts
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Penalties Tab */}
          <TabsContent value="penalties" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Apply Penalties</CardTitle>
                <p className="text-sm text-gray-600 mt-1">
                  Apply penalties for violations and missed payments
                </p>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="penaltyDate">Penalty Date</Label>
                  <Input
                    id="penaltyDate"
                    type="date"
                    value={penaltyDate}
                    onChange={(e) => setPenaltyDate(e.target.value)}
                    max={format(new Date(), 'yyyy-MM-dd')}
                  />
                </div>

                <div className="space-y-2">
                  <Label>Penalty Types (Leave empty for all)</Label>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="rdMissed"
                        checked={penaltyTypes.includes('rd_missed_installment')}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setPenaltyTypes([...penaltyTypes, 'rd_missed_installment'])
                          } else {
                            setPenaltyTypes(penaltyTypes.filter((t) => t !== 'rd_missed_installment'))
                          }
                        }}
                        className="rounded border-gray-300"
                      />
                      <Label htmlFor="rdMissed" className="cursor-pointer">
                        RD Missed Installment
                      </Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="minBalance"
                        checked={penaltyTypes.includes('min_balance_violation')}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setPenaltyTypes([...penaltyTypes, 'min_balance_violation'])
                          } else {
                            setPenaltyTypes(penaltyTypes.filter((t) => t !== 'min_balance_violation'))
                          }
                        }}
                        className="rounded border-gray-300"
                      />
                      <Label htmlFor="minBalance" className="cursor-pointer">
                        Minimum Balance Violation
                      </Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="excessWithdrawal"
                        checked={penaltyTypes.includes('excess_withdrawal')}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setPenaltyTypes([...penaltyTypes, 'excess_withdrawal'])
                          } else {
                            setPenaltyTypes(penaltyTypes.filter((t) => t !== 'excess_withdrawal'))
                          }
                        }}
                        className="rounded border-gray-300"
                      />
                      <Label htmlFor="excessWithdrawal" className="cursor-pointer">
                        Excess Withdrawal
                      </Label>
                    </div>
                  </div>
                </div>

                <Alert className="bg-red-50 border-red-200">
                  <AlertCircle className="h-4 w-4 text-red-600" />
                  <AlertDescription className="text-red-800">
                    Penalties will be automatically deducted from accounts. This action cannot be undone.
                  </AlertDescription>
                </Alert>

                <Button
                  onClick={() => applyPenaltiesMutation.mutate()}
                  disabled={applyPenaltiesMutation.isPending}
                  className="w-full"
                  size="lg"
                  variant="destructive"
                >
                  {applyPenaltiesMutation.isPending ? (
                    <>
                      <RefreshCw className="h-5 w-5 mr-2 animate-spin" />
                      Applying...
                    </>
                  ) : (
                    <>
                      <PlayCircle className="h-5 w-5 mr-2" />
                      Apply Penalties
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* MIS Payout Tab */}
          <TabsContent value="mis" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>MIS Payout Processing</CardTitle>
                <p className="text-sm text-gray-600 mt-1">
                  Process monthly interest payout for MIS accounts
                </p>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="misPayoutMonth">Payout Month</Label>
                  <Input
                    id="misPayoutMonth"
                    type="month"
                    value={misPayoutMonth}
                    onChange={(e) => setMisPayoutMonth(e.target.value)}
                    max={format(new Date(), 'yyyy-MM')}
                  />
                  <p className="text-xs text-gray-500">
                    Process MIS payouts for this month
                  </p>
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="misDryRun"
                    checked={misDryRun}
                    onChange={(e) => setMisDryRun(e.target.checked)}
                    className="rounded border-gray-300"
                  />
                  <Label htmlFor="misDryRun" className="cursor-pointer">
                    Dry run mode (preview payout calculation)
                  </Label>
                </div>

                {misDryRun && (
                  <Alert className="bg-blue-50 border-blue-200">
                    <AlertCircle className="h-4 w-4 text-blue-600" />
                    <AlertDescription className="text-blue-800">
                      Dry run will calculate payout amounts without processing actual transfers.
                    </AlertDescription>
                  </Alert>
                )}

                <Button
                  onClick={() => processMISPayoutMutation.mutate()}
                  disabled={processMISPayoutMutation.isPending}
                  className="w-full"
                  size="lg"
                >
                  {processMISPayoutMutation.isPending ? (
                    <>
                      <RefreshCw className="h-5 w-5 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <PlayCircle className="h-5 w-5 mr-2" />
                      {misDryRun ? 'Calculate Payout (Dry Run)' : 'Process MIS Payout'}
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Info Card */}
        <Card className="bg-gray-50 border-gray-200">
          <CardContent className="pt-6">
            <div className="flex gap-3">
              <FileText className="h-5 w-5 text-gray-600 mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-gray-900">Best Practices</h3>
                <ul className="text-sm text-gray-700 mt-2 space-y-1">
                  <li>• Always run batch operations during off-peak hours</li>
                  <li>• Use dry run mode first to verify the changes</li>
                  <li>• Review the results before executing actual operations</li>
                  <li>• Keep audit logs of all batch operations</li>
                  <li>• Schedule regular batch jobs for automated processing</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
