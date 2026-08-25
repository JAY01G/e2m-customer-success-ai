import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MetricCard } from '@/components/dashboard/MetricCard';
import { HealthScoreChart } from '@/components/dashboard/HealthScoreChart';
import { SentimentDistributionChart } from '@/components/dashboard/SentimentDistributionChart';
import { Activity } from 'lucide-react';

describe('Dashboard Components', () => {
  it('renders MetricCard with title and value', () => {
    render(
      <MetricCard
        title="Active Accounts"
        value={42}
        subtitle="Adopting users"
        icon={<Activity size={20} />}
      />
    );

    expect(screen.getByText(/Active Accounts/i)).toBeInTheDocument();
    expect(screen.getByText('42')).toBeInTheDocument();
    expect(screen.getByText('Adopting users')).toBeInTheDocument();
  });

  it('renders HealthScoreChart with distribution categories', () => {
    const distribution = {
      healthy: 15,
      moderate: 8,
      critical: 3,
    };

    render(<HealthScoreChart distribution={distribution} averageScore={78.5} />);

    expect(screen.getByText('Customer Health Breakdown')).toBeInTheDocument();
    expect(screen.getByText(/78.5\/100/i)).toBeInTheDocument();
    expect(screen.getByText(/HEALTHY/i)).toBeInTheDocument();
    expect(screen.getByText(/MODERATE/i)).toBeInTheDocument();
    expect(screen.getByText(/CRITICAL/i)).toBeInTheDocument();
  });

  it('renders SentimentDistributionChart with percentages', () => {
    const distribution = {
      positive: 10,
      neutral: 4,
      negative: 2,
      positive_percentage: 62.5,
      neutral_percentage: 25.0,
      negative_percentage: 12.5,
    };

    render(<SentimentDistributionChart distribution={distribution} />);

    expect(screen.getByText('AI Meeting Sentiment Analysis')).toBeInTheDocument();
    expect(screen.getByText(/Positive Sentiment/i)).toBeInTheDocument();
    expect(screen.getByText(/10 \(62.5%\)/i)).toBeInTheDocument();
    expect(screen.getByText(/4 \(25%\)/i)).toBeInTheDocument();
  });
});
