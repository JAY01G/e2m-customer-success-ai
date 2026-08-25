/**
 * Common API Response and Pagination Type Contracts.
 *
 * Defines uniform JSON envelope interfaces and base query parameter schemas.
 */

/** Standard API response envelope matching backend format */
export interface APIResponse<T> {
  /** Boolean status flag */
  success: boolean;
  /** Generic payload */
  data: T;
  /** Human-readable status message */
  message: string;
  /** Optional error details or validation error mapping */
  errors?: any;
}

/** Paginated collection data container */
export interface PaginatedData<T> {
  /** List of records for current page */
  items: T[];
  /** 1-based page index */
  page: number;
  /** Maximum items per page */
  page_size: number;
  /** Total matching items count */
  total: number;
  /** Calculated total page count */
  total_pages: number;
}

/** Base query parameters for paginated and sorted endpoints */
export interface BaseQueryParams {
  /** Requested page number */
  page?: number;
  /** Items per page limit */
  page_size?: number;
  /** Target sort column */
  sort_by?: string;
  /** Sort order direction */
  sort_order?: 'asc' | 'desc';
}

