from fastapi import APIRouter, HTTPException
from models.schemas import EligibilityRequest, EligibilityResponse
from engines.rules_engine import run_all_rules
from engines.gap_analysis import analyze_gaps, build_reasoning_trace
from engines.conflict_detector import detect_conflicts, get_documents_needed
from engines.ngo_router import route_to_ngos
from services.input_parser import parse_free_text
from services.explainer import generate_explanation
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class FreeTextRequest(BaseModel):
    text: str
    language: str = "en"


class EligibilityResponseWithExplanation(EligibilityResponse):
    explanation: Optional[str] = None


@router.post("/check", response_model=EligibilityResponseWithExplanation)
async def check_eligibility(req: EligibilityRequest):
    """
    Check eligibility given a structured EligibilityRequest.
    """
    try:
        results = run_all_rules(req)
        conflicts = detect_conflicts(req, results)
        gaps = analyze_gaps(req, results)
        reasoning_trace = build_reasoning_trace(req, results)
        documents_needed = get_documents_needed(results)

        # Build recommended path
        eligible_programs = [r for r in results if r.eligible]
        recommended_path = []
        for program in eligible_programs:
            if program.next_steps:
                recommended_path.append(f"{program.name}: {program.next_steps[0]}")

        # Add NGO alternatives to ineligible programs
        ngo_alternatives = route_to_ngos(req, results)
        for result in results:
            if not result.eligible:
                result.ngo_alternatives = ngo_alternatives

        response = EligibilityResponseWithExplanation(
            programs=results,
            conflicts=conflicts,
            reasoning_trace=reasoning_trace + gaps,
            recommended_path=recommended_path,
            documents_needed=documents_needed,
            language=req.language,
        )

        # Generate natural language explanation
        try:
            response.explanation = generate_explanation(response)
        except Exception as e:
            response.explanation = f"Results processed successfully. Check program details below."

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/parse-and-check", response_model=EligibilityResponseWithExplanation)
async def parse_and_check(req: FreeTextRequest):
    """
    Parse free-form text and check eligibility in one step.
    """
    try:
        parsed_req = parse_free_text(req.text, req.language)
        parsed_req.language = req.language
        
        # Reuse the check_eligibility logic
        results = run_all_rules(parsed_req)
        conflicts = detect_conflicts(parsed_req, results)
        gaps = analyze_gaps(parsed_req, results)
        reasoning_trace = build_reasoning_trace(parsed_req, results)
        documents_needed = get_documents_needed(results)

        eligible_programs = [r for r in results if r.eligible]
        recommended_path = []
        for program in eligible_programs:
            if program.next_steps:
                recommended_path.append(f"{program.name}: {program.next_steps[0]}")

        ngo_alternatives = route_to_ngos(parsed_req, results)
        for result in results:
            if not result.eligible:
                result.ngo_alternatives = ngo_alternatives

        response = EligibilityResponseWithExplanation(
            programs=results,
            conflicts=conflicts,
            reasoning_trace=reasoning_trace + gaps,
            recommended_path=recommended_path,
            documents_needed=documents_needed,
            language=req.language,
        )

        try:
            response.explanation = generate_explanation(response)
        except Exception:
            response.explanation = "Results processed. Check program details below."

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))