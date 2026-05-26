'use client'

import React from 'react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { motion } from 'framer-motion'

export default function InsightsPage() {
  const insights = [
    {
      id: 1,
      type: 'positive',
      icon: '🎯',
      title: 'Excellent Savings Rate',
      description: 'You\'re saving 45% of your income this month, that\'s 8% higher than last month.',
      confidence: 95,
      actionItems: ['Keep up the momentum', 'Consider investing extra savings'],
    },
    {
      id: 2,
      type: 'warning',
      icon: '⚠️',
      title: 'Food Spending Spike',
      description: 'Your food spending increased by 23% this month. You\'ve made 12 restaurant visits.',
      confidence: 87,
      actionItems: ['Review recent transactions', 'Set a weekly budget for dining'],
    },
    {
      id: 3,
      type: 'neutral',
      icon: '💡',
      title: 'Subscription Optimization Opportunity',
      description: 'You have 3 unused subscriptions. Canceling them could save $45/month.',
      confidence: 92,
      actionItems: ['Review subscriptions', 'Cancel unused services'],
    },
    {
      id: 4,
      type: 'positive',
      icon: '📈',
      title: 'Income Growth',
      description: 'Your average transaction value increased by 15% compared to last month.',
      confidence: 78,
      actionItems: ['Track income sources', 'Plan for increased revenue'],
    },
    {
      id: 5,
      type: 'warning',
      icon: '🔴',
      title: 'Unusual Transaction Detected',
      description: 'A $500 transaction from "TechStore" on May 25 seems unusual compared to your patterns.',
      confidence: 65,
      actionItems: ['Review transaction', 'Confirm it wasn\'t fraudulent'],
    },
  ]

  const variants = {
    hidden: { opacity: 0, y: 20 },
    visible: (i: number) => ({
      opacity: 1,
      y: 0,
      transition: { delay: i * 0.1, duration: 0.4 },
    }),
  }

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="typo-h2">AI Insights</h1>
          <p className="text-muted-foreground">Personalized financial recommendations powered by AI</p>
        </div>

        {/* Insights Grid */}
        <div className="space-y-4">
          {insights.map((insight, idx) => (
            <motion.div
              key={insight.id}
              custom={idx}
              variants={variants}
              initial="hidden"
              animate="visible"
            >
              <Card className="border-l-4 border-l-primary">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4">
                      <div className="text-3xl">{insight.icon}</div>
                      <div>
                        <CardTitle className="text-lg">{insight.title}</CardTitle>
                        <CardDescription className="mt-1">{insight.description}</CardDescription>
                      </div>
                    </div>
                    <Badge variant="default">
                      {insight.confidence}% confidence
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div>
                    <h4 className="text-sm font-semibold mb-2">Recommended Actions:</h4>
                    <ul className="space-y-2">
                      {insight.actionItems.map((action, i) => (
                        <li key={i} className="flex items-center gap-2 text-sm text-muted-foreground">
                          <span className="w-1.5 h-1.5 rounded-full bg-primary"></span>
                          {action}
                        </li>
                      ))}
                    </ul>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Memory Timeline */}
        <Card>
          <CardHeader>
            <CardTitle>Financial Memory Timeline</CardTitle>
            <CardDescription>Historical insights and decisions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="relative pl-6 pb-4 border-l-2 border-border">
                <div className="absolute left-0 top-0 w-3 h-3 bg-primary rounded-full -translate-x-1.5"></div>
                <h4 className="font-semibold text-sm">Budget Adjustment</h4>
                <p className="text-xs text-muted-foreground mt-1">Reduced food budget by $100/month</p>
                <p className="text-xs text-muted-foreground">May 20, 2024</p>
              </div>
              <div className="relative pl-6 pb-4 border-l-2 border-border">
                <div className="absolute left-0 top-0 w-3 h-3 bg-success rounded-full -translate-x-1.5"></div>
                <h4 className="font-semibold text-sm">Goal Achievement</h4>
                <p className="text-xs text-muted-foreground mt-1">Saved $500 for emergency fund</p>
                <p className="text-xs text-muted-foreground">May 15, 2024</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
