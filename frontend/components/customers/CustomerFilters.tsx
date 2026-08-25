/**
 * Customer Search and Filter Bar Component.
 *
 * Provides reactive form controls for searching by contact/company, filtering by status and health score tiers.
 */

import React, { useState } from 'react';
import { CustomerFiltersProps, CustomerQueryParams, CustomerStatus } from '@/types';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Button } from '@/components/ui/Button';
import { Search, Filter, RotateCcw } from 'lucide-react';

/**
 * Filter bar component for querying and searching customer accounts.
 */
export const CustomerFilters: React.FC<CustomerFiltersProps> = ({
  onFilterChange,
  initialFilters = {},
}) => {
  const [search, setSearch] = useState(initialFilters.search || '');
  const [status, setStatus] = useState<string>(initialFilters.status || '');
  const [minHealthScore, setMinHealthScore] = useState<string>(
    initialFilters.min_health_score !== undefined
      ? String(initialFilters.min_health_score)
      : ''
  );

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    applyFilters();
  };

  const applyFilters = () => {
    const filters: CustomerQueryParams = {};
    if (search.trim()) filters.search = search.trim();
    if (status) filters.status = status as CustomerStatus;
    if (minHealthScore !== '') {
      const score = parseInt(minHealthScore, 10);
      if (!isNaN(score)) filters.min_health_score = score;
    }
    onFilterChange(filters);
  };

  const handleReset = () => {
    setSearch('');
    setStatus('');
    setMinHealthScore('');
    onFilterChange({});
  };

  return (
    <div className="mb-6 rounded-xl border border-border/70 bg-card/60 p-4 shadow-card backdrop-blur-md">
      <form
        onSubmit={handleSearchSubmit}
        className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4 items-end"
      >
        <Input
          placeholder="Search by company or contact..."
          value={search}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearch(e.target.value)}
          leftIcon={<Search className="h-4 w-4" />}
        />

        <Select
          value={status}
          onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setStatus(e.target.value)}
          options={[
            { value: '', label: 'All Lifecycle Statuses' },
            { value: 'ACTIVE', label: 'Active Accounts' },
            { value: 'AT_RISK', label: 'At-Risk Accounts' },
            { value: 'PROSPECT', label: 'Prospect Accounts' },
            { value: 'CHURNED', label: 'Churned Accounts' },
          ]}
        />

        <Select
          value={minHealthScore}
          onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setMinHealthScore(e.target.value)}
          options={[
            { value: '', label: 'All Health Scores' },
            { value: '80', label: 'Healthy (Score >= 80)' },
            { value: '50', label: 'Moderate+ (Score >= 50)' },
            { value: '0', label: 'All Registered (Score >= 0)' },
          ]}
        />

        <div className="flex items-center gap-2">
          <Button
            type="submit"
            variant="primary"
            className="flex-1"
            leftIcon={<Filter className="h-3.5 w-3.5" />}
          >
            Apply Filters
          </Button>

          {(search || status || minHealthScore) && (
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

