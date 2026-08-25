/**
 * AI Insight Intelligence View Component.
 *
 * Displays executive AI summary, sentiment badge, extracted action items, identified risks,
 * and regenerate inference trigger.
 */

import React from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { AIInsightViewProps } from '@/types';
import {
  Sparkles,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Cpu,
} from 'lucide-react';

/**
 * Visual display component presenting LLM-extracted summary, risks, and action items.
 */
export const AIInsightView: React.FC<AIInsightViewProps> = ({
  insight,
  onRegenerate,
  isGenerating = false,
}) => {
  if (!insight) {
    return (
      <Card className="border-dashed border-indigo-500/30 bg-indigo-500/5 text-center p-8">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-indigo-500/10 text-indigo-400 mb-3">
          <Sparkles className="h-6 w-6" />
        </div>
        <h4 className="text-base font-bold text-foreground">
          No AI Insight Generated Yet
        </h4>
        <p className="mx-auto mt-1 max-w-md text-xs text-muted-foreground">
          Run the AI intelligence pipeline on this meeting note to extract executive summary, sentiment, action items, and account risks.
        </p>

        <div className="mt-4">
          <Button
            variant="primary"
            size="sm"
            onClick={onRegenerate}
            isLoading={isGenerating}
            leftIcon={<Sparkles className="h-4 w-4" />}
          >
            Generate AI Insights
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <Card className="border-indigo-500/30 bg-card/80 shadow-glow relative overflow-hidden">
      <div className="absolute top-0 left-0 h-1 w-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500" />

      {/* Header */}
      <CardHeader className="flex flex-row items-start justify-between pb-3">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-indigo-400" />
            <CardTitle>AI Intelligence Analysis</CardTitle>
            <Badge sentiment={insight.sentiment} />
          </div>
          <CardDescription>
            Autonomous NLP summary & extracted telemetry
          </CardDescription>
        </div>

        <Button
          variant="secondary"
          size="sm"
          onClick={onRegenerate}
          isLoading={isGenerating}
          leftIcon={<RefreshCw className="h-3.5 w-3.5" />}
          className="text-xs"
        >
          Regenerate
        </Button>
      </CardHeader>

      <CardContent className="space-y-5 pt-2">
        {/* Executive Summary */}
        <div className="rounded-lg border border-border/80 bg-secondary/30 p-4">
          <div className="flex items-center gap-2 mb-2">
            <FileText className="h-4 w-4 text-indigo-400" />
            <h5 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
              Executive Business Summary
            </h5>
          </div>
          <p className="text-sm font-medium leading-relaxed text-foreground">
            {insight.summary}
          </p>
        </div>

        {/* Action items & Risks columns */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Action Items */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              <h5 className="text-xs font-bold uppercase tracking-wider text-emerald-300">
                Extracted Action Items ({insight.action_items?.length || 0})
              </h5>
            </div>

            {(!insight.action_items || insight.action_items.length === 0) ? (
              <p className="text-xs italic text-muted-foreground py-2">
                No immediate action items identified.
              </p>
            ) : (
              <ul className="space-y-1.5">
                {insight.action_items.map((item, idx) => (
                  <li
                    key={idx}
                    className="flex items-start gap-2 rounded-lg border border-border/60 bg-secondary/30 p-2.5 text-xs text-foreground leading-relaxed"
                  >
                    <span className="font-bold text-emerald-400">&bull;</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Risks */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-rose-400" />
              <h5 className="text-xs font-bold uppercase tracking-wider text-rose-300">
                Identified Account Risks ({insight.risks?.length || 0})
              </h5>
            </div>

            {(!insight.risks || insight.risks.length === 0) ? (
              <p className="text-xs italic text-muted-foreground py-2">
                No retention or friction risks identified.
              </p>
            ) : (
              <ul className="space-y-1.5">
                {insight.risks.map((risk, idx) => (
                  <li
                    key={idx}
                    className="flex items-start gap-2 rounded-lg border border-rose-500/20 bg-rose-500/10 p-2.5 text-xs text-rose-300 leading-relaxed"
                  >
                    <span className="font-bold text-rose-400">&bull;</span>
                    <span>{risk}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Footer info */}
        <div className="flex items-center justify-between border-t border-border/60 pt-3 text-[11px] text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <Cpu className="h-3.5 w-3.5" />
            <span>Model: {insight.model}</span>
          </div>
          <div>
            Status:{' '}
            <span
              className={`font-semibold ${
                insight.generation_status === 'SUCCESS'
                  ? 'text-emerald-400'
                  : 'text-amber-400'
              }`}
            >
              {insight.generation_status}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

