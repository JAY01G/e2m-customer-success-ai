/**
 * AI Insight and Intelligence Types.
 *
 * Defines sentiment tiers, generation status states, AI insight structures, and insight generation parameters.
 */

import { BaseQueryParams } from './common';

/** Categorical sentiment value */
export type SentimentType = 'Positive' | 'Neutral' | 'Negative';

/** AI generation execution status */
export type GenerationStatus = 'SUCCESS' | 'FAILED' | 'FALLBACK';

/** AI insight extraction record */
export interface AIInsight {
  /** Unique UUID identifier */
  id: string;
  /** Parent interaction UUID */
  interaction_id: string;
  /** Synthesized business summary */
  summary: string;
  /** Detected sentiment classification */
  sentiment: SentimentType;
  /** Extracted next steps / action items */
  action_items: string[];
  /** Flagged customer risks and churn factors */
  risks: string[];
  /** AI model name used for inference */
  model: string;
  /** LLM generation status flag */
  generation_status: GenerationStatus;
  /** Creation timestamp */
  created_at: string;
  /** Last modification timestamp */
  updated_at: string;
}

/** Query parameters for insight retrieval */
export interface InsightQueryParams extends BaseQueryParams {
  /** Filter by sentiment classification */
  sentiment?: SentimentType;
  /** Filter by generation status */
  generation_status?: GenerationStatus;
  /** Filter for presence of flagged risks */
  has_risks?: boolean;
  /** Filter for presence of action items */
  has_action_items?: boolean;
}

/** Payload parameters for triggering on-demand insight generation */
export interface GenerateInsightParams {
  /** Target interaction UUID */
  interactionId: string;
  /** Force bypass existing cache */
  regenerate?: boolean;
}

