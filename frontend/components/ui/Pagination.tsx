import React from 'react';
import { cn } from '@/lib/utils';
import { PaginationProps } from '@/types';
import { getPaginationPages } from '@/lib/helpers';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from './Button';

export const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
  totalItems,
  pageSize,
  className,
}) => {
  if (totalPages <= 1 && !totalItems) return null;

  const startItem = (currentPage - 1) * (pageSize || 10) + 1;
  const endItem = Math.min(currentPage * (pageSize || 10), totalItems || 0);
  const pages = getPaginationPages(currentPage, totalPages);

  return (
    <div
      className={cn(
        'flex flex-col sm:flex-row items-center justify-between gap-4 py-4 px-2',
        className
      )}
    >
      {totalItems !== undefined && (
        <div className="text-xs text-muted-foreground">
          Showing <span className="font-semibold text-foreground">{startItem}</span> to{' '}
          <span className="font-semibold text-foreground">{endItem}</span> of{' '}
          <span className="font-semibold text-foreground">{totalItems}</span> results
        </div>
      )}

      <div className="flex items-center gap-1.5">
        <Button
          variant="secondary"
          size="sm"
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage <= 1}
          className="h-8 px-2.5"
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>

        {pages.map((p, idx) =>
          typeof p === 'number' ? (
            <Button
              key={idx}
              variant={currentPage === p ? 'default' : 'secondary'}
              size="sm"
              onClick={() => onPageChange(p)}
              className={cn(
                'h-8 w-8 p-0 text-xs',
                currentPage === p
                  ? 'bg-primary text-primary-foreground font-bold shadow-glow'
                  : 'text-muted-foreground hover:text-foreground'
              )}
            >
              {p}
            </Button>
          ) : (
            <span key={idx} className="px-2 text-xs text-muted-foreground">
              ...
            </span>
          )
        )}

        <Button
          variant="secondary"
          size="sm"
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage >= totalPages}
          className="h-8 px-2.5"
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
};
