'use client'

import React, { useState } from 'react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { LineChartComponent, AreaChartComponent } from '@/components/charts/chart-components'
import { StatCard } from '@/components/common/stat-card'
import { Badge } from '@/components/ui/badge'

export default function ForecastingPage() {
  const [scenario, setScenario] = useState<'baseline' | 'optimistic' | 'pessimistic'>('baseline')

  const forecastData = [
    { date: 'May', value: 5000 },
    { date: 'Jun', value: 5200 },
    { date: 'Jul', value: 5400 },
    { date: 'Aug', value: 5600 },
    { date: 'Sep', value: 5800 },
    { date: 'Oct', value: 6000 },
    { date: 'Nov', value: 6200 },
    { date: 'Dec', value: 6400 },
  ]

  const scenarios = {
    baseline: {
      title: 'Baseline Forecast',
      description: 'Based on current spending patterns',
      color: 'text-primary',
      runway: 42,
      confidence: 88,
    },
    optimistic: {
      title: 'Optimistic Forecast',
      description: 'If you reduce spending by 20%',
      color: 'text-success',
      runway: 52,
      confidence: 75,
    },
    pessimistic: {
      title: 'Pessimistic Forecast',
      description: 'If spending increases by 15%',
      color: 'text-destructive',
      runway: 32,
      confidence: 72,
    },
  }

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="typo-h2">Financial Forecasting</h1>
          <p className="text-muted-foreground">AI-powered projections for your financial future</p>
        </div>

        {/* Scenario Selector */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {['baseline', 'optimistic', 'pessimistic'].map((s) => (
            <button
              key={s}
              onClick={() => setScenario(s as any)}
              className={`p-4 rounded-lg border-2 transition-smooth ${
                scenario === s
                  ? 'border-primary bg-primary/5'
                  : 'border-border hover:border-primary/50'
              }`}
            >
              <h3 className="font-semibold">{scenarios[s as keyof typeof scenarios].title}</h3>
              <p className="text-sm text-muted-foreground mt-1">
                {scenarios[s as keyof typeof scenarios].description}
              </p>
            </button>
          ))}
        </div>

        {/* Forecast Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Financial Runway"
            value={scenarios[scenario].runway}
            icon="📅"
          />
          <StatCard
            title="Forecast Confidence"
            value={scenarios[scenario].confidence}
            icon="📊"
          />
          <StatCard
            title="Projected Balance (6mo)"
            value={32000}
            currency="USD"
            icon="💰"
          />
          <StatCard
            title="Risk Level"
            value={35}
            icon="⚠️"
          />
        </div>

        {/* Forecast Chart */}
        <AreaChartComponent
          data={forecastData}
          title="Financial Forecast"
          description={`${scenarios[scenario].title} - Next 8 months`}
          height={400}
        />

        {/* Scenario Comparison */}
        <Card>
          <CardHeader>
            <CardTitle>Scenario Comparison</CardTitle>
            <CardDescription>Compare different financial scenarios</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {['baseline', 'optimistic', 'pessimistic'].map((s) => (
                <div key={s} className="flex items-center justify-between p-4 rounded-lg bg-muted">
                  <div>
                    <h4 className="font-semibold text-sm">{scenarios[s as keyof typeof scenarios].title}</h4>
                    <p className="text-xs text-muted-foreground mt-1">
                      {scenarios[s as keyof typeof scenarios].description}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold">
                      {scenarios[s as keyof typeof scenarios].runway} months runway
                    </p>
                    <Badge variant="default" className="mt-1">
                      {scenarios[s as keyof typeof scenarios].confidence}% confidence
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* What-If Analysis */}
        <Card>
          <CardHeader>
            <CardTitle>What-If Analysis</CardTitle>
            <CardDescription>Explore different scenarios</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="p-4 rounded-lg border border-border hover:bg-muted transition-smooth cursor-pointer">
                <h4 className="font-semibold text-sm">If I reduce food spending by 20%</h4>
                <p className="text-xs text-muted-foreground mt-1">Savings: $480/month</p>
                <p className="text-xs text-success font-medium mt-2">New runway: 48 months (+6 months)</p>
              </div>
              <div className="p-4 rounded-lg border border-border hover:bg-muted transition-smooth cursor-pointer">
                <h4 className="font-semibold text-sm">If I get a 15% salary increase</h4>
                <p className="text-xs text-muted-foreground mt-1">New monthly income: $4,600</p>
                <p className="text-xs text-success font-medium mt-2">New runway: 55 months (+13 months)</p>
              </div>
              <div className="p-4 rounded-lg border border-border hover:bg-muted transition-smooth cursor-pointer">
                <h4 className="font-semibold text-sm">If I cancel unused subscriptions</h4>
                <p className="text-xs text-muted-foreground mt-1">Savings: $45/month</p>
                <p className="text-xs text-success font-medium mt-2">New runway: 44 months (+2 months)</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
