/**
 * Executive Dashboard API Service.
 *
 * Implements client-side HTTP calls for executive dashboard KPI aggregation.
 */

import apiClient from './api';
import { APIResponse, DashboardSummary } from '@/types';

/**
 * Dashboard analytics API service.
 */
export const dashboardApi = {
  /**
   * Fetch consolidated dashboard metrics, health score distribution, and recent risks.
   *
   * @returns DashboardSummary containing metrics and distribution data.
   */
  getDashboardSummary: async (): Promise<DashboardSummary> => {
    const res = await apiClient.get<APIResponse<DashboardSummary>>('/dashboard/summary');
    return res.data.data;
  },
};

