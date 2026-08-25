'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAppDispatch } from '@/store/hooks';
import { createCustomer } from '@/store/slices/customerSlice';
import { useToast } from '@/components/providers/ToastProvider';
import { AppLayout } from '@/components/layout/AppLayout';
import { CustomerForm } from '@/components/customers/CustomerForm';
import { Card } from '@/components/ui/Card';
import { CustomerFormData } from '@/schemas';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function NewCustomerPage() {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (data: CustomerFormData) => {
    setIsLoading(true);
    setError(null);
    try {
      const created = await dispatch(createCustomer(data)).unwrap();
      toast.success('Customer Created', `${created.company_name} was created successfully.`);
      router.push('/customers');
    } catch (err: any) {
      const msg = err.message || 'Failed to create customer';
      setError(msg);
      toast.error('Creation Failed', msg);
      setIsLoading(false);
    }
  };

  return (
    <AppLayout allowedRoles={['ADMIN', 'CUSTOMER_SUCCESS_MANAGER']}>
      <div className="max-w-3xl mx-auto space-y-6">
        <Link
          href="/customers"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="h-4 w-4" /> Back to Customers
        </Link>

        <div className="space-y-1">
          <h1 className="text-2xl font-extrabold tracking-tight text-foreground">
            Create Customer Account
          </h1>
          <p className="text-xs text-muted-foreground">
            Register a new client company, assign initial health score, and configure account details
          </p>
        </div>

        {error && (
          <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-xs font-medium text-destructive">
            {error}
          </div>
        )}

        <Card padding="lg" className="border-border/80 bg-card/80 shadow-card">
          <CustomerForm
            onSubmit={handleSubmit}
            isLoading={isLoading}
            onCancel={() => router.push('/customers')}
          />
        </Card>
      </div>
    </AppLayout>
  );
}
