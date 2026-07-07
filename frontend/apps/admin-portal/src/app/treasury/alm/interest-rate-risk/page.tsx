"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Download, RefreshCw, TrendingUp, TrendingDown, Activity } from "lucide-react";
import { almService } from '@/services/almService';
import type { InterestRateRiskResponse, InterestRateScenario, SCENARIO_LABELS } from '@/types/alm';
import { formatCurrency } from '@/lib/utils';

const SCENARIO_DESCRIPTIONS: Record<InterestRateScenario, string> = {
  base: 'Current interest rate environment',
  shock_up_100: '+100 basis points parallel shift',
  shock_down_100: '-100 basis points parallel shift',
  shock_up_200: '+200 basis points parallel shift',
  shock_down_200: '-200 basis points parallel shift',
  gradual_rise: 'Gradual increase over 12 months',
  gradual_fall: 'Gradual decrease over 12 months'
};

export default function InterestRateRiskPage() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<InterestRateRiskResponse[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<InterestRateScenario>('base');
  const [selectedDate, setSelectedDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  );

  useEffect(() => {
    fetchData();
  }, [selectedDate]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await almService.getInterestRateRisk(selectedDate);
      setData(response);
    } catch (error) {
      console.error('Failed to fetch interest rate risk:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      await almService.exportInterestRateRisk(selectedDate, selectedScenario, 'excel');
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  const currentScenarioData = data.find(d => d.scenario === selectedScenario);
  const baseScenario = data.find(d => d.scenario === 'base');

  const calculateImpactPercentage = (impact: number, base: number): string => {
    if (base === 0) return '0.0';
    return ((impact / base) * 100).toFixed(2);
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
          <h1 className="text-3xl font-bold tracking-tight">Interest Rate Risk</h1>
          <p className="text-muted-foreground">
            Stress testing and impact analysis across multiple interest rate scenarios
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

      {/* Scenario Selector */}
      <Card>
        <CardHeader>
          <CardTitle>Interest Rate Scenarios</CardTitle>
          <CardDescription>Select a scenario to view detailed analysis</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={selectedScenario} onValueChange={(v) => setSelectedScenario(v as InterestRateScenario)}>
            <TabsList className="grid w-full grid-cols-7">
              {data.map((scenario) => (
                <TabsTrigger key={scenario.scenario} value={scenario.scenario}>
                  {SCENARIO_LABELS[scenario.scenario]}
                </TabsTrigger>
              ))}
            </TabsList>
          </Tabs>
          {currentScenarioData && (
            <div className="mt-4 p-4 bg-muted rounded-lg">
              <p className="text-sm text-muted-foreground">{SCENARIO_DESCRIPTIONS[selectedScenario]}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Key Impact Metrics */}
      {currentScenarioData && (
        <>
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">NII Impact</CardTitle>
                {currentScenarioData.nii_impact >= 0 ? (
                  <TrendingUp className="h-4 w-4 text-green-600" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-600" />
                )}
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${
                  currentScenarioData.nii_impact >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {formatCurrency(currentScenarioData.nii_impact)}
                </div>
                <p className="text-xs text-muted-foreground mt-1">Net Interest Income Impact</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">EVE Impact</CardTitle>
                {currentScenarioData.eve_impact >= 0 ? (
                  <TrendingUp className="h-4 w-4 text-green-600" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-600" />
                )}
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${
                  currentScenarioData.eve_impact >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {formatCurrency(currentScenarioData.eve_impact)}
                </div>
                <p className="text-xs text-muted-foreground mt-1">Economic Value of Equity Impact</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Duration Gap</CardTitle>
                <Activity className="h-4 w-4 text-primary" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {currentScenarioData.duration_gap.toFixed(2)}
                </div>
                <p className="text-xs text-muted-foreground mt-1">Years</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Risk Level</CardTitle>
              </CardHeader>
              <CardContent>
                <div className={`text-lg font-bold px-3 py-1 rounded-full inline-block ${
                  currentScenarioData.risk_level === 'critical' ? 'bg-red-100 text-red-700' :
                  currentScenarioData.risk_level === 'high' ? 'bg-orange-100 text-orange-700' :
                  currentScenarioData.risk_level === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-green-100 text-green-700'
                }`}>
                  {currentScenarioData.risk_level.toUpperCase()}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Detailed Impact Analysis */}
          <Card>
            <CardHeader>
              <CardTitle>Detailed Impact Analysis - {SCENARIO_LABELS[selectedScenario]}</CardTitle>
              <CardDescription>Comprehensive breakdown of interest rate risk impacts</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* NII Analysis */}
                <div className="p-4 border rounded-lg">
                  <h3 className="font-semibold mb-4">Net Interest Income (NII) Impact</h3>
                  <div className="grid gap-4 md:grid-cols-3">
                    <div>
                      <p className="text-sm text-muted-foreground">Base NII</p>
                      <p className="text-xl font-bold">{formatCurrency(currentScenarioData.base_nii)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Projected NII</p>
                      <p className="text-xl font-bold">{formatCurrency(currentScenarioData.projected_nii)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Impact</p>
                      <p className={`text-xl font-bold ${
                        currentScenarioData.nii_impact >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {formatCurrency(currentScenarioData.nii_impact)}
                        <span className="text-sm ml-2">
                          ({calculateImpactPercentage(currentScenarioData.nii_impact, currentScenarioData.base_nii)}%)
                        </span>
                      </p>
                    </div>
                  </div>
                  <div className="mt-4">
                    <div className="w-full bg-muted rounded-full h-4">
                      <div
                        className={`h-4 rounded-full ${
                          currentScenarioData.nii_impact >= 0 ? 'bg-green-600' : 'bg-red-600'
                        }`}
                        style={{
                          width: `${Math.min(Math.abs(parseFloat(calculateImpactPercentage(currentScenarioData.nii_impact, currentScenarioData.base_nii))), 100)}%`
                        }}
                      />
                    </div>
                  </div>
                </div>

                {/* EVE Analysis */}
                <div className="p-4 border rounded-lg">
                  <h3 className="font-semibold mb-4">Economic Value of Equity (EVE) Impact</h3>
                  <div className="grid gap-4 md:grid-cols-3">
                    <div>
                      <p className="text-sm text-muted-foreground">Base EVE</p>
                      <p className="text-xl font-bold">{formatCurrency(currentScenarioData.base_eve)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Projected EVE</p>
                      <p className="text-xl font-bold">{formatCurrency(currentScenarioData.projected_eve)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Impact</p>
                      <p className={`text-xl font-bold ${
                        currentScenarioData.eve_impact >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {formatCurrency(currentScenarioData.eve_impact)}
                        <span className="text-sm ml-2">
                          ({calculateImpactPercentage(currentScenarioData.eve_impact, currentScenarioData.base_eve)}%)
                        </span>
                      </p>
                    </div>
                  </div>
                  <div className="mt-4">
                    <div className="w-full bg-muted rounded-full h-4">
                      <div
                        className={`h-4 rounded-full ${
                          currentScenarioData.eve_impact >= 0 ? 'bg-green-600' : 'bg-red-600'
                        }`}
                        style={{
                          width: `${Math.min(Math.abs(parseFloat(calculateImpactPercentage(currentScenarioData.eve_impact, currentScenarioData.base_eve))), 100)}%`
                        }}
                      />
                    </div>
                  </div>
                </div>

                {/* Duration Analysis */}
                <div className="p-4 border rounded-lg">
                  <h3 className="font-semibold mb-4">Duration Gap Analysis</h3>
                  <div className="grid gap-4 md:grid-cols-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Asset Duration</p>
                      <p className="text-xl font-bold">{currentScenarioData.asset_duration.toFixed(2)} years</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Liability Duration</p>
                      <p className="text-xl font-bold">{currentScenarioData.liability_duration.toFixed(2)} years</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Duration Gap</p>
                      <p className={`text-xl font-bold ${
                        Math.abs(currentScenarioData.duration_gap) <= 1 ? 'text-green-600' : 'text-orange-600'
                      }`}>
                        {currentScenarioData.duration_gap.toFixed(2)} years
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Modified Duration</p>
                      <p className="text-xl font-bold">{currentScenarioData.modified_duration.toFixed(2)}</p>
                    </div>
                  </div>
                </div>

                {/* Repricing Analysis */}
                <div className="p-4 border rounded-lg">
                  <h3 className="font-semibold mb-4">Repricing Gap Analysis</h3>
                  <div className="grid gap-4 md:grid-cols-3">
                    <div>
                      <p className="text-sm text-muted-foreground">Rate Sensitive Assets</p>
                      <p className="text-xl font-bold text-green-600">
                        {formatCurrency(currentScenarioData.rate_sensitive_assets)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Rate Sensitive Liabilities</p>
                      <p className="text-xl font-bold text-red-600">
                        {formatCurrency(currentScenarioData.rate_sensitive_liabilities)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Repricing Gap</p>
                      <p className={`text-xl font-bold ${
                        currentScenarioData.repricing_gap >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {formatCurrency(currentScenarioData.repricing_gap)}
                      </p>
                    </div>
                  </div>
                  <div className="mt-4">
                    <p className="text-sm text-muted-foreground mb-2">Gap Ratio: {currentScenarioData.gap_ratio.toFixed(2)}%</p>
                    <div className="w-full bg-muted rounded-full h-3">
                      <div
                        className="bg-primary h-3 rounded-full"
                        style={{ width: `${Math.min(Math.abs(currentScenarioData.gap_ratio), 100)}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Scenario Comparison */}
          <Card>
            <CardHeader>
              <CardTitle>Scenario Comparison</CardTitle>
              <CardDescription>Compare impacts across all interest rate scenarios</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-3 font-semibold">Scenario</th>
                      <th className="text-right p-3 font-semibold">NII Impact</th>
                      <th className="text-right p-3 font-semibold">EVE Impact</th>
                      <th className="text-right p-3 font-semibold">Duration Gap</th>
                      <th className="text-right p-3 font-semibold">Repricing Gap</th>
                      <th className="text-center p-3 font-semibold">Risk Level</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.map((scenario) => (
                      <tr
                        key={scenario.scenario}
                        className={`border-b hover:bg-muted/50 ${
                          scenario.scenario === selectedScenario ? 'bg-primary/5' : ''
                        }`}
                      >
                        <td className="p-3 font-medium">{SCENARIO_LABELS[scenario.scenario]}</td>
                        <td className={`p-3 text-right ${
                          scenario.nii_impact >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {formatCurrency(scenario.nii_impact)}
                        </td>
                        <td className={`p-3 text-right ${
                          scenario.eve_impact >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {formatCurrency(scenario.eve_impact)}
                        </td>
                        <td className="p-3 text-right">{scenario.duration_gap.toFixed(2)}</td>
                        <td className={`p-3 text-right ${
                          scenario.repricing_gap >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {formatCurrency(scenario.repricing_gap)}
                        </td>
                        <td className="p-3 text-center">
                          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                            scenario.risk_level === 'critical' ? 'bg-red-100 text-red-700' :
                            scenario.risk_level === 'high' ? 'bg-orange-100 text-orange-700' :
                            scenario.risk_level === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                            'bg-green-100 text-green-700'
                          }`}>
                            {scenario.risk_level.toUpperCase()}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Risk Management Recommendations */}
          <Card>
            <CardHeader>
              <CardTitle>Risk Management Recommendations</CardTitle>
              <CardDescription>Suggested actions for managing interest rate risk</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {currentScenarioData.recommendations.map((rec, index) => (
                  <div key={index} className="flex items-start gap-3 p-4 border rounded-lg">
                    <div className="h-6 w-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <span className="text-xs font-semibold text-primary">{index + 1}</span>
                    </div>
                    <p className="flex-1">{rec}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
