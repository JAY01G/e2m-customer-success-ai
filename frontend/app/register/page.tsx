'use client';

import React, { useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { registerSchema, RegisterFormData } from '@/schemas';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { registerUser, clearAuthError } from '@/store/slices/authSlice';
import { useToast } from '@/components/providers/ToastProvider';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Button } from '@/components/ui/Button';
import { ShieldCheck, Mail, Lock, User as UserIcon, ArrowRight } from 'lucide-react';

export default function RegisterPage() {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const { toast } = useToast();
  const { isAuthenticated, isLoading, error } = useAppSelector((state) => state.auth);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      name: '',
      email: '',
      password: '',
      role: 'CUSTOMER_SUCCESS_MANAGER',
    },
  });

  useEffect(() => {
    if (isAuthenticated) {
      router.replace('/dashboard');
    }
    return () => {
      dispatch(clearAuthError());
    };
  }, [isAuthenticated, router, dispatch]);

  const onSubmit = async (data: RegisterFormData) => {
    const result = await dispatch(registerUser(data));
    if (registerUser.fulfilled.match(result)) {
      toast.success('Account Created', `Welcome to SuccessAI, ${result.payload.user.name}!`);
      router.replace('/dashboard');
    } else if (registerUser.rejected.match(result)) {
      const errorMsg = (result.payload as string) || 'Registration could not be completed';
      toast.error('Registration Failed', errorMsg);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4 sm:p-6 bg-background bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-purple-900/20 via-background to-background">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center space-y-2">
          <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-glow">
            <ShieldCheck className="h-7 w-7" />
          </div>
          <h1 className="text-2xl font-extrabold tracking-tight text-foreground sm:text-3xl">
            SuccessAI
          </h1>
          <p className="text-xs text-muted-foreground">
            Create your account to start managing customer health
          </p>
        </div>

        <Card padding="lg" className="border-border/80 bg-card/80 shadow-card">
          <div className="space-y-1 mb-6">
            <h2 className="text-lg font-bold text-foreground">Create Account</h2>
            <p className="text-xs text-muted-foreground">
              Fill out the details below to join your organization workspace
            </p>
          </div>

          {error && (
            <div className="mb-4 rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-xs font-medium text-destructive">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              label="Full Name *"
              placeholder="e.g. Alex Mercer"
              leftIcon={<UserIcon className="h-4 w-4" />}
              {...register('name')}
              error={errors.name?.message}
            />

            <Input
              label="Email Address *"
              type="email"
              placeholder="alex@company.com"
              leftIcon={<Mail className="h-4 w-4" />}
              {...register('email')}
              error={errors.email?.message}
            />

            <Input
              label="Password *"
              type="password"
              placeholder="••••••••"
              leftIcon={<Lock className="h-4 w-4" />}
              {...register('password')}
              error={errors.password?.message}
              helperText="Min 8 chars: 1 uppercase, 1 lowercase, 1 number, 1 special symbol"
            />

            <Select
              label="Organization Role *"
              options={[
                { value: 'CUSTOMER_SUCCESS_MANAGER', label: 'Customer Success Manager (CSM)' },
                { value: 'ADMIN', label: 'Administrator (Admin)' },
                { value: 'VIEWER', label: 'Read-Only Viewer' },
              ]}
              {...register('role')}
              error={errors.role?.message}
            />

            <Button
              type="submit"
              variant="primary"
              size="lg"
              isLoading={isLoading}
              className="w-full mt-2"
              rightIcon={<ArrowRight className="h-4 w-4" />}
            >
              Register & Sign In
            </Button>
          </form>
        </Card>

        <p className="text-center text-xs text-muted-foreground">
          Already have an account?{' '}
          <Link href="/login" className="font-semibold text-primary hover:underline">
            Sign In
          </Link>
        </p>
      </div>
    </div>
  );
}
