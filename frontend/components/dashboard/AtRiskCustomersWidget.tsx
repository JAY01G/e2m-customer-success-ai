/**
 * At-Risk Customers List Widget Component.
 *
 * Displays accounts flagged with high churn risk or low health score requiring CSM intervention.
 */

import React from 'react';
import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { AtRiskCustomersWidgetProps } from '@/types';
import { getHealthScoreCategory } from '@/lib/helpers';
import { AlertTriangle, ArrowRight } from 'lucide-react';

/**
 * Executive dashboard widget presenting at-risk customer accounts.
 */
export const AtRiskCustomersWidget: React.FC<AtRiskCustomersWidgetProps> = ({
  customers,
}) => {
  return (
    <Card className="flex flex-col justify-between">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-amber-400" />
            <CardTitle>At-Risk Accounts</CardTitle>
          </div>
          <CardDescription>Accounts requiring immediate CSM retention actions</CardDescription>
        </div>
        <Link
          href="/customers?status=AT_RISK"
          className="text-xs font-semibold text-primary hover:underline inline-flex items-center gap-1"
        >
          View All <ArrowRight className="h-3.5 w-3.5" />
        </Link>
      </CardHeader>

      <CardContent className="pt-4">
        {customers.length === 0 ? (
          <p className="text-center text-xs text-muted-foreground py-6">
            🎉 Great job! No accounts are currently flagged as at-risk.
          </p>
        ) : (
          <div className="space-y-3">
            {customers.map((c) => {
              const scoreInfo = getHealthScoreCategory(c.health_score);

              return (
                <Link
                  key={c.id}
                  href={`/customers/${c.id}`}
                  className="flex items-center justify-between rounded-lg border border-border/60 bg-secondary/40 p-3 hover:border-amber-500/40 hover:bg-secondary/70 transition-all duration-200"
                >
                  <div className="space-y-1">
                    <span className="text-sm font-bold text-foreground line-clamp-1">
                      {c.company_name}
                    </span>
                    <div className="text-xs text-muted-foreground">
                      Contact: <span className="text-slate-300">{c.name}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <Badge status={c.status} size="sm" />
                    <div
                      className={`flex h-8 w-8 items-center justify-center rounded-full border text-xs font-extrabold ${scoreInfo.badgeClass}`}
                    >
                      {c.health_score}
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

