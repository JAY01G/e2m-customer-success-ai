/**
 * HTTP API Client Configuration.
 *
 * Configures Axios instance with base URL, authentication headers,
 * request token injection, automatic 401 token refresh retry queue,
 * redirection to login on session expiry, and structured response error handling.
 */

import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { emitToast } from '@/components/providers/ToastProvider';
import {
  getStorageToken,
  setStorageToken,
  getStorageRefreshToken,
  setStorageRefreshToken,
  clearStorageAuth,
} from '@/lib/helpers';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/**
 * Custom API Error class preserving HTTP status, backend validation errors, and friendly message.
 */
export class ApiError extends Error {
  statusCode: number;
  errors?: any;
  data?: any;

  constructor(message: string, statusCode: number = 500, errors?: any, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.errors = errors;
    this.data = data;
  }
}

/**
 * Pre-configured Axios HTTP client instance for backend API communication.
 */
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Send HttpOnly refresh token cookie
  timeout: 30000, // 30s timeout
});

// Request Interceptor: Attach JWT token if available
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getStorageToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Token Refresh State and Queued Requests Handler
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: any) => void;
}> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((promise) => {
    if (error) {
      promise.reject(error);
    } else if (token) {
      promise.resolve(token);
    }
  });
  failedQueue = [];
};

/**
 * Redirect user to login page if currently in browser and not on auth pages.
 */
export const redirectToLogin = () => {
  if (typeof window !== 'undefined') {
    const path = window.location.pathname;
    if (!path.includes('/login') && !path.includes('/register')) {
      window.location.href = '/login';
    }
  }
};

// Response Interceptor: Format, standardize error payload, and handle 401 refresh & retry
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error: AxiosError<any>) => {
    const status = error.response?.status || 500;
    const responseData = error.response?.data;
    const originalRequest = error.config as (InternalAxiosRequestConfig & { _retry?: boolean; skipToast?: boolean }) | undefined;

    let errorMessage = 'An unexpected error occurred';
    let errorsList = responseData?.errors || null;

    if (responseData) {
      if (typeof responseData.message === 'string' && responseData.message.trim()) {
        errorMessage = responseData.message;
      } else if (typeof responseData.detail === 'string' && responseData.detail.trim()) {
        errorMessage = responseData.detail;
      } else if (Array.isArray(responseData.detail)) {
        // FastAPI default validation format
        const summaries = responseData.detail.map((d: any) => {
          const loc = Array.isArray(d.loc) ? d.loc.filter((l: any) => l !== 'body').join(' -> ') : 'field';
          return `${loc}: ${d.msg}`;
        });
        errorMessage = `Validation failed: ${summaries.slice(0, 2).join(', ')}`;
        errorsList = responseData.detail;
      }
    } else if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      errorMessage = 'Request timed out. Please check your connection and try again.';
    } else if (error.message === 'Network Error' || !error.response) {
      errorMessage = 'Network connection error. Please verify the backend service is running.';
    }

    const requestUrl = originalRequest?.url || '';
    const isAuthEndpoint =
      requestUrl.includes('/auth/login') ||
      requestUrl.includes('/auth/register') ||
      requestUrl.includes('/auth/refresh');

    // Handle 401 Unauthorized for regular endpoints
    if (status === 401 && originalRequest && !isAuthEndpoint) {
      // If request has already been retried once and still returned 401, session is invalid
      if (originalRequest._retry) {
        clearStorageAuth();
        redirectToLogin();
        return Promise.reject(new ApiError(errorMessage, status, errorsList, responseData));
      }

      // If another refresh request is already pending, queue this request
      if (isRefreshing) {
        return new Promise<any>((resolve, reject) => {
          failedQueue.push({
            resolve: (token: string) => {
              if (originalRequest.headers) {
                originalRequest.headers.Authorization = `Bearer ${token}`;
              }
              resolve(apiClient(originalRequest));
            },
            reject: (err: any) => {
              reject(err);
            },
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const storedRefreshToken = getStorageRefreshToken();

      try {
        // Attempt token refresh via cookie or stored refresh token
        const refreshResponse = await axios.post<{
          success: boolean;
          data: {
            access_token: string;
            token_type: string;
            expires_in: number;
            refresh_token?: string;
          };
        }>(
          `${API_BASE_URL}/auth/refresh`,
          { refresh_token: storedRefreshToken || undefined },
          {
            withCredentials: true,
            headers: { 'Content-Type': 'application/json' },
            timeout: 15000,
          }
        );

        const newAccessToken = refreshResponse.data?.data?.access_token;
        const newRefreshToken = refreshResponse.data?.data?.refresh_token;

        if (!newAccessToken) {
          throw new Error('Refresh endpoint did not return a valid access token');
        }

        // Store refreshed tokens
        setStorageToken(newAccessToken);
        if (newRefreshToken) {
          setStorageRefreshToken(newRefreshToken);
        }

        // Process all queued requests waiting for this new token
        processQueue(null, newAccessToken);

        // Update authorization header for the original failed request and retry it
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        }
        return apiClient(originalRequest);
      } catch (refreshErr: any) {
        // Token refresh failed -> clear auth and redirect to login
        processQueue(refreshErr, null);
        clearStorageAuth();
        redirectToLogin();

        if (!originalRequest?.skipToast && typeof window !== 'undefined') {
          emitToast({
            type: 'error',
            title: 'Session Expired',
            message: 'Your session has expired. Please sign in again.',
          });
        }

        return Promise.reject(
          new ApiError('Session expired. Please log in again.', 401, null, refreshErr?.response?.data)
        );
      } finally {
        isRefreshing = false;
      }
    }

    // If 401 occurred on /auth/refresh or auth endpoints, clear storage & redirect
    if (status === 401 && isAuthEndpoint) {
      if (requestUrl.includes('/auth/refresh')) {
        clearStorageAuth();
        redirectToLogin();
      }
    }

    // Automatically trigger error toast on API failure (if not skipped and not during silent refresh)
    if (!originalRequest?.skipToast && typeof window !== 'undefined') {
      let title = 'Request Failed';
      if (status === 400 || status === 422) title = 'Validation Error';
      else if (status === 401) title = 'Unauthorized';
      else if (status === 403) title = 'Access Forbidden';
      else if (status === 404) title = 'Not Found';
      else if (status === 409) title = 'Conflict';
      else if (status >= 500) title = 'Server Error';

      emitToast({
        type: 'error',
        title,
        message: errorMessage,
      });
    }

    return Promise.reject(new ApiError(errorMessage, status, errorsList, responseData));
  }
);

export default apiClient;




