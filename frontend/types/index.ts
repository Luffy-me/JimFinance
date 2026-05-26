export type AccountType = 'checking' | 'savings' | 'credit_card' | 'investment' | 'cash'
export type TransactionCategory = 
  | 'food' 
  | 'transport' 
  | 'entertainment' 
  | 'utilities' 
  | 'healthcare' 
  | 'shopping' 
  | 'subscriptions' 
  | 'salary' 
  | 'investment' 
  | 'transfer' 
  | 'other'
export type TransactionType = 'income' | 'expense' | 'transfer'
export type Currency = 'USD' | 'RUB' | 'EUR' | 'INR' | 'GBP'
export type Period = 'daily' | 'weekly' | 'monthly' | 'yearly'

export interface User {
  id: string
  email: string
  name: string
  avatar?: string
  preferences: UserPreferences
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto'
  currency: Currency
  language: string
}

export interface Account {
  id: string
  name: string
  type: AccountType
  currency: Currency
  balance: number
  createdAt: string
}

export interface Transaction {
  id: string
  accountId: string
  amount: number
  currency: Currency
  type: TransactionType
  category: TransactionCategory
  description: string
  merchant?: string
  date: string
  tags?: string[]
  confidence?: number
  isRecurring?: boolean
  notes?: string
}

export interface Category {
  id: string
  name: string
  slug: string
  type: TransactionCategory
  color: string
  icon: string
}

export interface Subscription {
  id: string
  name: string
  amount: number
  currency: Currency
  billingCycle: Period
  nextBillingDate: string
  category: TransactionCategory
  status: 'active' | 'paused' | 'cancelled'
}

export interface DashboardStats {
  totalBalance: number
  monthlyIncome: number
  monthlyExpense: number
  savingsRate: number
  runway: number
}

export interface FinancialInsight {
  id: string
  type: string
  title: string
  description: string
  confidence: number
  timestamp: string
  actionItems?: string[]
}

export interface ChartDataPoint {
  date: string
  value: number
  currency: Currency
}

export interface SpendingPattern {
  category: TransactionCategory
  amount: number
  percentage: number
  trend: 'up' | 'down' | 'stable'
}
