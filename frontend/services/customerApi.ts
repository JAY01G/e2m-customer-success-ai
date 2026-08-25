/**
 * Customer Management API Service.
 *
 * Implements client-side HTTP calls for customer listing, retrieval, creation, updates, and deletion.
 */

import apiClient from './api';
import { APIResponse, Customer, CustomerQueryParams, PaginatedData } from '@/types';
import { CustomerFormData } from '@/schemas';

/**
 * Customer CRUD and query API service.
 */
export const customerApi = {
  /**
   * Fetch paginated and filtered list of customers.
   *
   * @param params - Optional query filters and pagination options.
   * @returns Paginated customer collection.
   */
  getCustomers: async (params?: CustomerQueryParams): Promise<PaginatedData<Customer>> => {
    const res = await apiClient.get<APIResponse<PaginatedData<Customer>>>('/customers', {
      params,
    });
    return res.data.data;
  },

  /**
   * Fetch a single customer record by UUID.
   *
   * @param id - Customer UUID string.
   * @returns Customer account details.
   */
  getCustomer: async (id: string): Promise<Customer> => {
    const res = await apiClient.get<APIResponse<Customer>>(`/customers/${id}`);
    return res.data.data;
  },

  /**
   * Create and persist a new customer record.
   *
   * @param data - Customer form payload.
   * @returns Created Customer account.
   */
  createCustomer: async (data: CustomerFormData): Promise<Customer> => {
    const res = await apiClient.post<APIResponse<Customer>>('/customers', data);
    return res.data.data;
  },

  /**
   * Update existing customer details.
   *
   * @param id - Customer UUID.
   * @param data - Updated customer attributes.
   * @returns Updated Customer account.
   */
  updateCustomer: async (id: string, data: Partial<CustomerFormData>): Promise<Customer> => {
    const res = await apiClient.patch<APIResponse<Customer>>(`/customers/${id}`, data);
    return res.data.data;
  },

  /**
   * Delete a customer record by UUID.
   *
   * @param id - Customer UUID.
   */
  deleteCustomer: async (id: string): Promise<void> => {
    await apiClient.delete<APIResponse<null>>(`/customers/${id}`);
  },
};

