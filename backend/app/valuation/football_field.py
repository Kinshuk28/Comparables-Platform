"""Combines the three methodologies into a football field summary and a
rule-based read on where the offer price falls relative to each range —
the quantitative backbone the narrative generator explains in prose."""

from __future__ import annotations


def _position(offer_price: float, low: float, high: float) -> str:
    if offer_price < low:
        return "below_range"
    if offer_price > high:
        return "above_range"
    return "within_range"


def build_football_field(
    dcf_result: dict | None,
    cca_result: dict | None,
    pta_result: dict | None,
    offer_price: float,
    current_share_price: float | None = None,
) -> dict:
    bars = []

    if dcf_result:
        low, high = dcf_result["implied_range"]["low"], dcf_result["implied_range"]["high"]
        bars.append(
            {
                "method": "Discounted Cash Flow",
                "low": low,
                "high": high,
                "mid": round(dcf_result["value_per_share"], 2),
                "offer_position": _position(offer_price, low, high),
            }
        )

    if cca_result:
        low, high = cca_result["implied_range"]["low"], cca_result["implied_range"]["high"]
        bars.append(
            {
                "method": "Comparable Company Analysis",
                "low": low,
                "high": high,
                "mid": round(cca_result["value_per_share"], 2),
                "offer_position": _position(offer_price, low, high),
            }
        )

    if pta_result:
        low, high = pta_result["implied_range"]["low"], pta_result["implied_range"]["high"]
        bars.append(
            {
                "method": "Precedent Transaction Analysis",
                "low": low,
                "high": high,
                "mid": round(pta_result["value_per_share"], 2),
                "offer_position": _position(offer_price, low, high),
            }
        )

    within_or_above = sum(1 for b in bars if b["offer_position"] in ("within_range", "above_range"))
    below = sum(1 for b in bars if b["offer_position"] == "below_range")

    if not bars:
        support = "insufficient_data"
    elif below == 0:
        support = "supports_fairness"
    elif within_or_above == 0:
        support = "does_not_support_fairness"
    else:
        support = "mixed"

    return {
        "bars": bars,
        "offer_price": offer_price,
        "current_share_price": current_share_price,
        "premium_to_current": (
            round((offer_price / current_share_price - 1) * 100, 2) if current_share_price else None
        ),
        "fairness_support": support,
    }
