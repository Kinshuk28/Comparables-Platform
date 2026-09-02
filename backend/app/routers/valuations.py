from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Valuation
from app.schemas import ValuationRequest, ValuationResponse, ValuationSummary
from app.valuation import (
    build_football_field,
    run_comparable_company_analysis,
    run_dcf,
    run_precedent_transactions_analysis,
)
from app.valuation.comparables import ComparablesInputError
from app.valuation.dcf import DCFInputError
from app.valuation.precedent import PrecedentInputError

router = APIRouter(prefix="/api/valuations", tags=["valuations"])


@router.post("", response_model=ValuationResponse, status_code=201)
def create_valuation(payload: ValuationRequest, db: Session = Depends(get_db)):
    try:
        dcf_result = run_dcf(
            base_revenue=payload.ltm_revenue,
            revenue_growth_rates=payload.dcf.revenue_growth_rates,
            ebitda_margins=payload.dcf.ebitda_margins,
            tax_rate=payload.dcf.tax_rate,
            capex_pct_revenue=payload.dcf.capex_pct_revenue,
            da_pct_revenue=payload.dcf.da_pct_revenue,
            nwc_pct_revenue_change=payload.dcf.nwc_pct_revenue_change,
            wacc=payload.dcf.wacc,
            terminal_growth_rate=payload.dcf.terminal_growth_rate,
            net_debt=payload.net_debt,
            shares_outstanding=payload.shares_outstanding,
        )
    except DCFInputError as exc:
        raise HTTPException(status_code=422, detail=f"DCF error: {exc}") from exc

    cca_result = None
    if payload.comps:
        try:
            cca_result = run_comparable_company_analysis(
                target_revenue=payload.ltm_revenue,
                target_ebitda=payload.ltm_ebitda,
                net_debt=payload.net_debt,
                shares_outstanding=payload.shares_outstanding,
                comps=[c.model_dump() for c in payload.comps],
            )
        except ComparablesInputError as exc:
            raise HTTPException(status_code=422, detail=f"Comparable company analysis error: {exc}") from exc

    pta_result = None
    if payload.precedent_transactions:
        try:
            pta_result = run_precedent_transactions_analysis(
                target_revenue=payload.ltm_revenue,
                target_ebitda=payload.ltm_ebitda,
                net_debt=payload.net_debt,
                shares_outstanding=payload.shares_outstanding,
                transactions=[t.model_dump() for t in payload.precedent_transactions],
            )
        except PrecedentInputError as exc:
            raise HTTPException(status_code=422, detail=f"Precedent transaction analysis error: {exc}") from exc

    football_field = build_football_field(
        dcf_result=dcf_result,
        cca_result=cca_result,
        pta_result=pta_result,
        offer_price=payload.offer_price,
        current_share_price=payload.current_share_price,
    )

    results = {
        "dcf": dcf_result,
        "comparable_company_analysis": cca_result,
        "precedent_transaction_analysis": pta_result,
        "football_field": football_field,
    }

    valuation = Valuation(
        target_name=payload.target_name,
        acquirer_name=payload.acquirer_name,
        offer_price=payload.offer_price,
        current_share_price=payload.current_share_price,
        consideration_type=payload.consideration_type,
        inputs=payload.model_dump(),
        results=results,
    )
    db.add(valuation)
    db.commit()
    db.refresh(valuation)
    return valuation


@router.get("", response_model=list[ValuationSummary])
def list_valuations(db: Session = Depends(get_db)):
    valuations = db.scalars(select(Valuation).order_by(Valuation.created_at.desc())).all()
    summaries = []
    for v in valuations:
        football_field = (v.results or {}).get("football_field") or {}
        summaries.append(
            ValuationSummary(
                id=v.id,
                target_name=v.target_name,
                acquirer_name=v.acquirer_name,
                offer_price=v.offer_price,
                created_at=v.created_at,
                fairness_support=football_field.get("fairness_support"),
            )
        )
    return summaries


@router.get("/{valuation_id}", response_model=ValuationResponse)
def get_valuation(valuation_id: str, db: Session = Depends(get_db)):
    valuation = db.get(Valuation, valuation_id)
    if not valuation:
        raise HTTPException(status_code=404, detail="Valuation not found")
    return valuation
