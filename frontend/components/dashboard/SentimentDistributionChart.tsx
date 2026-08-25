/**
 * AI Sentiment Distribution Donut Chart Component.
 *
 * Renders Recharts pie/donut breakdown of positive, neutral, and negative sentiment across logged customer interactions.
 */

import React from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { SentimentDistributionChartProps } from '@/types';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
} from 'recharts';
import { Sparkles } from 'lucide-react';

/**
 * Donut chart component visualizing meeting sentiment distribution percentages.
 */
export const SentimentDistributionChart: React.FC<SentimentDistributionChartProps> = ({
  distribution,
}) => {
  const chartData = [
    {
      name: 'Positive',
      value: distribution.positive,
      percentage: distribution.positive_percentage,
      color: '#10b981',
    },
    {
      name: 'Neutral',
      value: distribution.neutral,
      percentage: distribution.neutral_percentage,
      color: '#6366f1',
    },
    {
      name: 'Negative',
      value: distribution.negative,
      percentage: distribution.negative_percentage,
      color: '#f43f5e',
    },
  ];

  const total = distribution.positive + distribution.neutral + distribution.negative;

  return (
    <Card className="flex flex-col justify-between">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-indigo-400" />
            <CardTitle>AI Meeting Sentiment Analysis</CardTitle>
          </div>
          <CardDescription>Automated sentiment classification on logged interactions</CardDescription>
        </div>
        <div className="rounded-full border border-indigo-500/30 bg-indigo-500/10 px-3 py-1 text-xs font-bold text-indigo-400">
          {total} Analyzed
        </div>
      </CardHeader>

      <CardContent className="pt-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
          {/* Pie Chart */}
          <div className="h-52 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="rounded-lg border border-border bg-slate-900/95 p-2.5 shadow-xl">
                          <div className="flex items-center gap-2">
                            <span
                              className="h-2.5 w-2.5 rounded-full"
                              style={{ backgroundColor: data.color }}
                            />
                            <span className="text-xs font-bold text-slate-100">{data.name}</span>
                          </div>
                          <p className="mt-1 text-xs text-slate-400">
                            {data.value} meetings ({data.percentage}%)
                          </p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Breakdown List */}
          <div className="space-y-3">
            <div className="flex items-center justify-between rounded-lg bg-emerald-500/10 p-3 border border-emerald-500/20">
              <div className="flex items-center gap-2.5">
                <span className="h-3 w-3 rounded-full bg-emerald-400" />
                <span className="text-xs font-semibold text-emerald-300">Positive Sentiment</span>
              </div>
              <span className="text-sm font-bold text-emerald-400">
                {distribution.positive} ({distribution.positive_percentage}%)
              </span>
            </div>

            <div className="flex items-center justify-between rounded-lg bg-indigo-500/10 p-3 border border-indigo-500/20">
              <div className="flex items-center gap-2.5">
                <span className="h-3 w-3 rounded-full bg-indigo-400" />
                <span className="text-xs font-semibold text-indigo-300">Neutral Sentiment</span>
              </div>
              <span className="text-sm font-bold text-indigo-400">
                {distribution.neutral} ({distribution.neutral_percentage}%)
              </span>
            </div>

            <div className="flex items-center justify-between rounded-lg bg-rose-500/10 p-3 border border-rose-500/20">
              <div className="flex items-center gap-2.5">
                <span className="h-3 w-3 rounded-full bg-rose-400" />
                <span className="text-xs font-semibold text-rose-300">Negative Sentiment</span>
              </div>
              <span className="text-sm font-bold text-rose-400">
                {distribution.negative} ({distribution.negative_percentage}%)
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

