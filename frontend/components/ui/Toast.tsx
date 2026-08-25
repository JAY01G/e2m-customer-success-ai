'use client';

import React, { useEffect, useState } from 'react';
import { ToastItem as ToastItemType, ToastType } from '@/types';
import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ToastProps {
  toast: ToastItemType;
  onDismiss: (id: string) => void;
}

const TOAST_ICONS: Record<ToastType, React.ReactNode> = {
  success: <CheckCircle2 className="h-5 w-5 text-emerald-400 shrink-0 mt-0.5" />,
  error: <AlertCircle className="h-5 w-5 text-rose-400 shrink-0 mt-0.5" />,
  warning: <AlertTriangle className="h-5 w-5 text-amber-400 shrink-0 mt-0.5" />,
  info: <Info className="h-5 w-5 text-indigo-400 shrink-0 mt-0.5" />,
};

const TOAST_STYLES: Record<ToastType, { container: string; progressBar: string; glow: string }> = {
  success: {
    container: 'border-emerald-500/30 bg-gradient-to-r from-emerald-950/40 via-card/95 to-card/95 shadow-emerald-950/50',
    progressBar: 'bg-gradient-to-r from-emerald-500 to-teal-400',
    glow: 'shadow-[0_0_15px_-3px_rgba(16,185,129,0.2)]',
  },
  error: {
    container: 'border-rose-500/30 bg-gradient-to-r from-rose-950/40 via-card/95 to-card/95 shadow-rose-950/50',
    progressBar: 'bg-gradient-to-r from-rose-500 to-red-400',
    glow: 'shadow-[0_0_15px_-3px_rgba(244,63,94,0.2)]',
  },
  warning: {
    container: 'border-amber-500/30 bg-gradient-to-r from-amber-950/40 via-card/95 to-card/95 shadow-amber-950/50',
    progressBar: 'bg-gradient-to-r from-amber-500 to-orange-400',
    glow: 'shadow-[0_0_15px_-3px_rgba(245,158,11,0.2)]',
  },
  info: {
    container: 'border-indigo-500/30 bg-gradient-to-r from-indigo-950/40 via-card/95 to-card/95 shadow-indigo-950/50',
    progressBar: 'bg-gradient-to-r from-indigo-500 to-violet-400',
    glow: 'shadow-[0_0_15px_-3px_rgba(99,102,241,0.2)]',
  },
};

export const Toast: React.FC<ToastProps> = ({ toast, onDismiss }) => {
  const { id, title, message, type = 'info', duration = 4000 } = toast;
  const [isExiting, setIsExiting] = useState(false);
  const [progress, setProgress] = useState(100);

  const styleConfig = TOAST_STYLES[type] || TOAST_STYLES.info;
  const icon = TOAST_ICONS[type] || TOAST_ICONS.info;

  useEffect(() => {
    if (duration <= 0) return;

    // Start progress animation
    const startTime = Date.now();
    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const remaining = Math.max(0, 100 - (elapsed / duration) * 100);
      setProgress(remaining);

      if (remaining <= 0) {
        clearInterval(interval);
      }
    }, 20);

    const timer = setTimeout(() => {
      handleDismiss();
    }, duration);

    return () => {
      clearInterval(interval);
      clearTimeout(timer);
    };
  }, [id, duration]);

  const handleDismiss = () => {
    setIsExiting(true);
    setTimeout(() => {
      onDismiss(id);
    }, 200);
  };

  return (
    <div
      role="alert"
      aria-live="assertive"
      data-testid={`toast-${type}`}
      className={cn(
        'relative overflow-hidden pointer-events-auto w-full max-w-sm sm:max-w-md rounded-xl border backdrop-blur-xl p-4 shadow-2xl transition-all duration-200 ease-out',
        styleConfig.container,
        styleConfig.glow,
        isExiting
          ? 'opacity-0 translate-x-4 scale-95'
          : 'opacity-100 translate-x-0 scale-100 animate-in fade-in slide-in-from-top-2'
      )}
    >
      <div className="flex items-start gap-3">
        {icon}
        <div className="flex-1 min-w-0 pr-2">
          <h4 className="text-xs sm:text-sm font-bold text-foreground leading-tight tracking-tight">
            {title}
          </h4>
          {message && (
            <p className="text-xs text-muted-foreground mt-1 leading-relaxed break-words">
              {message}
            </p>
          )}
        </div>

        <button
          type="button"
          onClick={handleDismiss}
          aria-label="Dismiss alert"
          className="text-muted-foreground hover:text-foreground rounded-lg p-1 transition-colors hover:bg-white/5 -mr-1 -mt-1 focus:outline-none focus:ring-1 focus:ring-primary"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {duration > 0 && (
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-white/5">
          <div
            className={cn('h-full transition-all ease-linear', styleConfig.progressBar)}
            style={{ width: `${progress}%` }}
          />
        </div>
      )}
    </div>
  );
};
