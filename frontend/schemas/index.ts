/**
 * Form Validation Schemas.
 *
 * Defines Zod schemas and TypeScript inferred types for authentication, customer accounts,
 * and interaction meeting logs with client-side error messaging and boundary checks.
 */

import { z } from 'zod';

/**
 * Validation schema for user authentication.
 */
export const loginSchema = z.object({
  email: z
    .string()
    .trim()
    .min(1, 'Please enter a valid email address')
    .email('Please enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
});

/** Form input payload type for login */
export type LoginFormData = z.infer<typeof loginSchema>;

/**
 * Validation schema for operator user registration.
 */
export const registerSchema = z.object({
  name: z
    .string()
    .trim()
    .min(2, 'Full name must be at least 2 characters')
    .max(100, 'Full name cannot exceed 100 characters')
    .refine((s) => s.trim().length >= 2, {
      message: 'Full name cannot be blank whitespace',
    }),
  email: z
    .string()
    .trim()
    .min(1, 'Email address is required')
    .email('Please enter a valid email address'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .max(128, 'Password cannot exceed 128 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter (A-Z)')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter (a-z)')
    .regex(/\d/, 'Password must contain at least one number (0-9)')
    .regex(
      /[!@#$%^&*(),.?":{}|<>\-_+=\[\]\\/]/,
      'Password must contain at least one special character (!@#$%^&*...)'
    ),
  role: z.enum(['ADMIN', 'CUSTOMER_SUCCESS_MANAGER', 'VIEWER']),
});

/** Form input payload type for user registration */
export type RegisterFormData = z.infer<typeof registerSchema>;

/**
 * Validation schema for customer account creation and modification.
 */
export const customerSchema = z.object({
  name: z
    .string()
    .trim()
    .min(1, 'Primary contact name is required')
    .max(150, 'Contact name cannot exceed 150 characters')
    .refine((s) => s.trim().length > 0, {
      message: 'Contact name cannot be blank whitespace',
    }),
  company_name: z
    .string()
    .trim()
    .min(1, 'Company name is required')
    .max(150, 'Company name cannot exceed 150 characters')
    .refine((s) => s.trim().length > 0, {
      message: 'Company name cannot be blank whitespace',
    }),
  email: z
    .string()
    .trim()
    .min(1, 'Email address is required')
    .email('Please enter a valid email address'),
  phone: z
    .string()
    .trim()
    .optional()
    .or(z.literal(''))
    .refine(
      (val) => {
        if (!val) return true;
        const digitCount = (val.match(/\d/g) || []).length;
        const validChars = /^\+?[0-9\s\-().]{7,25}$/.test(val);
        return validChars && digitCount >= 7;
      },
      {
        message: 'Please enter a valid phone number (e.g. +1 555-123-4567, min 7 digits)',
      }
    ),
  industry: z
    .string()
    .trim()
    .max(100, 'Industry cannot exceed 100 characters')
    .optional()
    .or(z.literal('')),
  status: z.enum(['ACTIVE', 'AT_RISK', 'CHURNED', 'PROSPECT']),
  health_score: z.coerce
    .number({ invalid_type_error: 'Health score must be a number' })
    .int('Health score must be an integer')
    .min(0, 'Health score must be between 0 and 100')
    .max(100, 'Health score must be between 0 and 100'),
  owner_id: z.string().optional().or(z.literal('')),
  notes: z
    .string()
    .trim()
    .max(5000, 'Notes cannot exceed 5000 characters')
    .optional()
    .or(z.literal('')),
});

/** Form input payload type for customer forms */
export type CustomerFormData = z.infer<typeof customerSchema>;

/**
 * Validation schema for logging customer interaction meeting notes.
 */
export const interactionSchema = z.object({
  customer_id: z
    .string()
    .trim()
    .min(1, 'Customer selection is required'),
  type: z.enum(['MEETING', 'CALL', 'EMAIL', 'DEMO', 'OTHER']),
  title: z
    .string()
    .trim()
    .min(2, 'Meeting title must be at least 2 characters')
    .max(200, 'Meeting title cannot exceed 200 characters')
    .refine((s) => s.trim().length >= 2, {
      message: 'Meeting title cannot be blank whitespace',
    }),
  meeting_date: z
    .string()
    .trim()
    .min(1, 'Meeting date is required'),
  notes: z
    .string()
    .trim()
    .min(5, 'Meeting notes must be at least 5 characters')
    .max(20000, 'Meeting notes cannot exceed 20,000 characters')
    .refine((s) => s.trim().length >= 5, {
      message: 'Meeting notes cannot be blank whitespace',
    }),
  duration_minutes: z.coerce
    .number({ invalid_type_error: 'Duration must be a number' })
    .int('Duration must be a whole number of minutes')
    .min(1, 'Duration must be at least 1 minute')
    .max(1440, 'Duration cannot exceed 1440 minutes (24 hours)')
    .optional(),
  generate_ai_insight: z.boolean().default(true),
});

/** Form input payload type for interaction forms */
export type InteractionFormData = z.infer<typeof interactionSchema>;
