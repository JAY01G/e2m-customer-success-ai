/**
 * Customer Interactions Data Table.
 *
 * Renders tabular logs of meeting discussions, touchpoint types, duration, and AI sentiment badges.
 */

import React from 'react';
import Link from 'next/link';
import { InteractionTableProps } from '@/types';
import { formatDate } from '@/lib/helpers';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from '@/components/ui/Table';
import { useAppSelector } from '@/store/hooks';
import { Eye, Trash2, Calendar, Clock, MessageSquare } from 'lucide-react';

/**
 * Data table rendering customer touchpoints list with sentiment tags.
 */
export const InteractionTable: React.FC<InteractionTableProps> = ({
  interactions,
  onDelete,
}) => {
  const { user } = useAppSelector((state) => state.auth);
  const isAdmin = user?.role === 'ADMIN';

  if (interactions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-xl border border-border/80 bg-card/60 p-12 text-center">
        <MessageSquare className="h-10 w-10 text-muted-foreground/60 mb-3" />
        <h3 className="text-base font-bold text-foreground">No Interactions Found</h3>
        <p className="text-xs text-muted-foreground mt-1 max-w-sm">
          No meeting logs or call notes match your filters.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-border/80 bg-card/60 shadow-card backdrop-blur-md overflow-hidden">
      <Table>
        <TableHeader className="bg-secondary/40">
          <TableRow>
            <TableHead>Meeting Subject</TableHead>
            <TableHead>Customer</TableHead>
            <TableHead>Type</TableHead>
            <TableHead>Date & Duration</TableHead>
            <TableHead>AI Sentiment</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {interactions.map((i) => (
            <TableRow key={i.id} className="hover:bg-muted/30">
              <TableCell>
                <div className="space-y-0.5">
                  <Link
                    href={`/interactions/${i.id}`}
                    className="font-bold text-foreground hover:text-primary transition-colors text-sm line-clamp-1"
                  >
                    {i.title}
                  </Link>
                  <p className="text-xs text-muted-foreground line-clamp-1">
                    {i.notes.slice(0, 80)}...
                  </p>
                </div>
              </TableCell>

              <TableCell>
                {i.customer_id ? (
                  <Link
                    href={`/customers/${i.customer_id}`}
                    className="text-xs font-semibold text-slate-200 hover:text-primary transition-colors"
                  >
                    View Account
                  </Link>
                ) : (
                  <span className="text-xs text-muted-foreground">—</span>
                )}
              </TableCell>

              <TableCell>
                <span className="rounded-md bg-secondary px-2.5 py-1 text-xs font-bold uppercase tracking-wider text-muted-foreground">
                  {i.type}
                </span>
              </TableCell>

              <TableCell>
                <div className="space-y-0.5 text-xs text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    {formatDate(i.meeting_date)}
                  </div>
                  {i.duration_minutes && (
                    <div className="flex items-center gap-1 text-[11px] text-muted-foreground/80">
                      <Clock className="h-3 w-3" />
                      {i.duration_minutes} mins
                    </div>
                  )}
                </div>
              </TableCell>

              <TableCell>
                {i.ai_insight ? (
                  <Badge sentiment={i.ai_insight.sentiment} size="sm" />
                ) : (
                  <span className="text-xs text-muted-foreground/60 italic">Pending</span>
                )}
              </TableCell>

              <TableCell className="text-right">
                <div className="flex items-center justify-end gap-1">
                  <Link href={`/interactions/${i.id}`}>
                    <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-muted-foreground hover:text-foreground">
                      <Eye className="h-4 w-4" />
                    </Button>
                  </Link>

                  {isAdmin && onDelete && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onDelete(i.id, i.title)}
                      className="h-8 w-8 p-0 text-muted-foreground hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

