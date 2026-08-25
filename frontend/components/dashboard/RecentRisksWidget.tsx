/**
 * Recent Customer Risks Feed Widget Component.
 *
 * Displays AI-detected risk factors, blockers, and churn risks across accounts.
 */

import React from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { RecentRisksWidgetProps } from '@/types';
import { ShieldAlert } from 'lucide-react';

/**
 * Executive dashboard feed widget displaying flagged friction risks.
 */
export const RecentRisksWidget: React.FC<RecentRisksWidgetProps> = ({ risks }) => {
  return (
    <Card className="flex flex-col justify-between">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <ShieldAlert className="h-5 w-5 text-rose-400" />
            <CardTitle>Identified Account Risks</CardTitle>
          </div>
          <CardDescription>AI-extracted customer friction points & blockers</CardDescription>
        </div>
        <div className="rounded-full border border-rose-500/30 bg-rose-500/10 px-2.5 py-0.5 text-xs font-bold text-rose-400">
          {risks.length} Detected
        </div>
      </CardHeader>

      <CardContent className="pt-4">
        {risks.length === 0 ? (
          <p className="text-center text-xs text-muted-foreground py-6">
            No critical risks flagged in recent interactions.
          </p>
        ) : (
          <ul className="space-y-2.5">
            {risks.map((item, index) => (
              <li
                key={index}
                className="flex items-start gap-2.5 rounded-lg border border-rose-500/20 bg-rose-500/5 p-3 text-xs leading-relaxed text-rose-300"
              >
                <span className="font-extrabold text-rose-400">&bull;</span>
                <div>
                  <span className="font-bold text-slate-200">{item.company_name}: </span>
                  <span>{item.risk}</span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
};

