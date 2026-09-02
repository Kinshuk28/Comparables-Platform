from app.valuation.football_field import build_football_field


DCF = {"value_per_share": 25.0, "implied_range": {"low": 22.0, "high": 28.0}}
CCA = {"value_per_share": 24.0, "implied_range": {"low": 20.0, "high": 27.0}}
PTA = {"value_per_share": 29.0, "implied_range": {"low": 26.0, "high": 32.0}}


def test_offer_within_all_ranges_supports_fairness():
    result = build_football_field(DCF, CCA, PTA, offer_price=27.0, current_share_price=20.0)
    assert result["fairness_support"] == "supports_fairness"
    assert len(result["bars"]) == 3
    assert result["premium_to_current"] == 35.0


def test_offer_below_all_ranges_does_not_support_fairness():
    result = build_football_field(DCF, CCA, PTA, offer_price=10.0)
    assert result["fairness_support"] == "does_not_support_fairness"


def test_offer_mixed_relative_to_ranges():
    rich_pta = {"value_per_share": 32.0, "implied_range": {"low": 30.0, "high": 35.0}}
    result = build_football_field(DCF, CCA, rich_pta, offer_price=25.0)
    assert result["fairness_support"] == "mixed"


def test_missing_method_is_omitted():
    result = build_football_field(DCF, None, None, offer_price=25.0)
    assert len(result["bars"]) == 1
