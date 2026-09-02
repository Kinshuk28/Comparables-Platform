import pytest

from app.valuation.precedent import PrecedentInputError, run_precedent_transactions_analysis


TRANSACTIONS = [
    {"target_name": "Deal A", "ev_revenue_multiple": 3.8, "ev_ebitda_multiple": 14.0},
    {"target_name": "Deal B", "ev_revenue_multiple": 4.2, "ev_ebitda_multiple": 15.5},
    {"target_name": "Deal C", "ev_revenue_multiple": 3.5, "ev_ebitda_multiple": 13.0},
]


def test_run_precedent_transactions_analysis_basic():
    result = run_precedent_transactions_analysis(
        target_revenue=100.0,
        target_ebitda=20.0,
        net_debt=30.0,
        shares_outstanding=10.0,
        transactions=TRANSACTIONS,
    )
    assert result["implied_range"]["low"] <= result["value_per_share"] <= result["implied_range"]["high"]


def test_precedent_multiples_run_richer_than_trading_comps_in_this_fixture():
    result = run_precedent_transactions_analysis(100.0, 20.0, 30.0, 10.0, TRANSACTIONS)
    assert result["ev_ebitda"]["stats"]["median"] > 12.0


def test_empty_transactions_raises():
    with pytest.raises(PrecedentInputError):
        run_precedent_transactions_analysis(100.0, 20.0, 30.0, 10.0, [])
