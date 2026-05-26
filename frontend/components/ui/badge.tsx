'use client'

import * as React from 'react'
import { cn } from '@/utils'

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'success' | 'warning' | 'destructive' | 'info'
  size?: 'sm' | 'md'
}

const Badge = React.forwardRef<HTMLDivElement, BadgeProps>(
  ({ className, variant = 'default', size = 'md', ...props }, ref) => {
    const variants = {
      default: 'bg-primary/10 text-primary border border-primary/20',
      success: 'bg-success/10 text-success border border-success/20',
      warning: 'bg-warning/10 text-warning border border-warning/20',
      destructive: 'bg-destructive/10 text-destructive border border-destructive/20',
      info: 'bg-info/10 text-info border border-info/20',
    }

    const sizes = {
      sm: 'px-2 py-1 text-xs font-medium rounded',
      md: 'px-3 py-1.5 text-sm font-medium rounded-md',
    }

    return (
      <div
        ref={ref}
        className={cn('inline-flex items-center', variants[variant], sizes[size], className)}
        {...props}
      />
    )
  }
)
Badge.displayName = 'Badge'

export interface ChipProps extends React.HTMLAttributes<HTMLDivElement> {
  onRemove?: () => void
  variant?: 'default' | 'filled'
}

const Chip = React.forwardRef<HTMLDivElement, ChipProps>(
  ({ className, onRemove, variant = 'default', children, ...props }, ref) => {
    const variants = {
      default: 'bg-muted text-muted-foreground hover:bg-muted/80',
      filled: 'bg-primary text-primary-foreground',
    }

    return (
      <div
        ref={ref}
        className={cn(
          'inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-smooth',
          variants[variant],
          className
        )}
        {...props}
      >
        {children}
        {onRemove && (
          <button
            onClick={onRemove}
            className="ml-1 hover:opacity-70 transition-smooth"
            aria-label="Remove"
          >
            ✕
          </button>
        )}
      </div>
    )
  }
)
Chip.displayName = 'Chip'

export { Badge, Chip }
