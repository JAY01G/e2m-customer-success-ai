import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { AIInsightView } from '@/components/insights/AIInsightView';
import { AIInsight } from '@/types';

const mockInsight: AIInsight = {
  id: 'insight-1',
  interaction_id: 'interaction-1',
  summary: 'Client agreed to 3-year enterprise contract renewal with 50 additional seats.',
  sentiment: 'Positive',
  action_items: ['Send revised contract copy to procurement', 'Schedule onboarding webinar'],
  risks: ['Customer requested custom export format before rollout'],
  model: 'gpt-4o-mini',
  generation_status: 'SUCCESS',
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

describe('AIInsightView Component', () => {
  it('renders ungenerated state when no insight exists', () => {
    const handleRegenerate = vi.fn();
    render(<AIInsightView onRegenerate={handleRegenerate} />);

    expect(screen.getByText('No AI Insight Generated Yet')).toBeInTheDocument();
    const generateBtn = screen.getByRole('button', { name: /Generate AI Insights/i });
    fireEvent.click(generateBtn);
    expect(handleRegenerate).toHaveBeenCalledTimes(1);
  });

  it('renders executive summary, positive sentiment badge, action items and risks', () => {
    const handleRegenerate = vi.fn();
    render(<AIInsightView insight={mockInsight} onRegenerate={handleRegenerate} />);

    expect(screen.getByText('AI Intelligence Analysis')).toBeInTheDocument();
    expect(screen.getByText(/3-year enterprise contract renewal/i)).toBeInTheDocument();
    expect(screen.getByText(/Positive/i)).toBeInTheDocument();
    expect(screen.getByText('Send revised contract copy to procurement')).toBeInTheDocument();
    expect(screen.getByText('Customer requested custom export format before rollout')).toBeInTheDocument();
    expect(screen.getByText(/Model: gpt-4o-mini/i)).toBeInTheDocument();
  });

  it('calls onRegenerate when regenerate button is clicked', () => {
    const handleRegenerate = vi.fn();
    render(<AIInsightView insight={mockInsight} onRegenerate={handleRegenerate} />);

    const regenBtn = screen.getByRole('button', { name: /Regenerate/i });
    fireEvent.click(regenBtn);
    expect(handleRegenerate).toHaveBeenCalledTimes(1);
  });
});
