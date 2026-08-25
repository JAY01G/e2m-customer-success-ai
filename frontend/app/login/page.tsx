'use client';

import React, { useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { loginSchema, LoginFormData } from '@/schemas';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { loginUser, clearAuthError } from '@/store/slices/authSlice';
import { useToast } from '@/components/providers/ToastProvider';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { ShieldCheck, Mail, Lock, ArrowRight } from 'lucide-react';

export default function LoginPage() {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const { toast } = useToast();
  const { isAuthenticated, isLoading, error } = useAppSelector((state) => state.auth);

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
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

  const onSubmit = async (data: LoginFormData) => {
    const result = await dispatch(loginUser(data));
    if (loginUser.fulfilled.match(result)) {
      toast.success('Welcome Back!', `Signed in as ${result.payload.user.name}`);
      router.replace('/dashboard');
    } else if (loginUser.rejected.match(result)) {
      const errorMsg = (result.payload as string) || 'Invalid email or password';
      toast.error('Authentication Failed', errorMsg);
    }
  };

  const handleQuickLogin = (email: string) => {
    setValue('email', email);
    setValue('password', 'Password123!');
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4 sm:p-6 bg-background bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/20 via-background to-background">
      <div className="w-full max-w-md space-y-6">
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-glow">
            <ShieldCheck className="h-7 w-7" />
          </div>
          <h1 className="text-2xl font-extrabold tracking-tight text-foreground sm:text-3xl">
            SuccessAI
          </h1>
          <p className="text-xs text-muted-foreground">
            AI-Powered Customer Success Intelligence Platform
          </p>
        </div>

        <Card padding="lg" className="border-border/80 bg-card/80 shadow-card">
          <div className="space-y-1 mb-6">
            <h2 className="text-lg font-bold text-foreground">Sign In</h2>
            <p className="text-xs text-muted-foreground">
              Enter your credentials to access the portfolio dashboard
            </p>
          </div>

          {error && (
            <div className="mb-4 rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-xs font-medium text-destructive">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              label="Email Address"
              type="email"
              placeholder="you@company.com"
              leftIcon={<Mail className="h-4 w-4" />}
              {...register('email')}
              error={errors.email?.message}
            />

            <Input
              label="Password"
              type="password"
              placeholder="••••••••"
              leftIcon={<Lock className="h-4 w-4" />}
              {...register('password')}
              error={errors.password?.message}
            />

            <Button
              type="submit"
              variant="primary"
              size="lg"
              isLoading={isLoading}
              className="w-full mt-2"
              rightIcon={<ArrowRight className="h-4 w-4" />}
            >
              Sign In to Platform
            </Button>
          </form>

          {/* Quick Demo Credentials */}
          <div className="mt-6 pt-5 border-t border-border/80 space-y-2">
            <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground block">
              Quick Fill Demo Accounts:
            </span>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => handleQuickLogin('admin@example.com')}
                className="rounded-lg border border-border bg-secondary/60 py-1.5 text-xs font-semibold text-foreground hover:bg-accent hover:border-primary/40 transition-colors"
              >
                Admin
              </button>
              <button
                type="button"
                onClick={() => handleQuickLogin('csm@example.com')}
                className="rounded-lg border border-border bg-secondary/60 py-1.5 text-xs font-semibold text-foreground hover:bg-accent hover:border-primary/40 transition-colors"
              >
                CSM
              </button>
              <button
                type="button"
                onClick={() => handleQuickLogin('viewer@example.com')}
                className="rounded-lg border border-border bg-secondary/60 py-1.5 text-xs font-semibold text-foreground hover:bg-accent hover:border-primary/40 transition-colors"
              >
                Viewer
              </button>
            </div>
          </div>
        </Card>

        <p className="text-center text-xs text-muted-foreground">
          Don&apos;t have an account?{' '}
          <Link href="/register" className="font-semibold text-primary hover:underline">
            Create an Account
          </Link>
        </p>
      </div>
    </div>
  );
}
