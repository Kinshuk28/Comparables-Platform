from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import FairnessOpinion, Valuation
from app.narrative import generate_fairness_opinion_narrative
from app.schemas import FairnessOpinionDetailResponse, FairnessOpinionResponse

router = APIRouter(tags=["opinions"])


def _build_narrative_payload(valuation: Valuation) -> dict:
    return {
        "target_name": valuation.target_name,
        "acquirer_name": valuation.acquirer_name,
        "offer_price": valuation.offer_price,
        "current_share_price": valuation.current_share_price,
        "consideration_type": valuation.consideration_type,
        "shares_outstanding": valuation.inputs.get("shares_outstanding"),
        "net_debt": valuation.inputs.get("net_debt"),
        "ltm_revenue": valuation.inputs.get("ltm_revenue"),
        "ltm_ebitda": valuation.inputs.get("ltm_ebitda"),
        "dcf_assumptions": valuation.inputs.get("dcf"),
        "dcf_results": valuation.results.get("dcf"),
        "comparable_company_analysis": valuation.results.get("comparable_company_analysis"),
        "precedent_transaction_analysis": valuation.results.get("precedent_transaction_analysis"),
        "football_field": valuation.results.get("football_field"),
    }


@router.post("/api/valuations/{valuation_id}/opinion", response_model=FairnessOpinionResponse, status_code=201)
def create_fairness_opinion(valuation_id: str, db: Session = Depends(get_db)):
    valuation = db.get(Valuation, valuation_id)
    if not valuation:
        raise HTTPException(status_code=404, detail="Valuation not found")

    payload = _build_narrative_payload(valuation)
    try:
        narrative, model_used = generate_fairness_opinion_narrative(payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # openai SDK errors, network errors, etc.
        raise HTTPException(status_code=502, detail=f"Failed to generate fairness opinion: {exc}") from exc

    opinion = FairnessOpinion(valuation_id=valuation.id, narrative=narrative, model_used=model_used)
    db.add(opinion)
    db.commit()
    db.refresh(opinion)
    return opinion


@router.get("/api/opinions/{opinion_id}", response_model=FairnessOpinionDetailResponse)
def get_fairness_opinion(opinion_id: str, db: Session = Depends(get_db)):
    opinion = db.get(FairnessOpinion, opinion_id)
    if not opinion:
        raise HTTPException(status_code=404, detail="Fairness opinion not found")
    return opinion


@router.get("/api/opinions", response_model=list[FairnessOpinionResponse])
def list_fairness_opinions(db: Session = Depends(get_db)):
    return db.scalars(select(FairnessOpinion).order_by(FairnessOpinion.created_at.desc())).all()
