/**
 * Customer Health Score Bar Chart Component.
 *
 * Visualizes customer distribution across Healthy, Moderate, and Critical health tiers using Recharts.
 */

import React from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { HealthScoreChartProps } from '@/types';
import { getHealthScoreCategory } from '@/lib/helpers';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from 'recharts';
import { HeartPulse } from 'lucide-react';

/**
 * Interactive bar chart component rendering portfolio health distributions.
 */
export const HealthScoreChart: React.FC<HealthScoreChartProps> = ({
  distribution,
  averageScore,
}) => {
  const chartData = [
    {
      name: 'Healthy',
      range: '80-100',
      count: distribution.healthy,
      fill: '#10b981',
    },
    {
      name: 'Moderate',
      range: '50-79',
      count: distribution.moderate,
      fill: '#f59e0b',
    },
    {
      name: 'Critical',
      range: '0-49',
      count: distribution.critical,
      fill: '#f43f5e',
    },
  ];

  const scoreInfo = getHealthScoreCategory(averageScore);

  return (
    <Card className="flex flex-col justify-between">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <HeartPulse className="h-5 w-5 text-indigo-400" />
            <CardTitle>Customer Health Breakdown</CardTitle>
          </div>
          <CardDescription>Portfolio account health score distribution</CardDescription>
        </div>
        <div
          className={`flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-bold ${scoreInfo.badgeClass}`}
        >
          <span>Avg:</span>
          <span>{averageScore}/100</span>
        </div>
      </CardHeader>

      <CardContent className="pt-4">
        <div className="h-56 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <XAxis
                dataKey="name"
                stroke="#64748b"
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                stroke="#64748b"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                allowDecimals={false}
              />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <div className="rounded-lg border border-border bg-slate-900/95 p-2.5 shadow-xl">
                        <div className="flex items-center gap-2">
                          <span
                            className="h-2.5 w-2.5 rounded-full"
                            style={{ backgroundColor: data.fill }}
                          />
                          <span className="text-xs font-bold text-slate-100">{data.name}</span>
                        </div>
                        <p className="mt-1 text-xs text-slate-400">
                          Score: {data.range} &bull; <strong className="text-slate-200">{data.count} accounts</strong>
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Legend Row */}
        <div className="mt-4 grid grid-cols-3 gap-2 border-t border-border/60 pt-4 text-center">
          <div className="rounded-lg bg-emerald-500/5 p-2 border border-emerald-500/10">
            <span className="text-[11px] font-semibold text-emerald-400">HEALTHY (80-100)</span>
            <div className="text-lg font-extrabold text-foreground">{distribution.healthy}</div>
          </div>
          <div className="rounded-lg bg-amber-500/5 p-2 border border-amber-500/10">
            <span className="text-[11px] font-semibold text-amber-400">MODERATE (50-79)</span>
            <div className="text-lg font-extrabold text-foreground">{distribution.moderate}</div>
          </div>
          <div className="rounded-lg bg-rose-500/5 p-2 border border-rose-500/10">
            <span className="text-[11px] font-semibold text-rose-400">CRITICAL (0-49)</span>
            <div className="text-lg font-extrabold text-foreground">{distribution.critical}</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

