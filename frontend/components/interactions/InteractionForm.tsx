/**
 * Customer Touchpoint Interaction Logging Form Component.
 *
 * Captures customer selection, meeting type, duration, and notes with automated AI extraction option.
 */

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { interactionSchema, InteractionFormData } from '@/schemas';
import { InteractionFormProps } from '@/types';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Button } from '@/components/ui/Button';
import { Sparkles, Calendar, Clock, MessageSquare } from 'lucide-react';

/**
 * Form component for creating touchpoint interactions and triggering LLM analysis.
 */
export const InteractionForm: React.FC<InteractionFormProps> = ({
  customers,
  defaultCustomerId,
  onSubmit,
  isLoading = false,
  onCancel,
}) => {
  const customerOptions = customers.map((c) => ({
    value: c.id,
    label: `${c.company_name} (${c.name})`,
  }));

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<InteractionFormData>({
    resolver: zodResolver(interactionSchema),
    defaultValues: {
      customer_id: defaultCustomerId || (customers[0]?.id ?? ''),
      type: 'MEETING',
      title: '',
      meeting_date: new Date().toISOString().split('T')[0],
      duration_minutes: 30,
      notes: '',
      generate_ai_insight: true,
    },
  });

  const currentNotes = watch('notes') || '';

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Select
          label="Customer Account *"
          options={customerOptions}
          {...register('customer_id')}
          error={errors.customer_id?.message}
        />

        <Select
          label="Interaction Type *"
          options={[
            { value: 'MEETING', label: 'Customer Meeting / Review' },
            { value: 'CALL', label: 'Phone Call / Check-in' },
            { value: 'EMAIL', label: 'Email Thread' },
            { value: 'DEMO', label: 'Product Demonstration' },
            { value: 'OTHER', label: 'Other Activity' },
          ]}
          {...register('type')}
          error={errors.type?.message}
        />

        <div className="sm:col-span-2">
          <Input
            label="Meeting Subject / Title *"
            placeholder="e.g. Q3 Executive Business Review & Expansion Discussion"
            leftIcon={<MessageSquare className="h-4 w-4" />}
            {...register('title')}
            error={errors.title?.message}
            helperText="Min 2 characters, max 200 characters"
          />
        </div>

        <Input
          label="Meeting Date *"
          type="date"
          leftIcon={<Calendar className="h-4 w-4" />}
          {...register('meeting_date')}
          error={errors.meeting_date?.message}
        />

        <Input
          label="Duration (Minutes)"
          type="number"
          min={1}
          max={1440}
          leftIcon={<Clock className="h-4 w-4" />}
          {...register('duration_minutes', { valueAsNumber: true })}
          error={errors.duration_minutes?.message}
          helperText="Standard meeting duration (1 - 1440 minutes)"
        />
      </div>

      <div className="space-y-1.5">
        <div className="flex items-center justify-between">
          <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Meeting Notes & Raw Transcript *
          </label>
          <div className="flex items-center gap-3">
            <span className="text-[11px] text-muted-foreground">
              {currentNotes.length.toLocaleString()} / 20,000 chars (min 5)
            </span>
            <span className="inline-flex items-center gap-1 text-[11px] font-bold text-indigo-400">
              <Sparkles className="h-3 w-3" /> Auto AI Analysis
            </span>
          </div>
        </div>

        <textarea
          rows={6}
          className={`w-full rounded-lg border bg-card/60 px-3 py-2 text-sm text-foreground ring-offset-background placeholder:text-muted-foreground/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1 ${
            errors.notes ? 'border-destructive focus-visible:ring-destructive' : 'border-input'
          }`}
          placeholder="Paste meeting discussion notes, client requests, positive remarks, and concerns. The AI will automatically extract action items, sentiment, and risks..."
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
          rightIcon={<Sparkles className="h-4 w-4" />}
        >
          Save & Run AI Analysis
        </Button>
      </div>
    </form>
  );
};
