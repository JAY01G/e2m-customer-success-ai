/**
 * Customer Account Types.
 *
 * Defines customer lifecycle statuses, Customer ORM representations, and query filter interfaces.
 */

import { User } from './auth';
import { BaseQueryParams } from './common';

/** Customer lifecycle classification */
export type CustomerStatus = 'ACTIVE' | 'AT_RISK' | 'CHURNED' | 'PROSPECT';

/** Customer account record */
export interface Customer {
  /** Unique UUID identifier */
  id: string;
  /** Primary contact person name */
  name: string;
  /** Company organization name */
  company_name: string;
  /** Contact email */
  email: string;
  /** Optional phone number */
  phone?: string | null;
  /** Business industry */
  industry?: string | null;
  /** Account lifecycle status */
  status: CustomerStatus;
  /** Numeric health score rating (0-100) */
  health_score: number;
  /** UUID of assigned CSM / Owner */
  owner_id?: string | null;
  /** Populated CSM User profile */
  owner?: User | null;
  /** Internal account notes */
  notes?: string | null;
  /** Record creation timestamp */
  created_at: string;
  /** Last modification timestamp */
  updated_at: string;
}

/** Query parameters for customer listing and filtering */
export interface CustomerQueryParams extends BaseQueryParams {
  /** Text search across name, company, email */
  search?: string;
  /** Status filter */
  status?: CustomerStatus;
  /** Lower health score limit */
  min_health_score?: number;
  /** Upper health score limit */
  max_health_score?: number;
  /** CSM owner UUID filter */
  owner_id?: string;
  /** Industry category filter */
  industry?: string;
}

