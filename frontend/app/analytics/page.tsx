'use client'

import React, { useState } from 'react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { AreaChartComponent, BarChartComponent, PieChartComponent } from '@/components/charts/chart-components'
import { StatCard } from '@/components/common/stat-card'
import { Badge } from '@/components/ui/badge'

export default function AnalyticsPage() {
  const [period, setPeriod] = useState<'week' | 'month' | 'year'>('month')

  const weeklyData = [
    { date: 'Mon', value: 240 },
    { date: 'Tue', value: 139 },
    { date: 'Wed', value: 980 },
    { date: 'Thu', value: 390 },
    { date: 'Fri', value: 480 },
    { date: 'Sat', value: 380 },
    { date: 'Sun', value: 430 },
  ]

  const categoryData = [
    { name: 'Food', value: 2400 },
    { name: 'Transport', value: 1398 },
    { name: 'Entertainment', value: 9800 },
    { name: 'Shopping', value: 3908 },
    { name: 'Other', value: 4800 },
  ]

  const categoryMetrics = [
    { category: 'Food', spent: 2400, previous: 2100, trend: 'up', percentage: 14 },
    { category: 'Transport', spent: 1200, previous: 1100, trend: 'down', percentage: 9 },
    { category: 'Entertainment', spent: 980, previous: 1200, trend: 'down', percentage: 18 },
    { category: 'Utilities', spent: 450, previous: 450, trend: 'stable', percentage: 8 },
    { category: 'Shopping', spent: 1500, previous: 1200, trend: 'up', percentage: 25 },
  ]

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="typo-h2">Spending Analytics</h1>
          <p className="text-muted-foreground">Comprehensive analysis of your spending patterns</p>
        </div>

        {/* Period Selector */}
        <div className="flex gap-2">
          {['week', 'month', 'year'].map((p) => (
            <Button
              key={p}
              variant={period === p ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setPeriod(p as any)}
            >
              {p.charAt(0).toUpperCase() + p.slice(1)}
            </Button>
          ))}
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard title="Total Spending" value={6258} currency="USD" icon="💸" />
          <StatCard title="Average Daily" value={892.57} currency="USD" icon="📊" />
          <StatCard title="Highest Category" value={9800} currency="USD" icon="🏆" />
          <StatCard title="Largest Transaction" value={2400} currency="USD" icon="💰" />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <AreaChartComponent
            data={weeklyData}
            title="Spending Over Time"
            description={`Last 7 days in ${period}`}
            height={300}
          />
          <PieChartComponent
            data={categoryData}
            title="Spending by Category"
            description="Distribution of expenses"
            height={300}
          />
        </div>

        {/* Category Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle>Category Breakdown</CardTitle>
            <CardDescription>Detailed spending by category</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {categoryMetrics.map((cat) => (
                <div key={cat.category} className="flex items-center justify-between p-4 rounded-lg hover:bg-muted transition-smooth">
                  <div className="flex-1">
                    <h4 className="font-semibold text-sm">{cat.category}</h4>
                    <p className="text-xs text-muted-foreground">
                      ${cat.spent} this month
                    </p>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="w-32 bg-muted rounded-full h-2">
                      <div
                        className="bg-primary h-2 rounded-full transition-all"
                        style={{ width: `${(cat.spent / 9800) * 100}%` }}
                      />
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-sm">${cat.spent}</p>
                      <Badge
                        variant={cat.trend === 'up' ? 'destructive' : cat.trend === 'down' ? 'success' : 'default'}
                        className="mt-1"
                      >
                        {cat.trend === 'up' ? '↑' : cat.trend === 'down' ? '↓' : '→'} {cat.percentage}%
                      </Badge>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
