'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { cn, formatCurrency, calculatePercentChange } from '@/utils'
import { Card, CardContent } from '@/components/ui/card'

export interface StatCardProps {
  title: string
  value: number
  currency?: string
  previousValue?: number
  icon?: string
  trend?: 'up' | 'down' | 'neutral'
  className?: string
}

export function StatCard({
  title,
  value,
  currency,
  previousValue,
  icon,
  trend = 'neutral',
  className,
}: StatCardProps) {
  const percentChange = previousValue ? calculatePercentChange(value, previousValue) : 0

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className={className}>
        <CardContent className="pt-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-muted-foreground font-medium">{title}</p>
              <p className="text-3xl font-bold mt-2">
                {currency ? formatCurrency(value, currency) : value.toLocaleString()}
              </p>
              {previousValue !== undefined && (
                <p className={cn(
                  'text-sm font-medium mt-2',
                  percentChange > 0 ? 'text-success' : percentChange < 0 ? 'text-destructive' : 'text-muted-foreground'
                )}>
                  {percentChange > 0 ? '↑' : percentChange < 0 ? '↓' : '→'} {Math.abs(percentChange).toFixed(1)}% vs last period
                </p>
              )}
            </div>
            {icon && <div className="text-4xl">{icon}</div>}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

export function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center p-8">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-muted border-t-primary" />
    </div>
  )
}

export function EmptyState({ title, description, icon }: { title: string; description: string; icon: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      <div className="text-6xl mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-foreground">{title}</h3>
      <p className="text-sm text-muted-foreground mt-1">{description}</p>
    </div>
  )
}

export function SkeletonLoader({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="h-20 bg-muted rounded-lg animate-shimmer" />
      ))}
    </div>
  )
}
