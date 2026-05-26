'use client'

import React, { useState, useCallback } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/utils'
import { Button } from '@/components/ui/button'

export function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const pathname = usePathname()

  const navigation = [
    { label: 'Dashboard', href: '/dashboard', icon: '📊' },
    { label: 'Transactions', href: '/transactions', icon: '💳' },
    { label: 'Analytics', href: '/analytics', icon: '📈' },
    { label: 'Insights', href: '/insights', icon: '💡' },
    { label: 'Forecasting', href: '/forecasting', icon: '🔮' },
    { label: 'Subscriptions', href: '/subscriptions', icon: '📅' },
    { label: 'Settings', href: '/settings', icon: '⚙️' },
  ]

  const isActive = useCallback((href: string) => pathname === href || pathname.startsWith(href + '/'), [pathname])

  return (
    <div className={cn(
      'border-r border-border bg-card transition-smooth duration-300',
      isCollapsed ? 'w-20' : 'w-64'
    )}>
      <div className="flex items-center justify-between p-4">
        {!isCollapsed && <h1 className="font-bold text-xl">JimFinance</h1>}
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsCollapsed(!isCollapsed)}
        >
          {isCollapsed ? '→' : '←'}
        </Button>
      </div>

      <nav className="space-y-1 p-4">
        {navigation.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              'flex items-center gap-3 px-4 py-3 rounded-md text-sm font-medium transition-smooth',
              isActive(item.href)
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:bg-muted'
            )}
          >
            <span className="text-lg">{item.icon}</span>
            {!isCollapsed && <span>{item.label}</span>}
          </Link>
        ))}
      </nav>
    </div>
  )
}
