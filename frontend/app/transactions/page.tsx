'use client'

import React, { useState, useEffect } from 'react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge, Chip } from '@/components/ui/badge'
import { SkeletonLoader, EmptyState } from '@/components/common/stat-card'
import { formatCurrency, formatDate, categoryColors, categoryIcons } from '@/utils'
import { apiClient } from '@/services/api'
import { motion } from 'framer-motion'

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [sortBy, setSortBy] = useState<'date' | 'amount'>('date')

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        const data = await apiClient.getTransactions({ limit: 100 })
        setTransactions(data.data || [])
      } catch (error) {
        console.error('Failed to fetch transactions:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchTransactions()
  }, [])

  const categories = ['food', 'transport', 'entertainment', 'utilities', 'healthcare', 'shopping', 'subscriptions', 'salary', 'investment', 'transfer', 'other']

  let filtered = transactions.filter((tx) => {
    const matchesSearch = tx.description.toLowerCase().includes(search.toLowerCase()) ||
      (tx.merchant?.toLowerCase().includes(search.toLowerCase()) ?? false)
    const matchesCategory = !selectedCategory || tx.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  if (sortBy === 'amount') {
    filtered = filtered.sort((a, b) => b.amount - a.amount)
  } else {
    filtered = filtered.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
  }

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="space-y-6">
          <h1 className="typo-h2">Transactions</h1>
          <SkeletonLoader count={5} />
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="typo-h2">Transactions</h1>
            <p className="text-muted-foreground">Manage and analyze your transactions</p>
          </div>
          <Button variant="primary">+ Add Transaction</Button>
        </div>

        {/* Filters */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Filters</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium block mb-2">Search</label>
              <Input
                type="text"
                placeholder="Search by description or merchant..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>

            <div>
              <label className="text-sm font-medium block mb-2">Category</label>
              <div className="flex flex-wrap gap-2">
                <Chip
                  variant={!selectedCategory ? 'filled' : 'default'}
                  onClick={() => setSelectedCategory(null)}
                  className="cursor-pointer"
                >
                  All
                </Chip>
                {categories.map((cat) => (
                  <Chip
                    key={cat}
                    variant={selectedCategory === cat ? 'filled' : 'default'}
                    onClick={() => setSelectedCategory(cat)}
                    className="cursor-pointer"
                  >
                    {categoryIcons[cat as keyof typeof categoryIcons]} {cat}
                  </Chip>
                ))}
              </div>
            </div>

            <div>
              <label className="text-sm font-medium block mb-2">Sort By</label>
              <div className="flex gap-2">
                <Button
                  variant={sortBy === 'date' ? 'primary' : 'outline'}
                  size="sm"
                  onClick={() => setSortBy('date')}
                >
                  Date
                </Button>
                <Button
                  variant={sortBy === 'amount' ? 'primary' : 'outline'}
                  size="sm"
                  onClick={() => setSortBy('amount')}
                >
                  Amount
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Transactions Table */}
        <Card>
          <CardHeader>
            <CardTitle>All Transactions</CardTitle>
            <CardDescription>{filtered.length} transactions</CardDescription>
          </CardHeader>
          <CardContent>
            {filtered.length === 0 ? (
              <EmptyState
                title="No transactions found"
                description="Add your first transaction to get started"
                icon="💳"
              />
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-3 px-4 font-semibold text-sm">Date</th>
                      <th className="text-left py-3 px-4 font-semibold text-sm">Description</th>
                      <th className="text-left py-3 px-4 font-semibold text-sm">Category</th>
                      <th className="text-left py-3 px-4 font-semibold text-sm">Type</th>
                      <th className="text-right py-3 px-4 font-semibold text-sm">Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filtered.map((tx, idx) => (
                      <motion.tr
                        key={tx.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.2, delay: idx * 0.05 }}
                        className="border-b border-border hover:bg-muted transition-smooth cursor-pointer"
                      >
                        <td className="py-3 px-4 text-sm">{formatDate(tx.date)}</td>
                        <td className="py-3 px-4 text-sm">
                          <div>
                            <p className="font-medium">{tx.description}</p>
                            <p className="text-xs text-muted-foreground">{tx.merchant}</p>
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <Badge variant="default" className="capitalize">
                            {categoryIcons[tx.category as keyof typeof categoryIcons]} {tx.category}
                          </Badge>
                        </td>
                        <td className="py-3 px-4">
                          <Badge variant={tx.type === 'income' ? 'success' : 'default'}>
                            {tx.type}
                          </Badge>
                        </td>
                        <td className={`py-3 px-4 text-sm font-semibold text-right ${
                          tx.type === 'income' ? 'text-success' : 'text-destructive'
                        }`}>
                          {tx.type === 'income' ? '+' : '-'}{formatCurrency(tx.amount, tx.currency)}
                        </td>
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
