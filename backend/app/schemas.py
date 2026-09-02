from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class DCFAssumptions(BaseModel):
    revenue_growth_rates: list[float] = Field(min_length=1, max_length=10)
    ebitda_margins: list[float] = Field(min_length=1, max_length=10)
    tax_rate: float = Field(ge=0, le=1)
    capex_pct_revenue: float = Field(ge=0, le=1)
    da_pct_revenue: float = Field(ge=0, le=1)
    nwc_pct_revenue_change: float = Field(ge=-1, le=1)
    wacc: float = Field(gt=0, le=1)
    terminal_growth_rate: float = Field(ge=-0.1, le=0.15)

    @model_validator(mode="after")
    def check_lengths_match(self) -> "DCFAssumptions":
        if len(self.revenue_growth_rates) != len(self.ebitda_margins):
            raise ValueError("revenue_growth_rates and ebitda_margins must have the same number of years")
        if self.wacc <= self.terminal_growth_rate:
            raise ValueError("WACC must be greater than the terminal growth rate")
        return self


class ComparableCompany(BaseModel):
    name: str
    ev_revenue_multiple: float | None = Field(default=None, ge=0)
    ev_ebitda_multiple: float | None = Field(default=None, ge=0)


class PrecedentTransaction(BaseModel):
    target_name: str
    acquirer_name: str | None = None
    announced_date: str | None = None
    ev_revenue_multiple: float | None = Field(default=None, ge=0)
    ev_ebitda_multiple: float | None = Field(default=None, ge=0)


class ValuationRequest(BaseModel):
    target_name: str = Field(min_length=1, max_length=255)
    acquirer_name: str | None = None
    offer_price: float = Field(gt=0)
    current_share_price: float | None = Field(default=None, gt=0)
    consideration_type: Literal["cash", "stock", "mixed"] = "cash"
    shares_outstanding: float = Field(gt=0)
    net_debt: float = 0

    ltm_revenue: float = Field(gt=0)
    ltm_ebitda: float = Field(gt=0)

    dcf: DCFAssumptions
    comps: list[ComparableCompany] = Field(default_factory=list)
    precedent_transactions: list[PrecedentTransaction] = Field(default_factory=list)


class ValuationResponse(BaseModel):
    id: str
    target_name: str
    acquirer_name: str | None
    offer_price: float
    current_share_price: float | None
    consideration_type: str
    created_at: datetime
    inputs: dict[str, Any]
    results: dict[str, Any]

    model_config = {"from_attributes": True}


class ValuationSummary(BaseModel):
    id: str
    target_name: str
    acquirer_name: str | None
    offer_price: float
    created_at: datetime
    fairness_support: str | None = None

    model_config = {"from_attributes": True}


class FairnessOpinionResponse(BaseModel):
    id: str
    valuation_id: str
    narrative: str
    model_used: str
    created_at: datetime

    model_config = {"from_attributes": True, "protected_namespaces": ()}


class FairnessOpinionDetailResponse(FairnessOpinionResponse):
    valuation: ValuationResponse
