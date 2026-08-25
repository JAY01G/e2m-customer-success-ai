/**
 * Navigation Bar Component.
 *
 * Renders the top application header with brand identity, current user status, and logout button.
 */

import React from 'react';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { logout } from '@/store/slices/authSlice';
import { getInitials } from '@/lib/helpers';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { ShieldCheck, LogOut } from 'lucide-react';
import Link from 'next/link';

/**
 * Top application header component with user identity display and sign out action.
 */
export const Navbar: React.FC = () => {
  const dispatch = useAppDispatch();
  const { user } = useAppSelector((state) => state.auth);

  const handleLogout = () => {
    dispatch(logout());
  };

  return (
    <header className="sticky top-0 z-40 flex h-16 w-full items-center justify-between border-b border-border/80 bg-background/80 px-6 backdrop-blur-md">
      {/* Brand logo */}
      <Link href="/dashboard" className="flex items-center gap-2.5">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-glow">
          <ShieldCheck className="h-5 w-5" />
        </div>
        <div className="flex flex-col">
          <span className="text-base font-extrabold tracking-tight text-foreground">
            SuccessAI
          </span>
          <span className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
            Customer Intelligence
          </span>
        </div>
      </Link>

      {/* User Actions */}
      <div className="flex items-center gap-3">
        {user && (
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 rounded-lg border border-border/60 bg-secondary/50 px-3 py-1.5">
              <div className="flex h-7 w-7 items-center justify-center rounded-full bg-indigo-500/20 text-xs font-bold text-indigo-300">
                {getInitials(user.name)}
              </div>
              <div className="flex flex-col text-left">
                <span className="text-xs font-bold text-foreground line-clamp-1">
                  {user.name}
                </span>
                <Badge role={user.role} size="sm" />
              </div>
            </div>

            <Button
              variant="secondary"
              size="sm"
              onClick={handleLogout}
              className="text-xs text-muted-foreground hover:text-destructive hover:border-destructive/40"
              leftIcon={<LogOut className="h-3.5 w-3.5" />}
            >
              Sign Out
            </Button>
          </div>
        )}
      </div>
    </header>
  );
};

