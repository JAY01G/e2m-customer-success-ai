/**
 * Customer Interaction API Service.
 *
 * Implements client-side HTTP calls for interaction touchpoint logging, listing, updates, and deletion.
 */

import apiClient from './api';
import { APIResponse, Interaction, InteractionQueryParams, PaginatedData } from '@/types';
import { InteractionFormData } from '@/schemas';

/**
 * Interaction touchpoints API service.
 */
export const interactionApi = {
  /**
   * Fetch paginated and filtered list of interaction logs.
   *
   * @param params - Optional filter query parameters.
   * @returns Paginated interaction collection.
   */
  getInteractions: async (params?: InteractionQueryParams): Promise<PaginatedData<Interaction>> => {
    const res = await apiClient.get<APIResponse<PaginatedData<Interaction>>>('/interactions', {
      params,
    });
    return res.data.data;
  },

  /**
   * Fetch a single interaction record with AI insight by UUID.
   *
   * @param id - Interaction UUID string.
   * @returns Interaction record.
   */
  getInteraction: async (id: string): Promise<Interaction> => {
    const res = await apiClient.get<APIResponse<Interaction>>(`/interactions/${id}`);
    return res.data.data;
  },

  /**
   * Record a new customer interaction and trigger AI processing.
   *
   * @param data - Interaction form payload.
   * @returns Created Interaction record with insights.
   */
  createInteraction: async (data: InteractionFormData): Promise<Interaction> => {
    const res = await apiClient.post<APIResponse<Interaction>>('/interactions', data);
    return res.data.data;
  },

  /**
   * Update fields on an existing interaction.
   *
   * @param id - Interaction UUID string.
   * @param data - Updated interaction fields.
   * @returns Updated Interaction record.
   */
  updateInteraction: async (id: string, data: Partial<InteractionFormData>): Promise<Interaction> => {
    const res = await apiClient.patch<APIResponse<Interaction>>(`/interactions/${id}`, data);
    return res.data.data;
  },

  /**
   * Delete an interaction record by UUID.
   *
   * @param id - Interaction UUID string.
   */
  deleteInteraction: async (id: string): Promise<void> => {
    await apiClient.delete<APIResponse<null>>(`/interactions/${id}`);
  },
};

