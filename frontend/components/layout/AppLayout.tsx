/**
 * Main Application Shell Layout.
 *
 * Provides authenticated page layout including top navigation bar, responsive sidebar,
 * and role-based route access guard.
 */

import React from 'react';
import { Navbar } from './Navbar';
import { Sidebar } from './Sidebar';
import { ProtectedRouteGuard } from './ProtectedRouteGuard';
import { AppLayoutProps } from '@/types';

/**
 * Global authenticated shell layout wrapper enforcing session check and layout framing.
 */
export const AppLayout: React.FC<AppLayoutProps> = ({
  children,
  allowedRoles,
}) => {
  return (
    <ProtectedRouteGuard allowedRoles={allowedRoles}>
      <div className="flex min-h-screen flex-col bg-background text-foreground">
        <Navbar />
        <div className="flex flex-1">
          <Sidebar />
          <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
            <div className="mx-auto max-w-7xl">{children}</div>
          </main>
        </div>
      </div>
    </ProtectedRouteGuard>
  );
};

