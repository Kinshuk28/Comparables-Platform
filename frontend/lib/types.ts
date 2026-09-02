export type ConsiderationType = "cash" | "stock" | "mixed";

export interface DCFAssumptions {
  revenue_growth_rates: number[];
  ebitda_margins: number[];
  tax_rate: number;
  capex_pct_revenue: number;
  da_pct_revenue: number;
  nwc_pct_revenue_change: number;
  wacc: number;
  terminal_growth_rate: number;
}

export interface ComparableCompany {
  name: string;
  ev_revenue_multiple: number | null;
  ev_ebitda_multiple: number | null;
}

export interface PrecedentTransaction {
  target_name: string;
  acquirer_name: string | null;
  announced_date: string | null;
  ev_revenue_multiple: number | null;
  ev_ebitda_multiple: number | null;
}

export interface ValuationRequest {
  target_name: string;
  acquirer_name: string | null;
  offer_price: number;
  current_share_price: number | null;
  consideration_type: ConsiderationType;
  shares_outstanding: number;
  net_debt: number;
  ltm_revenue: number;
  ltm_ebitda: number;
  dcf: DCFAssumptions;
  comps: ComparableCompany[];
  precedent_transactions: PrecedentTransaction[];
}

export interface DCFYear {
  year: number;
  revenue: number;
  ebitda: number;
  ebit: number;
  nopat: number;
  da: number;
  capex: number;
  nwc_change: number;
  fcf: number;
  discount_factor: number;
  pv_fcf: number;
}

export interface DCFResult {
  years: DCFYear[];
  terminal_value: number;
  pv_terminal_value: number;
  pv_fcf_sum: number;
  enterprise_value: number;
  equity_value: number;
  value_per_share: number;
  sensitivity: {
    wacc_scenarios: number[];
    growth_scenarios: number[];
    grid: { wacc: number; values: (number | null)[] }[];
  };
  implied_range: { low: number; high: number };
  assumptions: Record<string, number>;
}

export interface MultipleStats {
  count: number;
  min: number;
  max: number;
  median: number;
  mean: number;
  p25: number;
  p75: number;
}

export interface ImpliedValuation {
  ev_low: number;
  ev_mid: number;
  ev_high: number;
  equity_low: number;
  equity_mid: number;
  equity_high: number;
  per_share_low: number;
  per_share_mid: number;
  per_share_high: number;
}

export interface MultiplesResult {
  ev_revenue: { stats: MultipleStats | null; implied: ImpliedValuation | null };
  ev_ebitda: { stats: MultipleStats | null; implied: ImpliedValuation | null };
  implied_range: { low: number; high: number };
  value_per_share: number;
}

export interface FootballFieldBar {
  method: string;
  low: number;
  mid: number;
  high: number;
  offer_position: "below_range" | "within_range" | "above_range";
}

export interface FootballField {
  bars: FootballFieldBar[];
  offer_price: number;
  current_share_price: number | null;
  premium_to_current: number | null;
  fairness_support: "supports_fairness" | "does_not_support_fairness" | "mixed" | "insufficient_data";
}

export interface ValuationResults {
  dcf: DCFResult;
  comparable_company_analysis: MultiplesResult | null;
  precedent_transaction_analysis: MultiplesResult | null;
  football_field: FootballField;
}

export interface Valuation {
  id: string;
  target_name: string;
  acquirer_name: string | null;
  offer_price: number;
  current_share_price: number | null;
  consideration_type: ConsiderationType;
  created_at: string;
  inputs: ValuationRequest;
  results: ValuationResults;
}

export interface ValuationSummary {
  id: string;
  target_name: string;
  acquirer_name: string | null;
  offer_price: number;
  created_at: string;
  fairness_support: FootballField["fairness_support"] | null;
}

export interface FairnessOpinion {
  id: string;
  valuation_id: string;
  narrative: string;
  model_used: string;
  created_at: string;
}

export interface FairnessOpinionDetail extends FairnessOpinion {
  valuation: Valuation;
}
