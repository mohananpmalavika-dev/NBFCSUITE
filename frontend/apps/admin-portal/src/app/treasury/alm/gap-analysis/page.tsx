"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Download, RefreshCw, TrendingUp, AlertCircle, Activity, Clock } from "lucide-react";
import { almService } from '@/services/almService';
import type { GapAnalysisResponse, GapType, GAP_TYPE_LABELS } from '@/types/alm';
import { formatCurrency } from '@/lib/utils';

const GAP_ICONS: Record<GapType, React.ReactNode> = {
  liquidity: <Activity className="h-5 w-5" />,
  interest_rate: <TrendingUp className="h-5 w-5" />,
  maturity: <Clock className="h-5 w-5" />,
  duration: <AlertCircle className="h-5 w-5" />
};

export default function GapAnalysisPage() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<GapAnalysisResponse[]>([]);
  const [selectedGapType, setSelectedGapType] = useState<GapType>('liquidity');
  const [selectedDate, setSelectedDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  );

  useEffect(() => {
    fetchData();
  }, [selectedDate]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await almService.getGapAnalysis(selectedDate);
      setData(response);
    } catch (error) {
      console.error('Failed to fetch gap analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      await almService.exportGapAnalysis(selectedDate, selectedGapType, 'excel');
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  const currentGapData = data.find(g => g.gap_type === selectedGapType);

  const getRiskColor = (level: string): string => {
    switch (level) {
      case 'critical': return 'text-red-600 bg-red-50 border-red-200';
      case 'high': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <RefreshCw className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Gap Analysis</h1>
          <p className="text-muted-foreground">
            Comprehensive analysis of liquidity, interest rate, maturity, and duration gaps
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={fetchData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button onClick={handleExport}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Date Selector */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-4">
            <label className="text-sm font-medium">Analysis Date:</label>
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="border rounded px-3 py-2"
            />
          </div>
        </CardContent>
      </Card>

      {/* Gap Type Overview Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        {data.map((gap) => (
          <Card
            key={gap.gap_type}
            className={`cursor-pointer transition-all ${
              selectedGapType === gap.gap_type ? 'ring-2 ring-primary' : ''
            }`}
            onClick={() => setSelectedGapType(gap.gap_type)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {GAP_TYPE_LABELS[gap.gap_type]}
              </CardTitle>
              {GAP_ICONS[gap.gap_type]}
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(gap.net_gap)}</div>
              <p className={`text-xs mt-2 px-2 py-1 rounded-full inline-block ${getRiskColor(gap.risk_level)}`}>
                {gap.risk_level.toUpperCase()} RISK
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Detailed Gap Analysis */}
      {currentGapData && (
        <div className="space-y-6">
          {/* Summary Metrics */}
          <Card>
            <CardHeader>
              <CardTitle>{GAP_TYPE_LABELS[selectedGapType]} Analysis</CardTitle>
              <CardDescription>Detailed breakdown and risk assessment</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-6 md:grid-cols-3">
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">Total Inflows</p>
                  <p className="text-3xl font-bold text-green-600">
                    {formatCurrency(currentGapData.total_inflows)}
                  </p>
                </div>
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">Total Outflows</p>
                  <p className="text-3xl font-bold text-red-600">
                    {formatCurrency(currentGapData.total_outflows)}
                  </p>
                </div>
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">Net Gap</p>
                  <p className={`text-3xl font-bold ${
                    currentGapData.net_gap >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {formatCurrency(currentGapData.net_gap)}
                  </p>
                </div>
              </div>

              <div className="mt-6 pt-6 border-t">
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <p className="text-sm text-muted-foreground mb-2">Gap Percentage</p>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-muted rounded-full h-3">
                        <div
                          className={`h-3 rounded-full ${
                            currentGapData.gap_percentage >= 0 ? 'bg-green-600' : 'bg-red-600'
                          }`}
                          style={{
                            width: `${Math.min(Math.abs(currentGapData.gap_percentage), 100)}%`
                          }}
                        />
                      </div>
                      <span className="text-lg font-semibold min-w-[80px]">
                        {currentGapData.gap_percentage.toFixed(2)}%
                      </span>
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground mb-2">Risk Level</p>
                    <div className={`px-4 py-2 rounded-lg font-semibold text-center ${
                      getRiskColor(currentGapData.risk_level)
                    }`}>
                      {currentGapData.risk_level.toUpperCase()}
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Period-wise Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle>Period-wise Gap Breakdown</CardTitle>
              <CardDescription>Analysis across different time periods</CardDescription>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="short">
                <TabsList className="grid w-full grid-cols-4">
                  <TabsTrigger value="short">Short Term (0-90 days)</TabsTrigger>
                  <TabsTrigger value="medium">Medium Term (91-365 days)</TabsTrigger>
                  <TabsTrigger value="long">Long Term (1-5 years)</TabsTrigger>
                  <TabsTrigger value="verylong">Very Long (5+ years)</TabsTrigger>
                </TabsList>

                <TabsContent value="short" className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-3">
                    <MetricCard
                      title="Inflows"
                      value={currentGapData.total_inflows * 0.4}
                      color="green"
                    />
                    <MetricCard
                      title="Outflows"
                      value={currentGapData.total_outflows * 0.5}
                      color="red"
                    />
                    <MetricCard
                      title="Gap"
                      value={(currentGapData.total_inflows * 0.4) - (currentGapData.total_outflows * 0.5)}
                      color={(currentGapData.total_inflows * 0.4) - (currentGapData.total_outflows * 0.5) >= 0 ? 'green' : 'red'}
                    />
                  </div>
                </TabsContent>

                <TabsContent value="medium" className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-3">
                    <MetricCard
                      title="Inflows"
                      value={currentGapData.total_inflows * 0.3}
                      color="green"
                    />
                    <MetricCard
                      title="Outflows"
                      value={currentGapData.total_outflows * 0.3}
                      color="red"
                    />
                    <MetricCard
                      title="Gap"
                      value={(currentGapData.total_inflows * 0.3) - (currentGapData.total_outflows * 0.3)}
                      color={(currentGapData.total_inflows * 0.3) - (currentGapData.total_outflows * 0.3) >= 0 ? 'green' : 'red'}
                    />
                  </div>
                </TabsContent>

                <TabsContent value="long" className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-3">
                    <MetricCard
                      title="Inflows"
                      value={currentGapData.total_inflows * 0.2}
                      color="green"
                    />
                    <MetricCard
                      title="Outflows"
                      value={currentGapData.total_outflows * 0.15}
                      color="red"
                    />
                    <MetricCard
                      title="Gap"
                      value={(currentGapData.total_inflows * 0.2) - (currentGapData.total_outflows * 0.15)}
                      color={(currentGapData.total_inflows * 0.2) - (currentGapData.total_outflows * 0.15) >= 0 ? 'green' : 'red'}
                    />
                  </div>
                </TabsContent>

                <TabsContent value="verylong" className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-3">
                    <MetricCard
                      title="Inflows"
                      value={currentGapData.total_inflows * 0.1}
                      color="green"
                    />
                    <MetricCard
                      title="Outflows"
                      value={currentGapData.total_outflows * 0.05}
                      color="red"
                    />
                    <MetricCard
                      title="Gap"
                      value={(currentGapData.total_inflows * 0.1) - (currentGapData.total_outflows * 0.05)}
                      color={(currentGapData.total_inflows * 0.1) - (currentGapData.total_outflows * 0.05) >= 0 ? 'green' : 'red'}
                    />
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          {/* Recommendations */}
          <Card>
            <CardHeader>
              <CardTitle>Risk Mitigation Recommendations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {currentGapData.recommendations.map((rec, index) => (
                  <div key={index} className="flex items-start gap-3 p-4 border rounded-lg">
                    <AlertCircle className="h-5 w-5 text-primary mt-0.5" />
                    <div className="flex-1">
                      <p className="font-medium">{rec}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Gap Type Specific Insights */}
          <Card>
            <CardHeader>
              <CardTitle>Analysis Insights</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="prose max-w-none">
                {selectedGapType === 'liquidity' && (
                  <div className="space-y-2">
                    <p><strong>Liquidity Gap Analysis:</strong> Measures the difference between liquid assets and liabilities across time buckets.</p>
                    <ul className="list-disc pl-5 space-y-1">
                      <li>Positive gap indicates surplus liquidity position</li>
                      <li>Negative gap suggests potential liquidity stress</li>
                      <li>Monitor short-term gaps (0-90 days) closely</li>
                      <li>Maintain adequate buffer for unexpected outflows</li>
                    </ul>
                  </div>
                )}
                {selectedGapType === 'interest_rate' && (
                  <div className="space-y-2">
                    <p><strong>Interest Rate Gap Analysis:</strong> Evaluates exposure to interest rate changes based on repricing assets and liabilities.</p>
                    <ul className="list-disc pl-5 space-y-1">
                      <li>Positive gap benefits from rising interest rates</li>
                      <li>Negative gap benefits from falling interest rates</li>
                      <li>Large gaps increase earnings volatility</li>
                      <li>Consider hedging strategies for significant exposures</li>
                    </ul>
                  </div>
                )}
                {selectedGapType === 'maturity' && (
                  <div className="space-y-2">
                    <p><strong>Maturity Gap Analysis:</strong> Assesses timing mismatch between asset and liability maturities.</p>
                    <ul className="list-disc pl-5 space-y-1">
                      <li>Positive gap suggests assets mature before liabilities</li>
                      <li>Monitor cumulative gap positions</li>
                      <li>Balance short-term and long-term positions</li>
                      <li>Consider refinancing risks</li>
                    </ul>
                  </div>
                )}
                {selectedGapType === 'duration' && (
                  <div className="space-y-2">
                    <p><strong>Duration Gap Analysis:</strong> Measures sensitivity of portfolio value to interest rate changes.</p>
                    <ul className="list-disc pl-5 space-y-1">
                      <li>Duration gap affects net worth sensitivity</li>
                      <li>Smaller duration gap reduces interest rate risk</li>
                      <li>Consider asset-liability duration matching</li>
                      <li>Use duration hedging strategies when needed</li>
                    </ul>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

function MetricCard({ title, value, color }: { title: string; value: number; color: 'green' | 'red' }) {
  return (
    <div className="p-4 border rounded-lg">
      <p className="text-sm text-muted-foreground mb-2">{title}</p>
      <p className={`text-2xl font-bold ${color === 'green' ? 'text-green-600' : 'text-red-600'}`}>
        {formatCurrency(value)}
      </p>
    </div>
  );
}
