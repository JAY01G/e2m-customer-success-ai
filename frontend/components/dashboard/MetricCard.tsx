/**
 * Executive Metric KPI Card Component.
 *
 * Displays single KPI metric value, change indicator trends, and category icon.
 */

import React from 'react';
import { Card } from '@/components/ui/Card';
import { cn } from '@/lib/utils';
import { MetricCardProps } from '@/types';

/**
 * Metric card component for high-level KPI dashboard values.
 */
export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  trend,
  className,
}) => {
  return (
    <Card
      className={cn(
        'relative overflow-hidden border-border/70 bg-card/70 backdrop-blur-md p-6 shadow-card hover:border-primary/40 transition-all duration-200',
        className
      )}
    >
      <div className="absolute top-0 left-0 h-full w-1 bg-gradient-to-b from-indigo-500 to-violet-500" />
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            {title}
          </span>
          <div className="text-3xl font-extrabold tracking-tight text-foreground">
            {value}
          </div>
          {subtitle && (
            <p className="text-xs text-muted-foreground">{subtitle}</p>
          )}
          {trend && (
            <div
              className={cn(
                'inline-flex items-center text-xs font-semibold mt-2',
                trend.isPositive ? 'text-emerald-400' : 'text-rose-400'
              )}
            >
              {trend.isPositive ? '+' : ''}
              {trend.value}
            </div>
          )}
        </div>

        <div className="flex h-11 w-11 items-center justify-center rounded-lg border border-border/80 bg-secondary/80 text-primary shadow-sm">
          {icon}
        </div>
      </div>
    </Card>
  );
};

