/**
 * UI Styling and Classname Utilities.
 *
 * Provides className merging using clsx and tailwind-merge to safely resolve Tailwind CSS conflicts.
 */

import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merges conditional and dynamic class names resolving Tailwind CSS specificity conflicts.
 *
 * @param inputs - List of class names, objects, or expressions.
 * @returns Combined and deduped class name string.
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

