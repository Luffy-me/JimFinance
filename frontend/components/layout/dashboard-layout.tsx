'use client'

import React, { ReactNode } from 'react'
import { Sidebar } from './sidebar'
import { Header } from './header'
import { cn } from '@/utils'

export interface DashboardLayoutProps {
  children: ReactNode
  className?: string
}

export function DashboardLayout({ children, className }: DashboardLayoutProps) {
  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className={cn('flex-1 overflow-auto p-6 space-y-6', className)}>
          {children}
        </main>
      </div>
    </div>
  )
}
