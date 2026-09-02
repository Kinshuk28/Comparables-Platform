"""Discounted Cash Flow valuation.

Unlevered free cash flow is projected explicitly for each forecast year, a
terminal value is derived with the Gordon Growth (perpetuity growth) method,
and both are discounted back to present value at the WACC. A WACC/terminal
growth sensitivity grid is used to derive an implied per-share value range
for the football field, mirroring how banks present a DCF range rather than
a single point estimate.
"""

from __future__ import annotations

WACC_SENSITIVITY_STEP = 0.01
TERMINAL_GROWTH_SENSITIVITY_STEP = 0.005


class DCFInputError(ValueError):
    pass


def _project_fcfs(
    base_revenue: float,
    revenue_growth_rates: list[float],
    ebitda_margins: list[float],
    tax_rate: float,
    capex_pct_revenue: float,
    da_pct_revenue: float,
    nwc_pct_revenue_change: float,
) -> list[dict]:
    years: list[dict] = []
    revenue = base_revenue
    prev_revenue = base_revenue

    for i, growth_rate in enumerate(revenue_growth_rates):
        revenue = revenue * (1 + growth_rate)
        margin = ebitda_margins[i]
        ebitda = revenue * margin
        da = revenue * da_pct_revenue
        ebit = ebitda - da
        nopat = ebit * (1 - tax_rate)
        capex = revenue * capex_pct_revenue
        delta_revenue = revenue - prev_revenue
        nwc_change = delta_revenue * nwc_pct_revenue_change
        fcf = nopat + da - capex - nwc_change

        years.append(
            {
                "year": i + 1,
                "revenue": revenue,
                "ebitda": ebitda,
                "ebit": ebit,
                "nopat": nopat,
                "da": da,
                "capex": capex,
                "nwc_change": nwc_change,
                "fcf": fcf,
            }
        )
        prev_revenue = revenue

    return years


def _enterprise_value(fcfs: list[float], wacc: float, terminal_growth_rate: float) -> tuple[float, float, float]:
    """Returns (enterprise_value, pv_of_explicit_fcfs, pv_of_terminal_value)."""
    if wacc <= terminal_growth_rate:
        raise DCFInputError("WACC must be greater than the terminal growth rate")

    pv_fcf_sum = sum(fcf / ((1 + wacc) ** (i + 1)) for i, fcf in enumerate(fcfs))
    terminal_value = fcfs[-1] * (1 + terminal_growth_rate) / (wacc - terminal_growth_rate)
    pv_terminal_value = terminal_value / ((1 + wacc) ** len(fcfs))
    return pv_fcf_sum + pv_terminal_value, pv_fcf_sum, pv_terminal_value


def run_dcf(
    base_revenue: float,
    revenue_growth_rates: list[float],
    ebitda_margins: list[float],
    tax_rate: float,
    capex_pct_revenue: float,
    da_pct_revenue: float,
    nwc_pct_revenue_change: float,
    wacc: float,
    terminal_growth_rate: float,
    net_debt: float,
    shares_outstanding: float,
) -> dict:
    if not revenue_growth_rates:
        raise DCFInputError("At least one projection year is required")
    if len(ebitda_margins) != len(revenue_growth_rates):
        raise DCFInputError("ebitda_margins must have the same length as revenue_growth_rates")
    if base_revenue <= 0:
        raise DCFInputError("base_revenue must be positive")
    if shares_outstanding <= 0:
        raise DCFInputError("shares_outstanding must be positive")
    if wacc <= terminal_growth_rate:
        raise DCFInputError("WACC must be greater than the terminal growth rate")

    years = _project_fcfs(
        base_revenue,
        revenue_growth_rates,
        ebitda_margins,
        tax_rate,
        capex_pct_revenue,
        da_pct_revenue,
        nwc_pct_revenue_change,
    )
    fcfs = [y["fcf"] for y in years]

    enterprise_value, pv_fcf_sum, pv_terminal_value = _enterprise_value(fcfs, wacc, terminal_growth_rate)
    terminal_value = fcfs[-1] * (1 + terminal_growth_rate) / (wacc - terminal_growth_rate)
    equity_value = enterprise_value - net_debt
    value_per_share = equity_value / shares_outstanding

    for y in years:
        i = y["year"] - 1
        y["discount_factor"] = 1 / ((1 + wacc) ** (i + 1))
        y["pv_fcf"] = y["fcf"] * y["discount_factor"]

    wacc_scenarios = [wacc - WACC_SENSITIVITY_STEP, wacc, wacc + WACC_SENSITIVITY_STEP]
    growth_scenarios = [
        terminal_growth_rate - TERMINAL_GROWTH_SENSITIVITY_STEP,
        terminal_growth_rate,
        terminal_growth_rate + TERMINAL_GROWTH_SENSITIVITY_STEP,
    ]

    sensitivity_grid = []
    per_share_values = []
    for w in wacc_scenarios:
        row = []
        for g in growth_scenarios:
            if w <= g or w <= 0:
                row.append(None)
                continue
            ev, _, _ = _enterprise_value(fcfs, w, g)
            eq = ev - net_debt
            per_share = eq / shares_outstanding
            row.append(round(per_share, 2))
            per_share_values.append(per_share)
        sensitivity_grid.append({"wacc": round(w, 4), "values": row})

    if not per_share_values:
        per_share_values = [value_per_share]

    implied_low = min(per_share_values)
    implied_high = max(per_share_values)

    return {
        "years": years,
        "terminal_value": terminal_value,
        "pv_terminal_value": pv_terminal_value,
        "pv_fcf_sum": pv_fcf_sum,
        "enterprise_value": enterprise_value,
        "equity_value": equity_value,
        "value_per_share": value_per_share,
        "sensitivity": {
            "wacc_scenarios": [round(w, 4) for w in wacc_scenarios],
            "growth_scenarios": [round(g, 4) for g in growth_scenarios],
            "grid": sensitivity_grid,
        },
        "implied_range": {"low": round(implied_low, 2), "high": round(implied_high, 2)},
        "assumptions": {
            "wacc": wacc,
            "terminal_growth_rate": terminal_growth_rate,
            "tax_rate": tax_rate,
            "capex_pct_revenue": capex_pct_revenue,
            "da_pct_revenue": da_pct_revenue,
            "nwc_pct_revenue_change": nwc_pct_revenue_change,
            "net_debt": net_debt,
            "shares_outstanding": shares_outstanding,
        },
    }
