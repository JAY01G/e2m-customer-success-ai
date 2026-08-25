/**
 * AI Insight Extraction API Service.
 *
 * Implements client-side HTTP calls for generating and retrieving automated meeting notes insights.
 */

import apiClient from './api';
import { AIInsight, APIResponse } from '@/types';

/**
 * AI Insight extraction API service.
 */
export const insightApi = {
  /**
   * Request LLM analysis generation or re-generation for an interaction record.
   *
   * @param interactionId - Target interaction UUID.
   * @param regenerate - Optional boolean to force re-analysis bypassing cache.
   * @returns Generated AIInsight payload.
   */
  generateInsight: async (interactionId: string, regenerate = false): Promise<AIInsight> => {
    const res = await apiClient.post<APIResponse<AIInsight>>(
      `/interactions/${interactionId}/insights?regenerate=${regenerate}`
    );
    return res.data.data;
  },

  /**
   * Fetch previously generated AI insight for an interaction.
   *
   * @param interactionId - Target interaction UUID.
   * @returns Persisted AIInsight record.
   */
  getInsight: async (interactionId: string): Promise<AIInsight> => {
    const res = await apiClient.get<APIResponse<AIInsight>>(`/interactions/${interactionId}/insights`);
    return res.data.data;
  },
};

