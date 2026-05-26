'use client'

import React, { useState } from 'react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { StatCard } from '@/components/common/stat-card'
import { formatCurrency, formatDate } from '@/utils'

export default function SubscriptionsPage() {
  const [subscriptions] = useState([
    {
      id: 1,
      name: 'Netflix',
      amount: 15.99,
      currency: 'USD',
      billingCycle: 'monthly',
      nextBillingDate: '2024-06-15',
      category: 'entertainment',
      status: 'active',
    },
    {
      id: 2,
      name: 'Spotify',
      amount: 10.99,
      currency: 'USD',
      billingCycle: 'monthly',
      nextBillingDate: '2024-06-10',
      category: 'entertainment',
      status: 'active',
    },
    {
      id: 3,
      name: 'Adobe Creative Cloud',
      amount: 49.99,
      currency: 'USD',
      billingCycle: 'monthly',
      nextBillingDate: '2024-06-20',
      category: 'subscriptions',
      status: 'active',
    },
    {
      id: 4,
      name: 'Discord Nitro',
      amount: 9.99,
      currency: 'USD',
      billingCycle: 'monthly',
      nextBillingDate: '2024-06-05',
      category: 'subscriptions',
      status: 'active',
    },
    {
      id: 5,
      name: 'Medium',
      amount: 5.0,
      currency: 'USD',
      billingCycle: 'monthly',
      nextBillingDate: '2024-06-25',
      category: 'subscriptions',
      status: 'paused',
    },
  ])

  const totalMonthly = subscriptions
    .filter((s) => s.status === 'active')
    .reduce((sum, s) => sum + s.amount, 0)

  const totalYearly = totalMonthly * 12

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="typo-h2">Subscriptions</h1>
          <p className="text-muted-foreground">Manage and track all your subscriptions</p>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Active Subscriptions"
            value={subscriptions.filter((s) => s.status === 'active').length}
            icon="✅"
          />
          <StatCard
            title="Monthly Spending"
            value={totalMonthly}
            currency="USD"
            icon="📅"
          />
          <StatCard
            title="Yearly Cost"
            value={totalYearly}
            currency="USD"
            icon="📊"
          />
          <StatCard
            title="Unused Services"
            value={subscriptions.filter((s) => s.status === 'paused').length}
            icon="⏸️"
          />
        </div>

        {/* Subscriptions List */}
        <Card>
          <CardHeader>
            <CardTitle>Active Subscriptions</CardTitle>
            <CardDescription>All your active subscription services</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {subscriptions
                .filter((s) => s.status === 'active')
                .map((sub) => (
                  <div key={sub.id} className="flex items-center justify-between p-4 rounded-lg border border-border hover:bg-muted transition-smooth">
                    <div className="flex-1">
                      <h4 className="font-semibold text-sm">{sub.name}</h4>
                      <p className="text-xs text-muted-foreground mt-1">
                        Next billing: {formatDate(sub.nextBillingDate)}
                      </p>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="font-semibold text-sm">
                          {formatCurrency(sub.amount, sub.currency)}/{sub.billingCycle.charAt(0)}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {formatCurrency(sub.amount * 12, sub.currency)}/year
                        </p>
                      </div>
                      <Badge variant="default" className="capitalize">
                        {sub.billingCycle}
                      </Badge>
                      <Button variant="ghost" size="sm">⋮</Button>
                    </div>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>

        {/* Paused Subscriptions */}
        {subscriptions.filter((s) => s.status === 'paused').length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Paused Subscriptions</CardTitle>
              <CardDescription>Services you've put on hold</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {subscriptions
                  .filter((s) => s.status === 'paused')
                  .map((sub) => (
                    <div key={sub.id} className="flex items-center justify-between p-4 rounded-lg border border-border opacity-60">
                      <div>
                        <h4 className="font-semibold text-sm">{sub.name}</h4>
                        <p className="text-xs text-muted-foreground mt-1">
                          {formatCurrency(sub.amount, sub.currency)}/{sub.billingCycle.charAt(0)}
                        </p>
                      </div>
                      <Badge variant="default">Paused</Badge>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Optimization Tips */}
        <Card>
          <CardHeader>
            <CardTitle>💡 Optimization Tips</CardTitle>
            <CardDescription>Ways to save on subscriptions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="p-3 rounded-lg bg-warning/5 border border-warning/20">
                <p className="font-medium text-sm">Bundle services</p>
                <p className="text-xs text-muted-foreground mt-1">Consider bundled plans like Spotify+Hulu to save money.</p>
              </div>
              <div className="p-3 rounded-lg bg-success/5 border border-success/20">
                <p className="font-medium text-sm">Annual billing</p>
                <p className="text-xs text-muted-foreground mt-1">Paying yearly instead of monthly can save up to 20%.</p>
              </div>
              <div className="p-3 rounded-lg bg-info/5 border border-info/20">
                <p className="font-medium text-sm">Shared accounts</p>
                <p className="text-xs text-muted-foreground mt-1">Share family plans with others to reduce costs.</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
