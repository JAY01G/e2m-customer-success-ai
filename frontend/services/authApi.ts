/**
 * Authentication API Service.
 *
 * Implements client-side calls for login, registration, token refresh, and user profile queries.
 */

import apiClient from './api';
import { APIResponse, AuthResponseData, User } from '@/types';
import { LoginFormData, RegisterFormData } from '@/schemas';

/**
 * Authentication API endpoints service object.
 */
export const authApi = {
  /**
   * Authenticate user credentials and return JWT tokens.
   *
   * @param data - User login credentials (email, password).
   * @returns AuthResponseData containing access token and user profile.
   */
  login: async (data: LoginFormData): Promise<AuthResponseData> => {
    const res = await apiClient.post<APIResponse<AuthResponseData>>('/auth/login', data);
    return res.data.data;
  },

  /**
   * Register a new operator account.
   *
   * @param data - User registration payload.
   * @returns AuthResponseData containing token and user profile.
   */
  register: async (data: RegisterFormData): Promise<AuthResponseData> => {
    const res = await apiClient.post<APIResponse<AuthResponseData>>('/auth/register', data);
    return res.data.data;
  },

  /**
   * Retrieve currently authenticated user profile.
   *
   * @returns User profile model.
   */
  getMe: async (): Promise<User> => {
    const res = await apiClient.get<APIResponse<User>>('/auth/me');
    return res.data.data;
  },

  /**
   * Request a fresh access token using the HttpOnly refresh token cookie or storage token.
   *
   * @param refreshTokenStr - Optional explicit refresh token string.
   * @returns AuthResponseData containing new access token (and refreshed token).
   */
  refreshToken: async (refreshTokenStr?: string): Promise<AuthResponseData> => {
    const res = await apiClient.post<APIResponse<AuthResponseData>>(
      '/auth/refresh',
      { refresh_token: refreshTokenStr || undefined },
      { skipToast: true } as any
    );
    return res.data.data;
  },
};


