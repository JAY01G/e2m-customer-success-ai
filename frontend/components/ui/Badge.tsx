import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';
import { CustomerStatus, SentimentType, UserRole } from '@/types';

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wider transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-primary/20 text-primary-foreground border-primary/30',
        secondary: 'border-transparent bg-secondary text-secondary-foreground',
        outline: 'text-foreground border-border',
        success: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400',
        warning: 'border-amber-500/30 bg-amber-500/10 text-amber-400',
        danger: 'border-rose-500/30 bg-rose-500/10 text-rose-400',
        info: 'border-indigo-500/30 bg-indigo-500/10 text-indigo-400',
        purple: 'border-purple-500/30 bg-purple-500/10 text-purple-400',
      },
      size: {
        sm: 'px-2 py-0.2 text-[10px]',
        md: 'px-2.5 py-0.5 text-xs',
        lg: 'px-3 py-1 text-sm',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'md',
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {
  status?: CustomerStatus;
  sentiment?: SentimentType;
  role?: UserRole;
}

export const Badge: React.FC<BadgeProps> = ({
  className,
  variant,
  size,
  status,
  sentiment,
  role,
  children,
  ...props
}) => {
  if (status) {
    switch (status) {
      case 'ACTIVE':
        return (
          <div className={cn(badgeVariants({ variant: 'success', size }), className)} {...props}>
            <span className="mr-1.5 h-1.5 w-1.5 rounded-full bg-emerald-400" />
            ACTIVE
          </div>
        );
      case 'AT_RISK':
        return (
          <div className={cn(badgeVariants({ variant: 'warning', size }), className)} {...props}>
            <span className="mr-1.5 h-1.5 w-1.5 rounded-full bg-amber-400" />
            AT RISK
          </div>
        );
      case 'CHURNED':
        return (
          <div className={cn(badgeVariants({ variant: 'danger', size }), className)} {...props}>
            <span className="mr-1.5 h-1.5 w-1.5 rounded-full bg-rose-400" />
            CHURNED
          </div>
        );
      case 'PROSPECT':
        return (
          <div className={cn(badgeVariants({ variant: 'info', size }), className)} {...props}>
            <span className="mr-1.5 h-1.5 w-1.5 rounded-full bg-indigo-400" />
            PROSPECT
          </div>
        );
    }
  }

  if (sentiment) {
    switch (sentiment) {
      case 'Positive':
        return (
          <div className={cn(badgeVariants({ variant: 'success', size }), className)} {...props}>
            Positive
          </div>
        );
      case 'Neutral':
        return (
          <div className={cn(badgeVariants({ variant: 'info', size }), className)} {...props}>
            Neutral
          </div>
        );
      case 'Negative':
        return (
          <div className={cn(badgeVariants({ variant: 'danger', size }), className)} {...props}>
            Negative
          </div>
        );
    }
  }

  if (role) {
    switch (role) {
      case 'ADMIN':
        return (
          <div className={cn(badgeVariants({ variant: 'purple', size }), className)} {...props}>
            ADMIN
          </div>
        );
      case 'CUSTOMER_SUCCESS_MANAGER':
        return (
          <div className={cn(badgeVariants({ variant: 'info', size }), className)} {...props}>
            CSM
          </div>
        );
      case 'VIEWER':
        return (
          <div className={cn(badgeVariants({ variant: 'secondary', size }), className)} {...props}>
            VIEWER
          </div>
        );
    }
  }

  return (
    <div className={cn(badgeVariants({ variant, size }), className)} {...props}>
      {children}
    </div>
  );
};
