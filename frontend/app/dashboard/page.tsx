'use client'

import React, { useState, useEffect } from 'react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { StatCard, LoadingSpinner, SkeletonLoader } from '@/components/common/stat-card'
import { LineChartComponent, PieChartComponent, AreaChartComponent } from '@/components/charts/chart-components'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import Link from 'next/link'
import { apiClient } from '@/services/api'

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [transactions, setTransactions] = useState<any[]>([])

  useEffect(() => {
    const fetchData = async () => {
      try {
        const dashboardData = await apiClient.getDashboardStats()
        setStats(dashboardData)

        const txns = await apiClient.getTransactions({ limit: 10 })
        setTransactions(txns.data || [])
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [])

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="space-y-6">
          <div>
            <h1 className="typo-h2">Dashboard</h1>
            <p className="text-muted-foreground">Welcome to your financial intelligence center</p>
          </div>
          <SkeletonLoader count={4} />
        </div>
      </DashboardLayout>
    )
  }

  const spendingTrend = [
    { date: 'Mon', value: 2400 },
    { date: 'Tue', value: 1398 },
    { date: 'Wed', value: 9800 },
    { date: 'Thu', value: 3908 },
    { date: 'Fri', value: 4800 },
    { date: 'Sat', value: 3800 },
    { date: 'Sun', value: 4300 },
  ]

  const categoryBreakdown = [
    { name: 'Food', value: 2400 },
    { name: 'Transport', value: 1398 },
    { name: 'Entertainment', value: 9800 },
    { name: 'Shopping', value: 3908 },
    { name: 'Other', value: 4800 },
  ]

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="typo-h2">Dashboard</h1>
            <p className="text-muted-foreground">Welcome back! Here's your financial overview.</p>
          </div>
          <Link href="/transactions">
            <Button variant="primary">Add Transaction</Button>
          </Link>
        </div>

        {/* Summary Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Balance"
            value={stats?.total_balance || 0}
            currency="USD"
            icon="💰"
          />
          <StatCard
            title="Monthly Income"
            value={stats?.monthly_income || 0}
            currency="USD"
            icon="📈"
            previousValue={stats?.previous_monthly_income}
          />
          <StatCard
            title="Monthly Expense"
            value={stats?.monthly_expense || 0}
            currency="USD"
            icon="💸"
            previousValue={stats?.previous_monthly_expense}
          />
          <StatCard
            title="Savings Rate"
            value={(stats?.savings_rate || 0) * 100}
            icon="🎯"
          />
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <AreaChartComponent
            data={spendingTrend}
            title="Spending Trend"
            description="Last 7 days"
            height={300}
          />
          <PieChartComponent
            data={categoryBreakdown}
            title="Spending by Category"
            description="Monthly breakdown"
            height={300}
          />
        </div>

        {/* Recent Transactions */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Recent Transactions</CardTitle>
              <CardDescription>Your latest transactions</CardDescription>
            </div>
            <Link href="/transactions">
              <Button variant="ghost" size="sm">View all</Button>
            </Link>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {transactions.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No transactions yet. Add your first transaction to get started!
                </div>
              ) : (
                transactions.slice(0, 5).map((tx) => (
                  <div key={tx.id} className="flex items-center justify-between p-3 hover:bg-muted rounded-md transition-smooth">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-muted flex items-center justify-center text-lg">
                        {tx.category === 'food' ? '🍽️' : '📌'}
                      </div>
                      <div>
                        <p className="font-medium text-sm">{tx.description}</p>
                        <p className="text-xs text-muted-foreground">{tx.merchant || 'Unknown'}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`font-semibold text-sm ${tx.type === 'income' ? 'text-success' : 'text-destructive'}`}>
                        {tx.type === 'income' ? '+' : '-'}${tx.amount}
                      </p>
                      <p className="text-xs text-muted-foreground capitalize">{tx.category}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        {/* Financial Insights Card */}
        <Card>
          <CardHeader>
            <CardTitle>💡 AI Insights</CardTitle>
            <CardDescription>Personalized recommendations for your finances</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="p-4 rounded-lg bg-primary/5 border border-primary/20">
                <p className="font-medium text-sm">You're saving 45% of your income this month</p>
                <p className="text-xs text-muted-foreground mt-1">That's 8% higher than last month. Keep it up! 🎯</p>
              </div>
              <div className="p-4 rounded-lg bg-warning/5 border border-warning/20">
                <p className="font-medium text-sm">Food spending increased by 23%</p>
                <p className="text-xs text-muted-foreground mt-1">Consider checking your recent restaurant visits.</p>
              </div>
              <Link href="/insights">
                <Button variant="ghost" fullWidth>View all insights</Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
