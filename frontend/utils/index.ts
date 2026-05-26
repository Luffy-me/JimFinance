import { type ClassValue, clsx } from 'clsx'

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs)
}

export function formatCurrency(amount: number, currency: string = 'USD', locale: string = 'en-US'): string {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount)
}

export function formatDate(date: string | Date, format: 'short' | 'long' | 'month' = 'short'): string {
  const d = typeof date === 'string' ? new Date(date) : date
  
  const options: Record<'short' | 'long' | 'month', Intl.DateTimeFormatOptions> = {
    short: { month: 'short', day: 'numeric' },
    long: { month: 'long', day: 'numeric', year: 'numeric' },
    month: { month: 'long' },
  }
  
  return d.toLocaleDateString('en-US', options[format])
}

export function formatCompact(num: number): string {
  if (num >= 1e6) return (num / 1e6).toFixed(1) + 'M'
  if (num >= 1e3) return (num / 1e3).toFixed(1) + 'K'
  return num.toFixed(2)
}

export function calculatePercentChange(current: number, previous: number): number {
  if (previous === 0) return 0
  return ((current - previous) / Math.abs(previous)) * 100
}

export function getInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

export const categoryColors: Record<string, { light: string; dark: string }> = {
  food: { light: '#FF6B6B', dark: '#FF8787' },
  transport: { light: '#4ECDC4', dark: '#56E8D8' },
  entertainment: { light: '#FFE66D', dark: '#FFED4E' },
  utilities: { light: '#95E1D3', dark: '#A8F4E3' },
  healthcare: { light: '#FF6B9D', dark: '#FF8AB0' },
  shopping: { light: '#C44569', dark: '#E07896' },
  subscriptions: { light: '#6C5CE7', dark: '#8E7FFF' },
  salary: { light: '#00B894', dark: '#27AE60' },
  investment: { light: '#0984E3', dark: '#3498DB' },
  transfer: { light: '#A29BFE', dark: '#B19EFF' },
  other: { light: '#DFE6E9', dark: '#95A5A6' },
}

export const categoryIcons: Record<string, string> = {
  food: '🍽️',
  transport: '🚗',
  entertainment: '🎬',
  utilities: '⚡',
  healthcare: '🏥',
  shopping: '🛍️',
  subscriptions: '📱',
  salary: '💰',
  investment: '📈',
  transfer: '↔️',
  other: '📌',
}
