'use client';

import React, { createContext, useContext, useState, useCallback, useEffect, useMemo } from 'react';
import { ToastItem, ToastOptions, ToastContextValue, ToastType } from '@/types';
import { Toast } from '@/components/ui/Toast';

const ToastContext = createContext<ToastContextValue | null>(null);

const DEFAULT_DURATION = 4000;

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const recentToastsRef = React.useRef<Map<string, number>>(new Map());

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const clearToasts = useCallback(() => {
    setToasts([]);
  }, []);

  const addToast = useCallback((toastData: Omit<ToastItem, 'id'>): string => {
    const key = `${toastData.type || 'info'}:${toastData.title}:${toastData.message || ''}`;
    const now = Date.now();
    const lastTime = recentToastsRef.current.get(key) || 0;

    // Prevent duplicate toast if identical notification was triggered in last 2.0s
    if (now - lastTime < 2000) {
      return '';
    }
    recentToastsRef.current.set(key, now);

    const id = `toast-${now}-${Math.random().toString(36).substring(2, 9)}`;
    const newToast: ToastItem = {
      id,
      title: toastData.title,
      message: toastData.message,
      type: toastData.type || 'info',
      duration: toastData.duration !== undefined ? toastData.duration : DEFAULT_DURATION,
    };

    // Ensure only one active toast notification is displayed on screen at a time
    setToasts([newToast]);
    return id;
  }, []);

  // Listen for global custom events for toasts triggered from outside React tree (e.g. Axios interceptor)
  useEffect(() => {
    const handleGlobalToast = (event: Event) => {
      const customEvent = event as CustomEvent<ToastOptions>;
      if (customEvent.detail && customEvent.detail.title) {
        addToast({
          title: customEvent.detail.title,
          message: customEvent.detail.message,
          type: customEvent.detail.type || 'info',
          duration: customEvent.detail.duration,
        });
      }
    };

    window.addEventListener('successai:toast', handleGlobalToast);
    return () => {
      window.removeEventListener('successai:toast', handleGlobalToast);
    };
  }, [addToast]);

  const toastMethods = useMemo(() => {
    const fn = (props: ToastOptions): string => {
      return addToast({
        title: props.title,
        message: props.message,
        type: props.type || 'info',
        duration: props.duration,
      });
    };

    fn.success = (title: string, message?: string, duration?: number): string => {
      return addToast({ title, message, type: 'success', duration });
    };

    fn.error = (title: string, message?: string, duration?: number): string => {
      return addToast({ title, message, type: 'error', duration });
    };

    fn.warning = (title: string, message?: string, duration?: number): string => {
      return addToast({ title, message, type: 'warning', duration });
    };

    fn.info = (title: string, message?: string, duration?: number): string => {
      return addToast({ title, message, type: 'info', duration });
    };

    fn.dismiss = (id: string): void => {
      removeToast(id);
    };

    fn.clear = (): void => {
      clearToasts();
    };

    return fn;
  }, [addToast, removeToast, clearToasts]);

  const contextValue = useMemo<ToastContextValue>(
    () => ({
      toasts,
      addToast,
      removeToast,
      clearToasts,
      toast: toastMethods,
    }),
    [toasts, addToast, removeToast, clearToasts, toastMethods]
  );

  return (
    <ToastContext.Provider value={contextValue}>
      {children}

      {/* Floating Toast Notification Container - Single Toast */}
      <div
        aria-live="polite"
        className="fixed top-4 right-4 z-50 flex flex-col gap-2.5 pointer-events-none max-w-sm sm:max-w-md w-full px-4 sm:px-0"
      >
        {toasts.map((t) => (
          <Toast key={t.id} toast={t} onDismiss={removeToast} />
        ))}
      </div>
    </ToastContext.Provider>
  );
};

/**
 * Custom React hook to access toast notifications.
 *
 * @returns {ToastContextValue} Hook providing `toast.success`, `toast.error`, etc.
 */
export const useToast = (): ToastContextValue => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

/**
 * Global helper to dispatch toast notifications from non-component modules (e.g., API interceptors).
 */
export const emitToast = (options: ToastOptions): void => {
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent('successai:toast', { detail: options }));
  }
};
