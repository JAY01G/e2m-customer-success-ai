'use client';

import React, { Suspense, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { fetchCustomers } from '@/store/slices/customerSlice';
import { createInteraction } from '@/store/slices/interactionSlice';
import { useToast } from '@/components/providers/ToastProvider';
import { AppLayout } from '@/components/layout/AppLayout';
import { InteractionForm } from '@/components/interactions/InteractionForm';
import { Card } from '@/components/ui/Card';
import { Spinner } from '@/components/ui/Spinner';
import { Button } from '@/components/ui/Button';
import { InteractionFormData } from '@/schemas';
import { ArrowLeft, UserPlus } from 'lucide-react';

function NewInteractionContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const defaultCustomerId = searchParams.get('customer_id') || undefined;

  const dispatch = useAppDispatch();
  const { toast } = useToast();
  const { customers, isLoading: isCustomersLoading } = useAppSelector(
    (state) => state.customers
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    dispatch(fetchCustomers({ page_size: 100 }));
  }, [dispatch]);

  const handleSubmit = async (data: InteractionFormData) => {
    setIsSubmitting(true);
    setError(null);
    try {
      const result = await dispatch(createInteraction(data)).unwrap();
      toast.success('Meeting Notes Logged', 'Interaction saved and AI analysis triggered.');
      router.push(`/interactions/${result.id}`);
    } catch (err: any) {
      const msg = err.message || 'Failed to create interaction';
      setError(msg);
      toast.error('Failed to Log Meeting', msg);
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <Link
        href="/interactions"
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="h-4 w-4" /> Back to Interactions
      </Link>

      <div className="space-y-1">
        <h1 className="text-2xl font-extrabold tracking-tight text-foreground">
          Log Meeting & Interaction Notes
        </h1>
        <p className="text-xs text-muted-foreground">
          Record customer discussions. AI will automatically extract action items, sentiment, and risks.
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-xs font-medium text-destructive">
          {error}
        </div>
      )}

      <Card padding="lg" className="border-border/80 bg-card/80 shadow-card">
        {isCustomersLoading && customers.length === 0 ? (
          <div className="py-8">
            <Spinner size={28} label="Loading customers..." />
          </div>
        ) : customers.length === 0 ? (
          <div className="text-center py-8 space-y-3">
            <p className="text-xs text-muted-foreground">
              Please create at least one customer account before logging an interaction.
            </p>
            <Link href="/customers/new">
              <Button variant="primary" size="sm" leftIcon={<UserPlus className="h-4 w-4" />}>
                Create Customer
              </Button>
            </Link>
          </div>
        ) : (
          <InteractionForm
            customers={customers}
            defaultCustomerId={defaultCustomerId}
            onSubmit={handleSubmit}
            isLoading={isSubmitting}
            onCancel={() => router.push('/interactions')}
          />
        )}
      </Card>
    </div>
  );
}

export default function NewInteractionPage() {
  return (
    <AppLayout allowedRoles={['ADMIN', 'CUSTOMER_SUCCESS_MANAGER']}>
      <Suspense
        fallback={
          <div className="py-16">
            <Spinner size={36} label="Loading form..." />
          </div>
        }
      >
        <NewInteractionContent />
      </Suspense>
    </AppLayout>
  );
}
