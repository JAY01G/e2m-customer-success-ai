'use client';

import React, { useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { fetchCustomerById } from '@/store/slices/customerSlice';
import { fetchInteractions } from '@/store/slices/interactionSlice';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Spinner } from '@/components/ui/Spinner';
import { formatDate, getHealthScoreCategory } from '@/lib/helpers';
import {
  ArrowLeft,
  Edit,
  Plus,
  Mail,
  Phone,
  Briefcase,
  User,
  Calendar,
  Sparkles,
} from 'lucide-react';

export default function CustomerDetailPage() {
  const { id } = useParams() as { id: string };
  const router = useRouter();
  const dispatch = useAppDispatch();

  const { selectedCustomer: customer, isLoading } = useAppSelector(
    (state) => state.customers
  );
  const { interactions } = useAppSelector((state) => state.interactions);
  const { user } = useAppSelector((state) => state.auth);

  useEffect(() => {
    if (id) {
      dispatch(fetchCustomerById(id));
      dispatch(fetchInteractions({ customer_id: id }));
    }
  }, [id, dispatch]);

  const isCsmOrAdmin =
    user?.role === 'ADMIN' || user?.role === 'CUSTOMER_SUCCESS_MANAGER';

  if (isLoading || !customer) {
    return (
      <AppLayout>
        <div className="py-16">
          <Spinner size={36} label="Loading customer details..." />
        </div>
      </AppLayout>
    );
  }

  const scoreInfo = getHealthScoreCategory(customer.health_score);

  return (
    <AppLayout>
      <div className="max-w-6xl mx-auto space-y-6">
        <Link
          href="/customers"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="h-4 w-4" /> Back to Customers
        </Link>

        {/* Top Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-3">
              <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground">
                {customer.company_name}
              </h1>
              <Badge status={customer.status} />
            </div>
            <p className="text-xs sm:text-sm text-muted-foreground">
              Primary Stakeholder: <span className="text-slate-200 font-medium">{customer.name}</span>
            </p>
          </div>

          <div className="flex items-center gap-2.5">
            {isCsmOrAdmin && (
              <>
                <Link href={`/customers/${customer.id}/edit`}>
                  <Button variant="secondary" size="sm" leftIcon={<Edit className="h-3.5 w-3.5" />}>
                    Edit Details
                  </Button>
                </Link>
                <Link href={`/interactions/new?customer_id=${customer.id}`}>
                  <Button variant="primary" size="sm" leftIcon={<Plus className="h-3.5 w-3.5" />}>
                    Log Meeting
                  </Button>
                </Link>
              </>
            )}
          </div>
        </div>

        {/* Profile Details & Health Score Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card padding="lg" className="lg:col-span-2 space-y-6 border-border/80 bg-card/80">
            <div>
              <h3 className="text-base font-bold text-foreground mb-4">
                Account Information
              </h3>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs text-muted-foreground">
                <div className="flex items-center gap-2.5">
                  <Mail className="h-4 w-4 text-primary" />
                  <span className="text-slate-200">{customer.email}</span>
                </div>
                <div className="flex items-center gap-2.5">
                  <Phone className="h-4 w-4 text-primary" />
                  <span className="text-slate-200">{customer.phone || 'No telephone provided'}</span>
                </div>
                <div className="flex items-center gap-2.5">
                  <Briefcase className="h-4 w-4 text-primary" />
                  <span className="text-slate-200">{customer.industry || 'No industry vertical'}</span>
                </div>
                <div className="flex items-center gap-2.5">
                  <User className="h-4 w-4 text-primary" />
                  <span className="text-slate-200">
                    Owner: {customer.owner ? customer.owner.name : 'Unassigned'}
                  </span>
                </div>
              </div>
            </div>

            {customer.notes && (
              <div className="pt-4 border-t border-border/80 space-y-1.5">
                <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground block">
                  Account Notes & Objectives
                </span>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {customer.notes}
                </p>
              </div>
            )}
          </Card>

          <Card padding="lg" className="flex flex-col items-center justify-center text-center border-border/80 bg-card/80 space-y-3">
            <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
              Health Telemetry Score
            </span>
            <div
              className={`flex h-24 w-24 items-center justify-center rounded-full border-2 text-3xl font-extrabold shadow-glow ${scoreInfo.badgeClass}`}
            >
              {customer.health_score}
            </div>
            <p className="text-xs text-muted-foreground max-w-[200px]">
              {scoreInfo.label}
            </p>
          </Card>
        </div>

        {/* Interaction History Timeline */}
        <div className="space-y-4 pt-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-foreground">
              Meeting & Interaction Timeline ({interactions.length})
            </h3>
          </div>

          {interactions.length === 0 ? (
            <Card padding="lg" className="text-center py-8">
              <p className="text-xs text-muted-foreground">
                No meetings or interactions logged for this customer yet.
              </p>
            </Card>
          ) : (
            <div className="space-y-3">
              {interactions.map((i) => (
                <Card key={i.id} padding="md" className="space-y-3 border-border/70 bg-card/70 hover:border-primary/40 transition-colors">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                    <div>
                      <Link
                        href={`/interactions/${i.id}`}
                        className="text-base font-bold text-foreground hover:text-primary transition-colors"
                      >
                        {i.title}
                      </Link>
                      <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {formatDate(i.meeting_date)}
                        </span>
                        <span>&bull;</span>
                        <span className="uppercase">{i.type}</span>
                        {i.duration_minutes && <span>&bull; {i.duration_minutes} min</span>}
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      {i.ai_insight && <Badge sentiment={i.ai_insight.sentiment} size="sm" />}
                      <Link href={`/interactions/${i.id}`}>
                        <Button variant="ghost" size="sm" className="text-xs">
                          View Details
                        </Button>
                      </Link>
                    </div>
                  </div>

                  <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
                    {i.notes}
                  </p>

                  {i.ai_insight && (
                    <div className="rounded-lg border border-indigo-500/20 bg-indigo-500/5 p-3 text-xs text-foreground flex items-start gap-2">
                      <Sparkles className="h-4 w-4 text-indigo-400 shrink-0 mt-0.5" />
                      <div>
                        <strong className="text-indigo-400">AI Summary:</strong>{' '}
                        <span className="text-slate-300">{i.ai_insight.summary}</span>
                      </div>
                    </div>
                  )}
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
