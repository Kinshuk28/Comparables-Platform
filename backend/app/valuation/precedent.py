"""Precedent Transaction Analysis.

Structurally identical to Comparable Company Analysis, but the multiples
come from historical control M&A transactions rather than public trading
peers, so they already embed a control premium and typically run richer
than trading comps.
"""

from __future__ import annotations

from app.valuation.multiples import blended_range, implied_valuation, multiple_stats


class PrecedentInputError(ValueError):
    pass


def run_precedent_transactions_analysis(
    target_revenue: float,
    target_ebitda: float,
    net_debt: float,
    shares_outstanding: float,
    transactions: list[dict],
) -> dict:
    if not transactions:
        raise PrecedentInputError("At least one precedent transaction is required")
    if shares_outstanding <= 0:
        raise PrecedentInputError("shares_outstanding must be positive")

    ev_revenue_multiples = [t["ev_revenue_multiple"] for t in transactions if t.get("ev_revenue_multiple") is not None]
    ev_ebitda_multiples = [t["ev_ebitda_multiple"] for t in transactions if t.get("ev_ebitda_multiple") is not None]

    if not ev_revenue_multiples and not ev_ebitda_multiples:
        raise PrecedentInputError("Transactions must include at least one EV/Revenue or EV/EBITDA multiple")

    revenue_stats = multiple_stats(ev_revenue_multiples)
    ebitda_stats = multiple_stats(ev_ebitda_multiples)

    revenue_implied = implied_valuation(revenue_stats, target_revenue, net_debt, shares_outstanding)
    ebitda_implied = implied_valuation(ebitda_stats, target_ebitda, net_debt, shares_outstanding)

    blended = blended_range([revenue_implied, ebitda_implied])
    if not blended:
        raise PrecedentInputError("Unable to derive an implied valuation from the supplied transactions")

    return {
        "transactions_used": transactions,
        "ev_revenue": {"stats": revenue_stats, "implied": revenue_implied},
        "ev_ebitda": {"stats": ebitda_stats, "implied": ebitda_implied},
        "implied_range": {"low": blended["per_share_low"], "high": blended["per_share_high"]},
        "value_per_share": blended["per_share_mid"],
    }
