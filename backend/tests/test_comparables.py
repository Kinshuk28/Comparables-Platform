import pytest

from app.valuation.comparables import ComparablesInputError, run_comparable_company_analysis


COMPS = [
    {"name": "Peer A", "ev_revenue_multiple": 3.0, "ev_ebitda_multiple": 12.0},
    {"name": "Peer B", "ev_revenue_multiple": 3.5, "ev_ebitda_multiple": 13.0},
    {"name": "Peer C", "ev_revenue_multiple": 2.8, "ev_ebitda_multiple": 11.0},
    {"name": "Peer D", "ev_revenue_multiple": 4.0, "ev_ebitda_multiple": 14.5},
]


def test_run_comparable_company_analysis_basic():
    result = run_comparable_company_analysis(
        target_revenue=100.0,
        target_ebitda=20.0,
        net_debt=30.0,
        shares_outstanding=10.0,
        comps=COMPS,
    )
    assert result["implied_range"]["low"] <= result["value_per_share"] <= result["implied_range"]["high"]
    assert result["ev_revenue"]["stats"]["count"] == 4


def test_empty_comps_raises():
    with pytest.raises(ComparablesInputError):
        run_comparable_company_analysis(100.0, 20.0, 30.0, 10.0, [])


def test_zero_shares_raises():
    with pytest.raises(ComparablesInputError):
        run_comparable_company_analysis(100.0, 20.0, 30.0, 0, COMPS)


def test_missing_multiples_raises():
    with pytest.raises(ComparablesInputError):
        run_comparable_company_analysis(
            100.0, 20.0, 30.0, 10.0, [{"name": "Peer A"}]
        )


def test_single_multiple_type_still_works():
    comps = [{"name": "Peer A", "ev_ebitda_multiple": 12.0}, {"name": "Peer B", "ev_ebitda_multiple": 13.0}]
    result = run_comparable_company_analysis(100.0, 20.0, 30.0, 10.0, comps)
    assert result["ev_revenue"]["stats"] is None
    assert result["ev_ebitda"]["stats"] is not None
