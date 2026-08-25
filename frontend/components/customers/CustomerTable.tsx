/**
 * Customer Accounts Data Table.
 *
 * Renders tabular display of customer accounts with health badges, owner info, and action triggers.
 */

import React from 'react';
import Link from 'next/link';
import { CustomerTableProps } from '@/types';
import { getHealthScoreCategory } from '@/lib/helpers';
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
import { Eye, Edit, Trash2, Mail, Building2 } from 'lucide-react';

/**
 * Data table rendering customer accounts list with role-based action triggers.
 */
export const CustomerTable: React.FC<CustomerTableProps> = ({
  customers,
  onDelete,
}) => {
  const { user } = useAppSelector((state) => state.auth);
  const isAdmin = user?.role === 'ADMIN';
  const isCsmOrAdmin = user?.role === 'ADMIN' || user?.role === 'CUSTOMER_SUCCESS_MANAGER';

  if (customers.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-xl border border-border/80 bg-card/60 p-12 text-center">
        <Building2 className="h-10 w-10 text-muted-foreground/60 mb-3" />
        <h3 className="text-base font-bold text-foreground">No Accounts Found</h3>
        <p className="text-xs text-muted-foreground mt-1 max-w-sm">
          No customer accounts found matching your criteria. Try adjusting your search query or filters.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-border/80 bg-card/60 shadow-card backdrop-blur-md overflow-hidden">
      <Table>
        <TableHeader className="bg-secondary/40">
          <TableRow>
            <TableHead>Company & Contact</TableHead>
            <TableHead>Industry</TableHead>
            <TableHead>Lifecycle Status</TableHead>
            <TableHead>Health Score</TableHead>
            <TableHead>CSM Owner</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {customers.map((c) => {
            const scoreInfo = getHealthScoreCategory(c.health_score);

            return (
              <TableRow key={c.id} className="hover:bg-muted/30">
                <TableCell>
                  <div className="space-y-0.5">
                    <Link
                      href={`/customers/${c.id}`}
                      className="font-bold text-foreground hover:text-primary transition-colors text-sm"
                    >
                      {c.company_name}
                    </Link>
                    <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                      <span>{c.name}</span>
                      <span>&bull;</span>
                      <span className="flex items-center gap-1">
                        <Mail className="h-3 w-3" /> {c.email}
                      </span>
                    </div>
                  </div>
                </TableCell>

                <TableCell className="text-xs text-muted-foreground">
                  {c.industry || '—'}
                </TableCell>

                <TableCell>
                  <Badge status={c.status} size="sm" />
                </TableCell>

                <TableCell>
                  <span
                    className={`inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-bold ${scoreInfo.badgeClass}`}
                  >
                    {c.health_score}
                  </span>
                </TableCell>

                <TableCell className="text-xs text-muted-foreground">
                  {c.owner ? (
                    <span className="font-medium text-slate-300">{c.owner.name}</span>
                  ) : (
                    <span className="italic text-muted-foreground/60">Unassigned</span>
                  )}
                </TableCell>

                <TableCell className="text-right">
                  <div className="flex items-center justify-end gap-1">
                    <Link href={`/customers/${c.id}`}>
                      <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-muted-foreground hover:text-foreground">
                        <Eye className="h-4 w-4" />
                      </Button>
                    </Link>

                    {isCsmOrAdmin && (
                      <Link href={`/customers/${c.id}/edit`}>
                        <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-muted-foreground hover:text-foreground">
                          <Edit className="h-4 w-4" />
                        </Button>
                      </Link>
                    )}

                    {isAdmin && onDelete && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onDelete(c.id, c.company_name)}
                        className="h-8 w-8 p-0 text-muted-foreground hover:text-destructive"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
};

