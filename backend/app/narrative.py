"""Turns the computed valuation results into a professional fairness-opinion
narrative using the OpenAI API. The model is given the already-computed
numbers (it is explicitly told not to invent or recompute figures) and asked
to write the prose that explains and contextualizes them, the way an
analyst would turn a valuation model into a client-ready opinion letter.
"""

from __future__ import annotations

import json

from openai import OpenAI

from app.config import get_settings

SYSTEM_PROMPT = """You are a senior valuation analyst at an investment bank, drafting a
fairness opinion report for a proposed M&A transaction. You write in the formal, precise
register of a real fairness opinion letter: measured, evidence-based, no hype, no filler.

Rules you must follow:
1. Use ONLY the figures given to you in the JSON payload. Never invent, estimate, or
   recompute a number. If you reference a value, it must come from the payload.
2. Structure the report with these sections, in this order, using markdown headings:
   ## Executive Summary
   ## Transaction Overview
   ## Scope of Review and Methodology
   ## Discounted Cash Flow Analysis
   ## Comparable Company Analysis
   ## Precedent Transaction Analysis
   ## Summary of Implied Valuation Ranges
   ## Conclusion
   ## Qualifications and Limitations
   (Omit a methodology section entirely if its data is null in the payload.)
3. In the Conclusion, state plainly whether the offer price is, in your professional
   judgment, within a range that is fair, from a financial point of view, to the target
   company's shareholders -- based strictly on where the offer price falls relative to
   the implied ranges provided (the payload includes a `fairness_support` field:
   "supports_fairness", "does_not_support_fairness", "mixed", or "insufficient_data" --
   ground your conclusion in this signal and explain why using the actual range data).
4. The "Qualifications and Limitations" section must state, clearly and unambiguously,
   that this report is an AI-generated draft produced for educational/informational and
   internal discussion purposes only, that it has not been prepared, reviewed, or
   approved by a licensed investment bank, financial advisor, or valuation professional,
   that it does not constitute a real fairness opinion under any regulatory or legal
   standard (e.g. Delaware corporate law, SEC rules), and that it must not be relied
   upon by any board, shareholder, or third party in connection with an actual
   transaction, disclosure document, or fiduciary decision without independent
   professional review.
5. Do not add sections beyond the list above. Do not editorialize about the AI process.
   Write as the analyst voice throughout the body of the report; the disclaimer in
   section 9 is the one place you step outside that voice to caveat the document itself.
"""


def _build_user_prompt(payload: dict) -> str:
    return (
        "Draft the fairness opinion report using only the data in this JSON payload. "
        "All monetary values are in the same currency and per-share figures are per "
        "share unless noted otherwise.\n\n"
        f"```json\n{json.dumps(payload, indent=2, default=str)}\n```"
    )


def generate_fairness_opinion_narrative(payload: dict) -> tuple[str, str]:
    """Returns (narrative_markdown, model_used)."""
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured on the backend. Set it in backend/.env to "
            "enable fairness opinion generation."
        )

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(payload)},
        ],
        temperature=0.3,
    )
    narrative = response.choices[0].message.content or ""
    return narrative, settings.openai_model
