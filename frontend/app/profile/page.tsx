'use client';

import React from 'react';
import { useAppSelector } from '@/store/hooks';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from '@/components/ui/Table';
import { Shield, Check, X, Server, Sparkles, Database } from 'lucide-react';

export default function ProfilePage() {
  const { user } = useAppSelector((state) => state.auth);

  if (!user) return null;

  const permissionsMatrix = [
    { feature: 'View Dashboard & Metrics', admin: true, csm: true, viewer: true },
    { feature: 'View Customers & Health Scores', admin: true, csm: true, viewer: true },
    { feature: 'Create & Update Customers', admin: true, csm: true, viewer: false },
    { feature: 'Delete Customers', admin: true, csm: false, viewer: false },
    { feature: 'Log Meeting Notes & Interactions', admin: true, csm: true, viewer: false },
    { feature: 'Generate & Regenerate AI Insights', admin: true, csm: true, viewer: false },
    { feature: 'Delete Meeting Logs', admin: true, csm: false, viewer: false },
    { feature: 'Manage Users & RBAC Roles', admin: true, csm: false, viewer: false },
  ];

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="space-y-1">
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground">
            User Profile & System Permissions
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground">
            Current authenticated session details and role-based access control policies
          </p>
        </div>

        {/* User Card */}
        <Card padding="lg" className="border-border/80 bg-card/80 shadow-card">
          <div className="flex items-center gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-r from-indigo-600 to-violet-600 text-2xl font-extrabold text-white shadow-glow">
              {user.name.charAt(0).toUpperCase()}
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-3">
                <h2 className="text-lg font-bold text-foreground">
                  {user.name}
                </h2>
                <Badge role={user.role} />
              </div>
              <p className="text-xs text-muted-foreground">
                {user.email} &bull; Account Status:{' '}
                <span className="font-semibold text-emerald-400">
                  {user.is_active ? 'Active' : 'Inactive'}
                </span>
              </p>
            </div>
          </div>
        </Card>

        {/* Role Matrix */}
        <Card padding="lg" className="border-border/80 bg-card/80 shadow-card space-y-4">
          <div className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-indigo-400" />
            <h3 className="text-base font-bold text-foreground">
              Role-Based Access Control (RBAC) Matrix
            </h3>
          </div>

          <div className="overflow-hidden rounded-lg border border-border/80">
            <Table>
              <TableHeader className="bg-secondary/40">
                <TableRow>
                  <TableHead>System Capability</TableHead>
                  <TableHead className="text-center">Admin</TableHead>
                  <TableHead className="text-center">CSM</TableHead>
                  <TableHead className="text-center">Viewer</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {permissionsMatrix.map((p, idx) => (
                  <TableRow key={idx}>
                    <TableCell className="font-medium text-xs text-slate-200">
                      {p.feature}
                    </TableCell>
                    <TableCell className="text-center">
                      {p.admin ? (
                        <Check className="h-4 w-4 text-emerald-400 mx-auto" />
                      ) : (
                        <X className="h-4 w-4 text-rose-400 mx-auto" />
                      )}
                    </TableCell>
                    <TableCell className="text-center">
                      {p.csm ? (
                        <Check className="h-4 w-4 text-emerald-400 mx-auto" />
                      ) : (
                        <X className="h-4 w-4 text-rose-400 mx-auto" />
                      )}
                    </TableCell>
                    <TableCell className="text-center">
                      {p.viewer ? (
                        <Check className="h-4 w-4 text-emerald-400 mx-auto" />
                      ) : (
                        <X className="h-4 w-4 text-rose-400 mx-auto" />
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </Card>

        {/* System Telemetry & Integrations */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Card padding="md" className="border-border/80 bg-card/60 space-y-1">
            <div className="flex items-center gap-2 text-indigo-400">
              <Server className="h-4 w-4" />
              <span className="text-xs font-bold uppercase tracking-wider">FastAPI Backend</span>
            </div>
            <p className="text-xs text-muted-foreground">
              v1.0.0 (Python 3.11/3.14 MVC)
            </p>
          </Card>

          <Card padding="md" className="border-border/80 bg-card/60 space-y-1">
            <div className="flex items-center gap-2 text-purple-400">
              <Sparkles className="h-4 w-4" />
              <span className="text-xs font-bold uppercase tracking-wider">AI Intelligence</span>
            </div>
            <p className="text-xs text-muted-foreground">
              Schema Validation & Fallback Active
            </p>
          </Card>

          <Card padding="md" className="border-border/80 bg-card/60 space-y-1">
            <div className="flex items-center gap-2 text-emerald-400">
              <Database className="h-4 w-4" />
              <span className="text-xs font-bold uppercase tracking-wider">Redis & Postgres</span>
            </div>
            <p className="text-xs text-muted-foreground">
              Normalized Schema & Active Cache
            </p>
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}
