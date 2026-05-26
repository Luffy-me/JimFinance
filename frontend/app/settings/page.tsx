'use client'

import React, { useState } from 'react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'

export default function SettingsPage() {
  const [theme, setTheme] = useState<'light' | 'dark' | 'auto'>('auto')
  const [currency, setCurrency] = useState('USD')
  const [notifications, setNotifications] = useState(true)

  const handleThemeChange = (newTheme: typeof theme) => {
    setTheme(newTheme)
    if (newTheme === 'dark') {
      document.documentElement.classList.add('dark')
    } else if (newTheme === 'light') {
      document.documentElement.classList.remove('dark')
    }
    localStorage.setItem('theme', newTheme)
  }

  return (
    <DashboardLayout>
      <div className="space-y-8 max-w-2xl">
        {/* Header */}
        <div>
          <h1 className="typo-h2">Settings</h1>
          <p className="text-muted-foreground">Manage your preferences and account settings</p>
        </div>

        {/* Profile Settings */}
        <Card>
          <CardHeader>
            <CardTitle>Profile</CardTitle>
            <CardDescription>Manage your account information</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium block mb-2">Full Name</label>
              <Input type="text" placeholder="John Doe" defaultValue="John Doe" />
            </div>
            <div>
              <label className="text-sm font-medium block mb-2">Email</label>
              <Input type="email" placeholder="john@example.com" defaultValue="john@example.com" />
            </div>
            <Button variant="primary">Save Changes</Button>
          </CardContent>
        </Card>

        {/* Preferences */}
        <Card>
          <CardHeader>
            <CardTitle>Preferences</CardTitle>
            <CardDescription>Customize your experience</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Theme */}
            <div>
              <label className="text-sm font-medium block mb-3">Theme</label>
              <div className="flex gap-2">
                {['light', 'dark', 'auto'].map((t) => (
                  <button
                    key={t}
                    onClick={() => handleThemeChange(t as typeof theme)}
                    className={`px-4 py-2 rounded-md border transition-smooth capitalize ${
                      theme === t
                        ? 'bg-primary text-primary-foreground border-primary'
                        : 'border-border hover:bg-muted'
                    }`}
                  >
                    {t === 'auto' ? 'System' : t}
                  </button>
                ))}
              </div>
            </div>

            {/* Currency */}
            <div>
              <label className="text-sm font-medium block mb-2">Default Currency</label>
              <select
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
                className="w-full px-4 py-2 rounded-md border border-input bg-background text-foreground"
              >
                <option value="USD">USD - US Dollar</option>
                <option value="EUR">EUR - Euro</option>
                <option value="GBP">GBP - British Pound</option>
                <option value="RUB">RUB - Russian Ruble</option>
                <option value="INR">INR - Indian Rupee</option>
              </select>
            </div>

            {/* Notifications */}
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium block">Email Notifications</label>
                <p className="text-xs text-muted-foreground mt-1">Receive updates about your finances</p>
              </div>
              <button
                onClick={() => setNotifications(!notifications)}
                className={`relative w-12 h-6 rounded-full transition-colors ${
                  notifications ? 'bg-primary' : 'bg-muted'
                }`}
              >
                <div
                  className={`absolute w-5 h-5 bg-white rounded-full top-0.5 transition-transform ${
                    notifications ? 'translate-x-6' : 'translate-x-0.5'
                  }`}
                />
              </button>
            </div>
          </CardContent>
        </Card>

        {/* Account Settings */}
        <Card>
          <CardHeader>
            <CardTitle>Account</CardTitle>
            <CardDescription>Manage your account</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 rounded-lg bg-muted">
              <h4 className="font-semibold text-sm">Account Status</h4>
              <p className="text-xs text-muted-foreground mt-1">Your account is active and in good standing</p>
              <Badge variant="success" className="mt-3">Active</Badge>
            </div>
            <div>
              <h4 className="font-semibold text-sm mb-2">Change Password</h4>
              <Input type="password" placeholder="Current password" className="mb-2" />
              <Input type="password" placeholder="New password" className="mb-2" />
              <Input type="password" placeholder="Confirm password" />
              <Button variant="primary" className="mt-3">Update Password</Button>
            </div>
          </CardContent>
        </Card>

        {/* Data Management */}
        <Card>
          <CardHeader>
            <CardTitle>Data Management</CardTitle>
            <CardDescription>Export or delete your data</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button variant="outline" fullWidth>📥 Export My Data</Button>
            <Button variant="outline" fullWidth>📊 Export Transactions</Button>
            <Button variant="destructive" fullWidth>🗑️ Delete Account</Button>
          </CardContent>
        </Card>

        {/* About */}
        <Card>
          <CardHeader>
            <CardTitle>About</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            <p>JimFinance v1.0.0</p>
            <p>© 2024 JimFinance. All rights reserved.</p>
            <a href="#" className="text-primary hover:underline">Privacy Policy</a>
            <a href="#" className="text-primary hover:underline ml-4">Terms of Service</a>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
