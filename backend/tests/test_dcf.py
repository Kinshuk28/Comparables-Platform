import pytest

from app.valuation.dcf import DCFInputError, run_dcf


def base_kwargs(**overrides):
    kwargs = dict(
        base_revenue=100.0,
        revenue_growth_rates=[0.10, 0.08, 0.06, 0.05, 0.04],
        ebitda_margins=[0.20, 0.21, 0.22, 0.22, 0.22],
        tax_rate=0.25,
        capex_pct_revenue=0.04,
        da_pct_revenue=0.035,
        nwc_pct_revenue_change=0.10,
        wacc=0.10,
        terminal_growth_rate=0.025,
        net_debt=50.0,
        shares_outstanding=20.0,
    )
    kwargs.update(overrides)
    return kwargs


def test_run_dcf_produces_positive_enterprise_value():
    result = run_dcf(**base_kwargs())
    assert result["enterprise_value"] > 0
    assert len(result["years"]) == 5
    assert result["years"][0]["year"] == 1


def test_equity_value_equals_ev_minus_net_debt():
    result = run_dcf(**base_kwargs())
    assert result["equity_value"] == pytest.approx(result["enterprise_value"] - 50.0)


def test_value_per_share_matches_equity_over_shares():
    result = run_dcf(**base_kwargs())
    assert result["value_per_share"] == pytest.approx(result["equity_value"] / 20.0)


def test_higher_wacc_reduces_enterprise_value():
    low_wacc = run_dcf(**base_kwargs(wacc=0.09))
    high_wacc = run_dcf(**base_kwargs(wacc=0.13))
    assert high_wacc["enterprise_value"] < low_wacc["enterprise_value"]


def test_implied_range_is_ordered():
    result = run_dcf(**base_kwargs())
    assert result["implied_range"]["low"] <= result["value_per_share"] <= result["implied_range"]["high"]


def test_wacc_must_exceed_terminal_growth():
    with pytest.raises(DCFInputError):
        run_dcf(**base_kwargs(wacc=0.02, terminal_growth_rate=0.025))


def test_mismatched_margin_length_raises():
    with pytest.raises(DCFInputError):
        run_dcf(**base_kwargs(ebitda_margins=[0.2, 0.21]))


def test_zero_shares_outstanding_raises():
    with pytest.raises(DCFInputError):
        run_dcf(**base_kwargs(shares_outstanding=0))
