'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { fetchCustomerById, updateCustomer } from '@/store/slices/customerSlice';
import { useToast } from '@/components/providers/ToastProvider';
import { AppLayout } from '@/components/layout/AppLayout';
import { CustomerForm } from '@/components/customers/CustomerForm';
import { Card } from '@/components/ui/Card';
import { Spinner } from '@/components/ui/Spinner';
import { CustomerFormData } from '@/schemas';
import { ArrowLeft } from 'lucide-react';

export default function EditCustomerPage() {
  const { id } = useParams() as { id: string };
  const router = useRouter();
  const dispatch = useAppDispatch();
  const { toast } = useToast();
  const { selectedCustomer: customer, isLoading } = useAppSelector(
    (state) => state.customers
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      dispatch(fetchCustomerById(id));
    }
  }, [id, dispatch]);

  const handleSubmit = async (data: CustomerFormData) => {
    setIsSubmitting(true);
    setError(null);
    try {
      await dispatch(updateCustomer({ id, data })).unwrap();
      toast.success('Customer Updated', `${data.company_name} details were saved.`);
      router.push(`/customers/${id}`);
    } catch (err: any) {
      const msg = err.message || 'Failed to update customer';
      setError(msg);
      toast.error('Update Failed', msg);
      setIsSubmitting(false);
    }
  };

  if (isLoading || !customer) {
    return (
      <AppLayout allowedRoles={['ADMIN', 'CUSTOMER_SUCCESS_MANAGER']}>
        <div className="py-16">
          <Spinner size={36} label="Loading customer details..." />
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout allowedRoles={['ADMIN', 'CUSTOMER_SUCCESS_MANAGER']}>
      <div className="max-w-3xl mx-auto space-y-6">
        <Link
          href={`/customers/${id}`}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="h-4 w-4" /> Back to Customer Profile
        </Link>

        <div className="space-y-1">
          <h1 className="text-2xl font-extrabold tracking-tight text-foreground">
            Edit Customer: {customer.company_name}
          </h1>
          <p className="text-xs text-muted-foreground">
            Update account health metrics, key contacts, and lifecycle status
          </p>
        </div>

        {error && (
          <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-xs font-medium text-destructive">
            {error}
          </div>
        )}

        <Card padding="lg" className="border-border/80 bg-card/80 shadow-card">
          <CustomerForm
            initialData={customer}
            onSubmit={handleSubmit}
            isLoading={isSubmitting}
            onCancel={() => router.push(`/customers/${id}`)}
          />
        </Card>
      </div>
    </AppLayout>
  );
}
