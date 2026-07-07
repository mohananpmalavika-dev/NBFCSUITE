'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { ArrowLeft, Download, TrendingDown } from 'lucide-react'
import { almService, type InterestRateScenario } from '@/services/alm.service'
import { toast } from 'sonner'

const MOCK_SCENARIOS = [
  { scenario: 'base', nii_impact: 0, mve_impact: 0, risk_level: 'low' },
  { scenario: 'parallel_up_100', nii_impact: -5.2, mve_impact: -8.5, risk_level: 'medium' },
  { scenario: 'parallel_down_100', nii_impact: 5.8, mve_impact: 9.2, risk_level: 'low' },
  { scenario: 'parallel_up_200', nii_impact: -12.5, mve_impact: -18.3, risk_level: 'high' },
  { scenario: 'parallel_down_200', nii_impact: 11.2, mve_impact: 17.5, risk_level: 'low' },
  { scenario: 'steepening', nii_impact: -3.5, mve_impact: -6.8, risk_level: 'medium' },
  { scenario: 'flattening', nii_impact: 2.8, mve_impact: 4.2, risk_level: 'low' },
]

export default function InterestRateRiskPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [reportDate, setReportDate] = useState(new Date().toISOString().split('T')[0])
  const [scenarios, setScenarios] = useState(MOCK_SCENARIOS)

  const handleAnalyze = async () => {
    try {
      setLoading(true)
      const response = await almService.getInterestRateRisk(reportDate)
      setScenarios(response.data || MOCK_SCENARIOS)
      toast.success('Interest rate risk analyzed')
    } catch (error: any) {
      toast.error(error.message || 'Failed to analyze')
      setScenarios(MOCK_SCENARIOS)
    } finally {
      setLoading(false)
    }
  }

  const formatPercentage = (value: number) => `${value > 0 ? '+' : ''}${value.toFixed(2)}%`
  const worstCase = scenarios.reduce((min, s) => s.nii_impact < min.nii_impact ? s : min, scenarios[0])

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Interest Rate Risk</h1>
            <p className="text-muted-foreground">Stress testing & scenario analysis</p>
          </div>
        </div>
        <Button variant="outline"><Download className="mr-2 h-4 w-4" />Export</Button>
      </div>

      <Card>
        <CardHeader><CardTitle>Analysis Parameters</CardTitle></CardHeader>
        <CardContent>
          <div className="flex items-end space-x-4 max-w-md">
            <div className="flex-1 space-y-2">
              <Label htmlFor="reportDate">Report Date</Label>
              <Input id="reportDate" type="date" value={reportDate} onChange={(e) => setReportDate(e.target.value)} />
            </div>
            <Button onClick={handleAnalyze} disabled={loading}>
              <TrendingDown className="mr-2 h-4 w-4" />{loading ? 'Analyzing...' : 'Analyze'}
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-3"><CardTitle className="text-sm font-medium">Scenarios Tested</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{scenarios.length}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3"><CardTitle className="text-sm font-medium">Worst Case Impact</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold text-red-600">{formatPercentage(worstCase.nii_impact)}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3"><CardTitle className="text-sm font-medium">High Risk Scenarios</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold text-orange-600">{scenarios.filter(s => s.risk_level === 'high').length}</div></CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Scenario Analysis</CardTitle><CardDescription>Impact on NII and MVE</CardDescription></CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Scenario</TableHead>
                <TableHead className="text-right">NII Impact (%)</TableHead>
                <TableHead className="text-right">MVE Impact (%)</TableHead>
                <TableHead>Risk Level</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {scenarios.map((scenario) => (
                <TableRow key={scenario.scenario}>
                  <TableCell className="font-medium">{almService.getScenarioLabel(scenario.scenario as InterestRateScenario)}</TableCell>
                  <TableCell className={`text-right font-semibold ${scenario.nii_impact < 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {formatPercentage(scenario.nii_impact)}
                  </TableCell>
                  <TableCell className={`text-right font-semibold ${scenario.mve_impact < 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {formatPercentage(scenario.mve_impact)}
                  </TableCell>
                  <TableCell><Badge className={almService.getRiskLevelColor(scenario.risk_level)}>{scenario.risk_level.toUpperCase()}</Badge></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
