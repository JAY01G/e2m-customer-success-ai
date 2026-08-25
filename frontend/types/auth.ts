/**
 * Authentication and User Identity Types.
 *
 * Defines RBAC roles, User entity interfaces, Redux Auth state, and login response contracts.
 */

/** Role-Based Access Control (RBAC) tiers */
export type UserRole = 'ADMIN' | 'CUSTOMER_SUCCESS_MANAGER' | 'VIEWER';

/** Authenticated user profile entity */
export interface User {
  /** Unique UUID identifier */
  id: string;
  /** Full display name */
  name: string;
  /** Primary contact email */
  email: string;
  /** Assigned system role */
  role: UserRole;
  /** Account active status */
  is_active: boolean;
  /** Account creation timestamp */
  created_at?: string;
  /** Last modification timestamp */
  updated_at?: string;
}

/** Client-side Redux authentication slice state */
export interface AuthState {
  /** Currently logged-in user profile */
  user: User | null;
  /** Active JWT access token */
  token: string | null;
  /** Authentication status flag */
  isAuthenticated: boolean;
  /** Async loading state */
  isLoading: boolean;
  /** Error message string if authentication failed */
  error: string | null;
}

/** Server response payload from login/refresh/register endpoints */
export interface AuthResponseData {
  /** JWT access token */
  access_token: string;
  /** Token bearer type (e.g. 'bearer') */
  token_type: string;
  /** Token expiration duration in seconds */
  expires_in: number;
  /** Refresh token JWT (if issued) */
  refresh_token?: string;
  /** Authenticated user profile summary */
  user: User;
}

