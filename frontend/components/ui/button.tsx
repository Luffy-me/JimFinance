'use client'

import * as React from 'react'
import { cn } from '@/utils'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'destructive' | 'outline'
  size?: 'sm' | 'md' | 'lg'
  isLoading?: boolean
  fullWidth?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = 'primary',
      size = 'md',
      isLoading = false,
      fullWidth = false,
      disabled,
      children,
      ...props
    },
    ref
  ) => {
    const baseStyles = 'inline-flex items-center justify-center font-medium transition-smooth focus-ring rounded-md'

    const variants = {
      primary: 'bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50',
      secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/90 disabled:opacity-50',
      ghost: 'hover:bg-muted disabled:opacity-50',
      destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90 disabled:opacity-50',
      outline: 'border border-border hover:bg-muted disabled:opacity-50',
    }

    const sizes = {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-4 py-2 text-base',
      lg: 'px-6 py-3 text-lg',
    }

    return (
      <button
        className={cn(
          baseStyles,
          variants[variant],
          sizes[size],
          fullWidth && 'w-full',
          isLoading && 'opacity-50 pointer-events-none',
          className
        )}
        disabled={disabled || isLoading}
        ref={ref}
        {...props}
      >
        {isLoading && <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />}
        {children}
      </button>
    )
  }
)
Button.displayName = 'Button'

export { Button }
