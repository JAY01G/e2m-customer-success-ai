/**
 * Recent Customer Interactions Feed Widget Component.
 *
 * Displays a chronological list of recent meetings with quick sentiment indicators.
 */

import React from 'react';
import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { RecentInteractionsWidgetProps } from '@/types';
import { formatDate } from '@/lib/helpers';
import { MessageSquare, Calendar, ArrowRight } from 'lucide-react';

/**
 * Executive dashboard feed widget of recently logged customer interactions.
 */
export const RecentInteractionsWidget: React.FC<RecentInteractionsWidgetProps> = ({
  interactions,
}) => {
  return (
    <Card className="flex flex-col justify-between">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5 text-indigo-400" />
            <CardTitle>Recent Customer Meetings</CardTitle>
          </div>
          <CardDescription>Latest interaction notes & AI sentiment signals</CardDescription>
        </div>
        <Link
          href="/interactions"
          className="text-xs font-semibold text-primary hover:underline inline-flex items-center gap-1"
        >
          View All <ArrowRight className="h-3.5 w-3.5" />
        </Link>
      </CardHeader>

      <CardContent className="pt-4">
        {interactions.length === 0 ? (
          <p className="text-center text-xs text-muted-foreground py-6">
            No recent interactions logged yet.
          </p>
        ) : (
          <div className="space-y-3">
            {interactions.map((i) => (
              <Link
                key={i.id}
                href={`/interactions/${i.id}`}
                className="block rounded-lg border border-border/60 bg-secondary/40 p-3 hover:border-primary/40 hover:bg-secondary/70 transition-all duration-200"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="space-y-1">
                    <span className="text-sm font-bold text-foreground line-clamp-1">
                      {i.title}
                    </span>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <span className="font-medium text-slate-300">
                        {i.user ? i.user.name : i.type}
                      </span>
                      <span>&bull;</span>
                      <span className="inline-flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {formatDate(i.meeting_date)}
                      </span>
                    </div>
                  </div>

                  {i.ai_insight && <Badge sentiment={i.ai_insight.sentiment} size="sm" />}
                </div>
              </Link>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

