import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, act, fireEvent } from '@testing-library/react';
import { Toast } from '@/components/ui/Toast';
import { ToastProvider, useToast } from '@/components/providers/ToastProvider';
import { ToastItem } from '@/types';

// Test consumer component
const TestConsumer = () => {
  const { toast } = useToast();

  return (
    <div className="p-4 space-y-2">
      <button onClick={() => toast.success('Success Title', 'Success detail message')}>
        Trigger Success
      </button>
      <button onClick={() => toast.error('Error Title', 'Error detail message')}>
        Trigger Error
      </button>
      <button onClick={() => toast.warning('Warning Title', 'Warning detail message')}>
        Trigger Warning
      </button>
      <button onClick={() => toast.info('Info Title', 'Info detail message')}>
        Trigger Info
      </button>
      <button onClick={() => toast.clear()}>Clear All</button>
    </div>
  );
};

describe('Toast Notification System', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('Toast Component', () => {
    it('renders success toast with title, message, and correct role', () => {
      const mockToast: ToastItem = {
        id: 'toast-1',
        title: 'Operation Completed',
        message: 'Your changes have been saved.',
        type: 'success',
        duration: 4000,
      };
      const onDismiss = vi.fn();

      render(<Toast toast={mockToast} onDismiss={onDismiss} />);

      expect(screen.getByRole('alert')).toBeInTheDocument();
      expect(screen.getByText('Operation Completed')).toBeInTheDocument();
      expect(screen.getByText('Your changes have been saved.')).toBeInTheDocument();
      expect(screen.getByTestId('toast-success')).toBeInTheDocument();
    });

    it('renders error toast with error styling and icon', () => {
      const mockToast: ToastItem = {
        id: 'toast-2',
        title: 'Validation Error',
        message: 'Please check your inputs.',
        type: 'error',
        duration: 4000,
      };
      const onDismiss = vi.fn();

      render(<Toast toast={mockToast} onDismiss={onDismiss} />);

      expect(screen.getByTestId('toast-error')).toBeInTheDocument();
      expect(screen.getByText('Validation Error')).toBeInTheDocument();
      expect(screen.getByText('Please check your inputs.')).toBeInTheDocument();
    });

    it('triggers dismiss callback when close button is clicked', async () => {
      const mockToast: ToastItem = {
        id: 'toast-3',
        title: 'Notice',
        message: 'Something happened',
        type: 'info',
        duration: 5000,
      };
      const onDismiss = vi.fn();

      render(<Toast toast={mockToast} onDismiss={onDismiss} />);

      const closeButton = screen.getByRole('button', { name: /dismiss/i });
      fireEvent.click(closeButton);

      // Fast forward the exit animation timeout
      act(() => {
        vi.advanceTimersByTime(250);
      });

      expect(onDismiss).toHaveBeenCalledWith('toast-3');
    });

    it('auto dismisses after duration expires', () => {
      const mockToast: ToastItem = {
        id: 'toast-4',
        title: 'Auto Dismiss',
        type: 'warning',
        duration: 3000,
      };
      const onDismiss = vi.fn();

      render(<Toast toast={mockToast} onDismiss={onDismiss} />);

      act(() => {
        vi.advanceTimersByTime(3000);
      });

      act(() => {
        vi.advanceTimersByTime(250);
      });

      expect(onDismiss).toHaveBeenCalledWith('toast-4');
    });
  });

  describe('ToastProvider & useToast Hook', () => {
    it('throws error when useToast is used outside of ToastProvider', () => {
      // Suppress console.error for expected error
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      expect(() => render(<TestConsumer />)).toThrow(
        'useToast must be used within a ToastProvider'
      );
      consoleSpy.mockRestore();
    });

    it('allows triggering success, error, warning, and info toasts', () => {
      render(
        <ToastProvider>
          <TestConsumer />
        </ToastProvider>
      );

      // Trigger success
      fireEvent.click(screen.getByText('Trigger Success'));
      expect(screen.getByText('Success Title')).toBeInTheDocument();
      expect(screen.getByText('Success detail message')).toBeInTheDocument();

      // Trigger error
      fireEvent.click(screen.getByText('Trigger Error'));
      expect(screen.getByText('Error Title')).toBeInTheDocument();
      expect(screen.getByText('Error detail message')).toBeInTheDocument();

      // Trigger warning
      fireEvent.click(screen.getByText('Trigger Warning'));
      expect(screen.getByText('Warning Title')).toBeInTheDocument();

      // Trigger info
      fireEvent.click(screen.getByText('Trigger Info'));
      expect(screen.getByText('Info Title')).toBeInTheDocument();
    });

    it('clears all toasts when clear is invoked', () => {
      render(
        <ToastProvider>
          <TestConsumer />
        </ToastProvider>
      );

      fireEvent.click(screen.getByText('Trigger Success'));
      expect(screen.getByText('Success Title')).toBeInTheDocument();

      fireEvent.click(screen.getByText('Clear All'));
      expect(screen.queryByText('Success Title')).not.toBeInTheDocument();
    });
  });
});
