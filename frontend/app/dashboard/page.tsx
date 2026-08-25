'use client';

import React, { useEffect } from 'react';
import Link from 'next/link';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { fetchDashboardSummary } from '@/store/slices/dashboardSlice';
import { AppLayout } from '@/components/layout/AppLayout';
import { MetricCard } from '@/components/dashboard/MetricCard';
import { HealthScoreChart } from '@/components/dashboard/HealthScoreChart';
import { SentimentDistributionChart } from '@/components/dashboard/SentimentDistributionChart';
import { RecentInteractionsWidget } from '@/components/dashboard/RecentInteractionsWidget';
import { AtRiskCustomersWidget } from '@/components/dashboard/AtRiskCustomersWidget';
import { RecentRisksWidget } from '@/components/dashboard/RecentRisksWidget';
import { Button } from '@/components/ui/Button';
import { Spinner } from '@/components/ui/Spinner';
import {
  Users,
  Activity,
  AlertTriangle,
  HeartHandshake,
  MessageSquare,
  Plus,
  RefreshCw,
} from 'lucide-react';

export default function DashboardPage() {
  const dispatch = useAppDispatch();
  const { summary, isLoading, error } = useAppSelector((state) => state.dashboard);
  const { user } = useAppSelector((state) => state.auth);

  useEffect(() => {
    dispatch(fetchDashboardSummary());
  }, [dispatch]);

  const handleRefresh = () => {
    dispatch(fetchDashboardSummary());
  };

  const isCsmOrAdmin = user?.role === 'ADMIN' || user?.role === 'CUSTOMER_SUCCESS_MANAGER';

  return (
    <AppLayout>
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div className="space-y-1">
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground">
            Executive CS Dashboard
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground">
            Real-time portfolio health, automated AI sentiment insights, and risk telemetry
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="secondary"
            size="sm"
            onClick={handleRefresh}
            isLoading={isLoading}
            leftIcon={<RefreshCw className="h-3.5 w-3.5" />}
          >
            Refresh
          </Button>

          {isCsmOrAdmin && (
            <>
              <Link href="/customers/new">
                <Button variant="secondary" size="sm" leftIcon={<Plus className="h-3.5 w-3.5" />}>
                  New Customer
                </Button>
              </Link>
              <Link href="/interactions/new">
                <Button variant="primary" size="sm" leftIcon={<Plus className="h-3.5 w-3.5" />}>
                  Log Meeting
                </Button>
              </Link>
            </>
          )}
        </div>
      </div>

      {isLoading && !summary && (
        <div className="py-16">
          <Spinner size={36} label="Loading dashboard metrics..." />
        </div>
      )}

      {error && (
        <div className="mb-6 rounded-xl border border-destructive/30 bg-destructive/10 p-4 text-sm font-medium text-destructive">
          {error}
        </div>
      )}

      {summary && (
        <div className="space-y-8">
          {/* Top Metric Cards Grid */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
            <MetricCard
              title="Total Accounts"
              value={summary.total_customers}
              subtitle="All registered accounts"
              icon={<Users className="h-5 w-5" />}
            />
            <MetricCard
              title="Active Accounts"
              value={summary.active_customers}
              subtitle="Healthy & adopting"
              icon={<Activity className="h-5 w-5 text-emerald-400" />}
            />
            <MetricCard
              title="At-Risk Accounts"
              value={summary.at_risk_customers}
              subtitle="Requires CSM intervention"
              icon={<AlertTriangle className="h-5 w-5 text-amber-400" />}
            />
            <MetricCard
              title="Avg Health Score"
              value={`${summary.average_health_score}/100`}
              subtitle="Weighted portfolio score"
              icon={<HeartHandshake className="h-5 w-5 text-purple-400" />}
            />
            <MetricCard
              title="Total Interactions"
              value={summary.total_interactions}
              subtitle="Meetings, calls & demos"
              icon={<MessageSquare className="h-5 w-5 text-pink-400" />}
            />
          </div>

          {/* Interactive Recharts Charts Grid */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <HealthScoreChart
              distribution={summary.health_distribution}
              averageScore={summary.average_health_score}
            />
            <SentimentDistributionChart distribution={summary.sentiment_distribution} />
          </div>

          {/* Widgets Grid */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <AtRiskCustomersWidget customers={summary.at_risk_customers_list} />
            <RecentRisksWidget risks={summary.recent_risks} />
            <RecentInteractionsWidget interactions={summary.recent_interactions} />
          </div>
        </div>
      )}
    </AppLayout>
  );
}
