import React from 'react';
import { VariantProps } from 'class-variance-authority';
import { User, UserRole } from './auth';
import { Customer, CustomerStatus, CustomerQueryParams } from './customer';
import { Interaction, InteractionQueryParams, InteractionType } from './interaction';
import { AIInsight, SentimentType } from './insight';
import { HealthDistribution, SentimentDistribution, RiskSummary } from './dashboard';
import { CustomerFormData, InteractionFormData } from '@/schemas';

// Primitive Props
export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive' | 'danger' | 'link';
  size?: 'default' | 'sm' | 'md' | 'lg' | 'icon';
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export interface SelectOption {
  value: string;
  label: string;
}

export interface SelectProps
  extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: SelectOption[];
  error?: string;
  helperText?: string;
}

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'secondary' | 'outline' | 'success' | 'warning' | 'danger' | 'info' | 'purple';
  size?: 'sm' | 'md' | 'lg';
  status?: CustomerStatus;
  sentiment?: SentimentType;
  role?: UserRole;
}

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  hover?: boolean;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

export interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  totalItems?: number;
  pageSize?: number;
  className?: string;
}

export interface SpinnerProps {
  size?: number | 'sm' | 'md' | 'lg';
  label?: string;
  className?: string;
}

// Layout Props
export interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
}

export interface AppLayoutProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
}

export interface ProtectedRouteGuardProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
}

// Dashboard Widget & Chart Props
export interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  trend?: {
    value: string;
    isPositive: boolean;
  };
  accentColor?: string;
  className?: string;
}

export interface HealthScoreChartProps {
  distribution: HealthDistribution;
  averageScore: number;
}

export interface SentimentDistributionChartProps {
  distribution: SentimentDistribution;
}

export interface AtRiskCustomersWidgetProps {
  customers: Customer[];
}

export interface RecentInteractionsWidgetProps {
  interactions: Interaction[];
}

export interface RecentRisksWidgetProps {
  risks: RiskSummary[];
}

// Customer Domain Props
export interface CustomerTableProps {
  customers: Customer[];
  onDelete?: (id: string, name: string) => void;
  isLoading?: boolean;
}

export interface CustomerFiltersProps {
  onFilterChange: (filters: CustomerQueryParams) => void;
  initialFilters?: CustomerQueryParams;
}

export interface CustomerFormProps {
  initialData?: Customer;
  onSubmit: (data: CustomerFormData) => Promise<void>;
  isLoading?: boolean;
  onCancel?: () => void;
}

// Interaction Domain Props
export interface InteractionTableProps {
  interactions: Interaction[];
  onDelete?: (id: string, title: string) => void;
  isLoading?: boolean;
}

export interface InteractionFiltersProps {
  onFilterChange: (filters: InteractionQueryParams) => void;
  initialFilters?: InteractionQueryParams;
}

export interface InteractionFormProps {
  customers: Customer[];
  defaultCustomerId?: string;
  onSubmit: (data: InteractionFormData) => Promise<void>;
  isLoading?: boolean;
  onCancel?: () => void;
}

// Insight Domain Props
export interface AIInsightViewProps {
  insight?: AIInsight | null;
  onRegenerate: () => void;
  isGenerating?: boolean;
}

// Toast Notification Types
export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface ToastItem {
  id: string;
  title: string;
  message?: string;
  type: ToastType;
  duration?: number;
}

export interface ToastOptions {
  title: string;
  message?: string;
  type?: ToastType;
  duration?: number;
}

export interface ToastContextValue {
  toasts: ToastItem[];
  addToast: (toast: Omit<ToastItem, 'id'>) => string;
  removeToast: (id: string) => void;
  clearToasts: () => void;
  toast: {
    (props: ToastOptions): string;
    success: (title: string, message?: string, duration?: number) => string;
    error: (title: string, message?: string, duration?: number) => string;
    warning: (title: string, message?: string, duration?: number) => string;
    info: (title: string, message?: string, duration?: number) => string;
    dismiss: (id: string) => void;
    clear: () => void;
  };
}

