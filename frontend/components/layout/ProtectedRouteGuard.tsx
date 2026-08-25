/**
 * Protected Route Guard Component.
 *
 * Verifies JWT token existence, loads user profile on cold start, and renders access restriction
 * warning cards for unauthorized roles.
 */

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { fetchCurrentUser } from '@/store/slices/authSlice';
import { ProtectedRouteGuardProps } from '@/types';
import { getStorageToken } from '@/lib/helpers';
import { Spinner } from '@/components/ui/Spinner';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { ShieldAlert, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

/**
 * Route protection higher-order component checking authentication and RBAC permissions.
 */
export const ProtectedRouteGuard: React.FC<ProtectedRouteGuardProps> = ({
  children,
  allowedRoles,
}) => {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const { user, isAuthenticated, token } = useAppSelector((state) => state.auth);
  const [isInitializing, setIsInitializing] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const storedToken = token || getStorageToken();

      if (!storedToken) {
        router.replace('/login');
        return;
      }

      if (!user) {
        try {
          await dispatch(fetchCurrentUser()).unwrap();
        } catch {
          router.replace('/login');
          return;
        }
      }

      setIsInitializing(false);
    };

    checkAuth();
  }, [dispatch, router, token, user]);

  if (isInitializing) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <Spinner size={36} label="Verifying session..." />
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return null;
  }

  // RBAC check
  if (allowedRoles && allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
    return (
      <div className="flex min-h-screen items-center justify-center p-6 bg-background">
        <Card className="max-w-md w-full text-center p-8 space-y-4">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/30">
            <ShieldAlert className="h-7 w-7" />
          </div>
          <div className="space-y-1">
            <h2 className="text-xl font-bold text-foreground">Access Restricted</h2>
            <p className="text-sm text-muted-foreground">
              Your role <strong className="text-primary">({user.role})</strong> is not authorized to access this section.
            </p>
          </div>

          <Link href="/dashboard" className="block pt-2">
            <Button variant="secondary" className="w-full" leftIcon={<ArrowLeft className="h-4 w-4" />}>
              Return to Dashboard
            </Button>
          </Link>
        </Card>
      </div>
    );
  }

  return <>{children}</>;
};

