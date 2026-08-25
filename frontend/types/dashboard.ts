import { Customer } from './customer';
import { Interaction } from './interaction';
import { SentimentType } from './insight';

export interface SentimentDistribution {
  positive: number;
  neutral: number;
  negative: number;
  positive_percentage: number;
  neutral_percentage: number;
  negative_percentage: number;
}

export interface HealthDistribution {
  healthy: number;
  moderate: number;
  critical: number;
}

export interface StatusDistribution {
  active: number;
  at_risk: number;
  churned: number;
  prospect: number;
}

export interface ActionItemSummary {
  interaction_id: string;
  customer_name: string;
  company_name: string;
  action_item: string;
}

export interface RiskSummary {
  interaction_id: string;
  customer_name: string;
  company_name: string;
  risk: string;
  sentiment: SentimentType;
}

export interface DashboardSummary {
  total_customers: number;
  active_customers: number;
  at_risk_customers: number;
  churned_customers: number;
  prospect_customers: number;
  average_health_score: number;
  total_interactions: number;
  recent_interactions_count: number;
  sentiment_distribution: SentimentDistribution;
  health_distribution: HealthDistribution;
  status_distribution: StatusDistribution;
  recent_interactions: Interaction[];
  at_risk_customers_list: Customer[];
  recent_risks: RiskSummary[];
  recent_action_items: ActionItemSummary[];
}
