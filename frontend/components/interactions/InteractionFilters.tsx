/**
 * Interaction Search and Filter Controls Component.
 *
 * Provides reactive query controls for title/notes search and interaction type filtering.
 */

import React, { useState } from 'react';
import { InteractionFiltersProps, InteractionQueryParams, InteractionType } from '@/types';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Button } from '@/components/ui/Button';
import { Search, Filter, RotateCcw } from 'lucide-react';

/**
 * Filter bar component for searching and categorizing meeting interactions.
 */
export const InteractionFilters: React.FC<InteractionFiltersProps> = ({
  onFilterChange,
  initialFilters = {},
}) => {
  const [search, setSearch] = useState(initialFilters.search || '');
  const [type, setType] = useState<string>(initialFilters.type || '');

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    applyFilters();
  };

  const applyFilters = () => {
    const filters: InteractionQueryParams = {};
    if (search.trim()) filters.search = search.trim();
    if (type) filters.type = type as InteractionType;
    onFilterChange(filters);
  };

  const handleReset = () => {
    setSearch('');
    setType('');
    onFilterChange({});
  };

  return (
    <div className="mb-6 rounded-xl border border-border/70 bg-card/60 p-4 shadow-card backdrop-blur-md">
      <form
        onSubmit={handleSearchSubmit}
        className="grid grid-cols-1 gap-3 sm:grid-cols-3 items-end"
      >
        <Input
          placeholder="Search by title or notes..."
          value={search}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearch(e.target.value)}
          leftIcon={<Search className="h-4 w-4" />}
        />

        <Select
          value={type}
          onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setType(e.target.value)}
          options={[
            { value: '', label: 'All Interaction Types' },
            { value: 'MEETING', label: 'Meetings' },
            { value: 'CALL', label: 'Phone Calls' },
            { value: 'EMAIL', label: 'Email Threads' },
            { value: 'DEMO', label: 'Product Demos' },
            { value: 'OTHER', label: 'Other Activities' },
          ]}
        />

        <div className="flex items-center gap-2">
          <Button
            type="submit"
            variant="primary"
            className="flex-1"
            leftIcon={<Filter className="h-3.5 w-3.5" />}
          >
            Filter Logs
          </Button>

          {(search || type) && (
            <Button
              type="button"
              variant="secondary"
              onClick={handleReset}
              className="px-3"
              leftIcon={<RotateCcw className="h-3.5 w-3.5" />}
            >
              Reset
            </Button>
          )}
        </div>
      </form>
    </div>
  );
};

