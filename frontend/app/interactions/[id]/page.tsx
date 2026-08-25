'use client';

import React, { useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import {
  fetchInteractionById,
  generateInteractionInsight,
} from '@/store/slices/interactionSlice';
import { useToast } from '@/components/providers/ToastProvider';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Spinner } from '@/components/ui/Spinner';
import { AIInsightView } from '@/components/insights/AIInsightView';
import { formatFullDate } from '@/lib/helpers';
import { ArrowLeft, Calendar, Clock, User, Building, FileText } from 'lucide-react';

export default function InteractionDetailPage() {
  const { id } = useParams() as { id: string };
  const dispatch = useAppDispatch();
  const { toast } = useToast();
  const {
    selectedInteraction: interaction,
    isLoading,
    isGeneratingInsight,
  } = useAppSelector((state) => state.interactions);

  useEffect(() => {
    if (id) {
      dispatch(fetchInteractionById(id));
    }
  }, [id, dispatch]);

  const handleRegenerateInsight = async () => {
    if (id) {
      toast.info('Generating AI Insights', 'Synthesizing meeting notes, sentiment, and action items...');
      try {
        await dispatch(
          generateInteractionInsight({ interactionId: id, regenerate: true })
        ).unwrap();
        toast.success('AI Insights Generated', 'Meeting intelligence updated successfully.');
      } catch (err: any) {
        const msg = err.message || 'Failed to generate AI insights';
        toast.error('AI Generation Failed', msg);
      }
    }
  };

  if (isLoading || !interaction) {
    return (
      <AppLayout>
        <div className="py-16">
          <Spinner size={36} label="Loading interaction details..." />
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="max-w-5xl mx-auto space-y-6">
        <Link
          href="/interactions"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="h-4 w-4" /> Back to Interactions
        </Link>

        {/* Meeting Header */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="rounded-md bg-secondary px-2.5 py-1 text-xs font-bold uppercase tracking-wider text-muted-foreground">
              {interaction.type}
            </span>
            {interaction.ai_insight && (
              <Badge sentiment={interaction.ai_insight.sentiment} />
            )}
          </div>

          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground">
            {interaction.title}
          </h1>

          <div className="flex flex-wrap items-center gap-4 text-xs text-muted-foreground pt-1">
            <span className="flex items-center gap-1.5">
              <Calendar className="h-3.5 w-3.5" />
              {formatFullDate(interaction.meeting_date)}
            </span>

            {interaction.duration_minutes && (
              <span className="flex items-center gap-1.5">
                <Clock className="h-3.5 w-3.5" />
                {interaction.duration_minutes} Minutes
              </span>
            )}

            {interaction.user && (
              <span className="flex items-center gap-1.5">
                <User className="h-3.5 w-3.5" />
                Recorded by: <strong className="text-slate-300">{interaction.user.name}</strong>
              </span>
            )}

            {interaction.customer_id && (
              <Link
                href={`/customers/${interaction.customer_id}`}
                className="flex items-center gap-1.5 text-primary font-semibold hover:underline"
              >
                <Building className="h-3.5 w-3.5" />
                View Customer Profile
              </Link>
            )}
          </div>
        </div>

        {/* AI Insight Card */}
        <div>
          <AIInsightView
            insight={interaction.ai_insight}
            onRegenerate={handleRegenerateInsight}
            isGenerating={isGeneratingInsight}
          />
        </div>

        {/* Raw Meeting Notes */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-muted-foreground" />
            <h3 className="text-sm font-bold uppercase tracking-wider text-muted-foreground">
              Raw Meeting Notes & Discussion Transcript
            </h3>
          </div>

          <Card padding="lg" className="border-border/80 bg-card/80">
            <p className="text-sm text-foreground leading-relaxed whitespace-pre-wrap">
              {interaction.notes}
            </p>
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}
