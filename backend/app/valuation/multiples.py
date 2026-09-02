"""Shared statistics for multiples-based valuation (comps and precedent deals).

Both Comparable Company Analysis and Precedent Transaction Analysis apply a
distribution of peer EV/Revenue and EV/EBITDA multiples to the target's own
metrics. The only real difference between the two methodologies is the
source of the multiples (public trading peers vs. historical M&A deals,
where the latter already embeds a control premium) — the math is identical.
"""

from __future__ import annotations

import statistics


def _percentile(sorted_values: list[float], pct: float) -> float:
    if len(sorted_values) == 1:
        return sorted_values[0]
    k = (len(sorted_values) - 1) * (pct / 100)
    f = int(k)
    c = min(f + 1, len(sorted_values) - 1)
    if f == c:
        return sorted_values[f]
    return sorted_values[f] + (sorted_values[c] - sorted_values[f]) * (k - f)


def multiple_stats(multiples: list[float]) -> dict | None:
    if not multiples:
        return None
    ordered = sorted(multiples)
    return {
        "count": len(multiples),
        "min": min(multiples),
        "max": max(multiples),
        "median": statistics.median(multiples),
        "mean": statistics.mean(multiples),
        "p25": round(_percentile(ordered, 25), 2),
        "p75": round(_percentile(ordered, 75), 2),
    }


def implied_valuation(stats: dict | None, target_metric: float | None, net_debt: float, shares_outstanding: float) -> dict | None:
    """Applies the p25-p75 multiple range (the customary comps trading range)
    to the target metric to derive an implied enterprise/equity/per-share range."""
    if not stats or target_metric is None:
        return None

    ev_low = stats["p25"] * target_metric
    ev_mid = stats["median"] * target_metric
    ev_high = stats["p75"] * target_metric

    equity_low = ev_low - net_debt
    equity_mid = ev_mid - net_debt
    equity_high = ev_high - net_debt

    return {
        "ev_low": round(ev_low, 2),
        "ev_mid": round(ev_mid, 2),
        "ev_high": round(ev_high, 2),
        "equity_low": round(equity_low, 2),
        "equity_mid": round(equity_mid, 2),
        "equity_high": round(equity_high, 2),
        "per_share_low": round(equity_low / shares_outstanding, 2) if shares_outstanding else None,
        "per_share_mid": round(equity_mid / shares_outstanding, 2) if shares_outstanding else None,
        "per_share_high": round(equity_high / shares_outstanding, 2) if shares_outstanding else None,
    }


def blended_range(implied_results: list[dict | None]) -> dict | None:
    """Averages the per-share low/mid/high across whichever multiple types
    (EV/Revenue, EV/EBITDA) produced a valid implied valuation."""
    valid = [r for r in implied_results if r and r.get("per_share_low") is not None]
    if not valid:
        return None

    def avg(key: str) -> float:
        return round(sum(r[key] for r in valid) / len(valid), 2)

    return {
        "per_share_low": avg("per_share_low"),
        "per_share_mid": avg("per_share_mid"),
        "per_share_high": avg("per_share_high"),
    }
