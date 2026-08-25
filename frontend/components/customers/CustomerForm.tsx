/**
 * Customer Account Input Form Component.
 *
 * Provides a validated React Hook Form with Zod resolver for creating and editing customer accounts.
 */

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { customerSchema, CustomerFormData } from '@/schemas';
import { CustomerFormProps } from '@/types';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Button } from '@/components/ui/Button';
import { Building, User, Mail, Phone, Briefcase, Activity } from 'lucide-react';

/**
 * Form component for creating or modifying customer profiles.
 */
export const CustomerForm: React.FC<CustomerFormProps> = ({
  initialData,
  onSubmit,
  isLoading = false,
  onCancel,
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CustomerFormData>({
    resolver: zodResolver(customerSchema),
    defaultValues: {
      name: initialData?.name || '',
      company_name: initialData?.company_name || '',
      email: initialData?.email || '',
      phone: initialData?.phone || '',
      industry: initialData?.industry || '',
      status: initialData?.status || 'ACTIVE',
      health_score: initialData?.health_score ?? 80,
      notes: initialData?.notes || '',
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Input
          label="Company Name *"
          placeholder="e.g. Acme Corporation"
          leftIcon={<Building className="h-4 w-4" />}
          {...register('company_name')}
          error={errors.company_name?.message}
        />

        <Input
          label="Primary Contact Name *"
          placeholder="e.g. Jane Doe"
          leftIcon={<User className="h-4 w-4" />}
          {...register('name')}
          error={errors.name?.message}
        />

        <Input
          label="Email Address *"
          type="email"
          placeholder="jane@acme.com"
          leftIcon={<Mail className="h-4 w-4" />}
          {...register('email')}
          error={errors.email?.message}
        />

        <Input
          label="Phone Number"
          placeholder="+1 555 123 4567"
          leftIcon={<Phone className="h-4 w-4" />}
          {...register('phone')}
          error={errors.phone?.message}
          helperText="Format: +1 555-123-4567 or local (min 7 digits)"
        />

        <Input
          label="Industry Vertical"
          placeholder="e.g. Enterprise SaaS, FinTech"
          leftIcon={<Briefcase className="h-4 w-4" />}
          {...register('industry')}
          error={errors.industry?.message}
        />

        <Select
          label="Lifecycle Status *"
          options={[
            { value: 'ACTIVE', label: 'Active Account' },
            { value: 'AT_RISK', label: 'At-Risk Account' },
            { value: 'PROSPECT', label: 'Prospect Account' },
            { value: 'CHURNED', label: 'Churned Account' },
          ]}
          {...register('status')}
          error={errors.status?.message}
        />

        <div className="sm:col-span-2">
          <Input
            label="Health Score (0 - 100) *"
            type="number"
            min={0}
            max={100}
            leftIcon={<Activity className="h-4 w-4" />}
            {...register('health_score')}
            error={errors.health_score?.message}
            helperText="80-100: Healthy (Green), 50-79: Moderate (Yellow), 0-49: Critical (Red)"
          />
        </div>
      </div>

      <div className="space-y-1.5">
        <div className="flex items-center justify-between">
          <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Account Notes & Strategic Objectives
          </label>
          <span className="text-[11px] text-muted-foreground">Max 5,000 characters</span>
        </div>
        <textarea
          rows={4}
          className={`w-full rounded-lg border bg-card/60 px-3 py-2 text-sm text-foreground ring-offset-background placeholder:text-muted-foreground/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1 ${
            errors.notes ? 'border-destructive focus-visible:ring-destructive' : 'border-input'
          }`}
          placeholder="Key milestones, renewal target date, organizational structure notes..."
          {...register('notes')}
        />
        {errors.notes && (
          <p className="text-xs font-medium text-destructive">{errors.notes.message}</p>
        )}
      </div>

      <div className="flex items-center justify-end gap-3 pt-4 border-t border-border/80">
        {onCancel && (
          <Button
            type="button"
            variant="secondary"
            onClick={onCancel}
            disabled={isLoading}
          >
            Cancel
          </Button>
        )}

        <Button
          type="submit"
          variant="primary"
          isLoading={isLoading}
        >
          {initialData ? 'Update Customer Profile' : 'Create Customer Account'}
        </Button>
      </div>
    </form>
  );
};
