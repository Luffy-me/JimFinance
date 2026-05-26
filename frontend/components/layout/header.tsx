'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'

export function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <header className="border-b border-border bg-card">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-4">
          <input
            type="text"
            placeholder="Search transactions..."
            className="w-96 rounded-md border border-input bg-muted px-4 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>

        <div className="flex items-center gap-4">
          <button className="text-muted-foreground hover:text-foreground transition-smooth">
            🔔
          </button>
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="flex items-center gap-2 rounded-md hover:bg-muted px-3 py-2 transition-smooth"
          >
            👤
          </button>

          {isMenuOpen && (
            <div className="absolute right-4 top-16 z-50 w-48 rounded-md border border-border bg-popover shadow-lg">
              <Link href="/settings" className="block px-4 py-2 text-sm hover:bg-muted">
                Profile
              </Link>
              <Link href="/settings" className="block px-4 py-2 text-sm hover:bg-muted">
                Settings
              </Link>
              <button
                onClick={() => {
                  localStorage.removeItem('access_token')
                  window.location.href = '/login'
                }}
                className="w-full text-left px-4 py-2 text-sm text-destructive hover:bg-destructive/10"
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
