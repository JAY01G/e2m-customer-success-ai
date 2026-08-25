import React from 'react';
import { cn } from '@/lib/utils';
import { SpinnerProps } from '@/types';
import { Loader2 } from 'lucide-react';

export const Spinner: React.FC<SpinnerProps> = ({
  size = 'md',
  label,
  className,
}) => {
  const sizeClasses = typeof size === 'string' ? {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-10 w-10',
  }[size] : '';

  return (
    <div className={cn('flex flex-col items-center justify-center gap-3 py-6', className)}>
      <Loader2
        className={cn('animate-spin text-primary', sizeClasses)}
        style={typeof size === 'number' ? { width: size, height: size } : undefined}
      />
      {label && <p className="text-xs font-medium text-muted-foreground">{label}</p>}
    </div>
  );
};
