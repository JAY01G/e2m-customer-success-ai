/**
 * General Frontend Helper Utilities.
 *
 * Provides date formatting, string abbreviation/truncation, health score badge categorizations,
 * pagination window computation, and browser localStorage persistence helpers.
 */

import { CustomerStatus, SentimentType, User, UserRole } from '@/types';

/**
 * Format an ISO date string or Date object into a localized date representation.
 *
 * @param dateStr - ISO date string, Date object, or null/undefined.
 * @param options - Custom Intl.DateTimeFormatOptions.
 * @returns Localized date string or '—' placeholder on invalid/empty date.
 */
export function formatDate(
  dateStr?: string | Date | null,
  options?: Intl.DateTimeFormatOptions
): string {
  if (!dateStr) return '—';
  const date = typeof dateStr === 'string' ? new Date(dateStr) : dateStr;
  if (isNaN(date.getTime())) return '—';

  return date.toLocaleDateString(undefined, options || {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

/**
 * Format a date with abbreviated weekday name, e.g. "Mon, Jan 15, 2025".
 *
 * @param dateStr - Date representation string or object.
 * @returns Full formatted date string.
 */
export function formatFullDate(dateStr?: string | Date | null): string {
  return formatDate(dateStr, {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

/**
 * Extract 1 or 2 uppercase initials from a full name.
 *
 * @param name - Full user or contact name string.
 * @returns 1 or 2 capital initials, or 'U' fallback.
 */
export function getInitials(name?: string | null): string {
  if (!name || !name.trim()) return 'U';
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].charAt(0).toUpperCase();
  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
}

/**
 * Safely truncate a long text string appending an ellipsis if exceeded.
 *
 * @param text - Source text string.
 * @param maxLength - Maximum allowed character length before truncation.
 * @returns Truncated string or empty string.
 */
export function truncateText(
  text: string | null | undefined,
  maxLength: number = 100
): string {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return `${text.slice(0, maxLength)}...`;
}

/**
 * Categorize a numeric health score (0-100) into a structured tier with styling classes.
 *
 * @param score - Health score number.
 * @returns Categorization metadata including label, category literal, text class, and badge styling class.
 */
export function getHealthScoreCategory(score: number): {
  label: string;
  category: 'Healthy' | 'Moderate' | 'Critical';
  textClass: string;
  badgeClass: string;
} {
  if (score >= 80) {
    return {
      label: 'Healthy & Highly Engaged',
      category: 'Healthy',
      textClass: 'text-emerald-400',
      badgeClass: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400',
    };
  }
  if (score >= 50) {
    return {
      label: 'Moderate Retention Risk',
      category: 'Moderate',
      textClass: 'text-amber-400',
      badgeClass: 'border-amber-500/30 bg-amber-500/10 text-amber-400',
    };
  }
  return {
    label: 'Urgent Escalation Required',
    category: 'Critical',
    textClass: 'text-rose-400',
    badgeClass: 'border-rose-500/30 bg-rose-500/10 text-rose-400',
  };
}

/**
 * Generate a smart pagination page numbers array with ellipsis gaps for large ranges.
 *
 * @param currentPage - Currently active page index.
 * @param totalPages - Total available pages.
 * @param delta - Number of sibling page buttons around the current page.
 * @returns Array of page numbers and ellipsis strings.
 */
export function getPaginationPages(
  currentPage: number,
  totalPages: number,
  delta: number = 1
): (number | string)[] {
  const pages: (number | string)[] = [];

  for (let i = 1; i <= totalPages; i++) {
    if (
      i === 1 ||
      i === totalPages ||
      (i >= currentPage - delta && i <= currentPage + delta)
    ) {
      pages.push(i);
    } else if (pages[pages.length - 1] !== '...') {
      pages.push('...');
    }
  }

  return pages;
}

/**
 * Retrieve stored JWT access token from browser localStorage.
 *
 * @returns Token string or null.
 */
export function getStorageToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('token');
}

/**
 * Persist JWT access token to browser localStorage.
 *
 * @param token - Bearer JWT token string.
 */
export function setStorageToken(token: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem('token', token);
}

/**
 * Remove stored JWT token from browser localStorage.
 */
export function removeStorageToken(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('token');
}

/**
 * Retrieve stored refresh token from browser localStorage.
 *
 * @returns Refresh token string or null.
 */
export function getStorageRefreshToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('refresh_token');
}

/**
 * Persist refresh token to browser localStorage.
 *
 * @param token - Refresh JWT token string.
 */
export function setStorageRefreshToken(token: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem('refresh_token', token);
}

/**
 * Remove stored refresh token from browser localStorage.
 */
export function removeStorageRefreshToken(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('refresh_token');
}

/**
 * Retrieve cached User profile object from browser localStorage.
 *
 * @returns Parsed User object or null.
 */
export function getStorageUser(): User | null {
  if (typeof window === 'undefined') return null;
  const userStr = localStorage.getItem('user');
  if (!userStr) return null;
  try {
    return JSON.parse(userStr);
  } catch {
    return null;
  }
}

/**
 * Persist User profile object to browser localStorage.
 *
 * @param user - User profile object.
 */
export function setStorageUser(user: User): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem('user', JSON.stringify(user));
}

/**
 * Remove stored User profile from browser localStorage.
 */
export function removeStorageUser(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('user');
}

/**
 * Clear all authentication state (access token, refresh token, user profile) from storage.
 */
export function clearStorageAuth(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
}


