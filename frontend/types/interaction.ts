import { User } from './auth';
import { BaseQueryParams } from './common';
import { AIInsight } from './insight';

export type InteractionType = 'MEETING' | 'CALL' | 'EMAIL' | 'DEMO' | 'OTHER';

export interface Interaction {
  id: string;
  customer_id: string;
  user_id?: string | null;
  user?: User | null;
  type: InteractionType;
  title: string;
  meeting_date: string;
  notes: string;
  duration_minutes?: number;
  ai_insight?: AIInsight | null;
  created_at: string;
  updated_at: string;
}

export interface InteractionQueryParams extends BaseQueryParams {
  customer_id?: string;
  user_id?: string;
  type?: InteractionType;
  search?: string;
  start_date?: string;
  end_date?: string;
}
