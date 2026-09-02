"""Comparable Company Analysis (trading comps).

Applies the peer group's EV/Revenue and EV/EBITDA multiples to the target's
own revenue and EBITDA to derive an implied valuation range.
"""

from __future__ import annotations

from app.valuation.multiples import blended_range, implied_valuation, multiple_stats


class ComparablesInputError(ValueError):
    pass


def run_comparable_company_analysis(
    target_revenue: float,
    target_ebitda: float,
    net_debt: float,
    shares_outstanding: float,
    comps: list[dict],
) -> dict:
    if not comps:
        raise ComparablesInputError("At least one comparable company is required")
    if shares_outstanding <= 0:
        raise ComparablesInputError("shares_outstanding must be positive")

    ev_revenue_multiples = [c["ev_revenue_multiple"] for c in comps if c.get("ev_revenue_multiple") is not None]
    ev_ebitda_multiples = [c["ev_ebitda_multiple"] for c in comps if c.get("ev_ebitda_multiple") is not None]

    if not ev_revenue_multiples and not ev_ebitda_multiples:
        raise ComparablesInputError("Comps must include at least one EV/Revenue or EV/EBITDA multiple")

    revenue_stats = multiple_stats(ev_revenue_multiples)
    ebitda_stats = multiple_stats(ev_ebitda_multiples)

    revenue_implied = implied_valuation(revenue_stats, target_revenue, net_debt, shares_outstanding)
    ebitda_implied = implied_valuation(ebitda_stats, target_ebitda, net_debt, shares_outstanding)

    blended = blended_range([revenue_implied, ebitda_implied])
    if not blended:
        raise ComparablesInputError("Unable to derive an implied valuation from the supplied comps")

    return {
        "comps_used": comps,
        "ev_revenue": {"stats": revenue_stats, "implied": revenue_implied},
        "ev_ebitda": {"stats": ebitda_stats, "implied": ebitda_implied},
        "implied_range": {"low": blended["per_share_low"], "high": blended["per_share_high"]},
        "value_per_share": blended["per_share_mid"],
    }
