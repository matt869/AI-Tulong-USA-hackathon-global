from typing import List
from models.schemas import EligibilityRequest, ProgramResult


def analyze_gaps(req: EligibilityRequest, results: List[ProgramResult]) -> List[str]:
    """
    Identifies systemic gaps in coverage — programs the person isn't enrolled in
    but should consider, and structural barriers.
    """
    gaps = []
    eligible_programs = [r for r in results if r.eligible]
    ineligible_programs = [r for r in results if not r.eligible]

    # No programs found eligible
    if not eligible_programs:
        gaps.append("No standard government programs matched your current profile. NGO support may be available.")

    # Not covered by health insurance
    philhealth_result = next((r for r in results if r.program_id == "philhealth"), None)
    if philhealth_result and not philhealth_result.eligible and not req.has_philhealth:
        gaps.append("You currently have no health insurance coverage — a medical emergency could be financially devastating.")

    # Senior without programs
    if req.is_senior and req.age >= 60:
        gaps.append("As a senior citizen, you may also qualify for OSCA (Office for Senior Citizens Affairs) benefits — check with your LGU.")

    # PWD without mention of PWD ID
    if req.is_pwd:
        gaps.append("As a PWD, you are entitled to a PWD ID which grants 20% discount on medicines, medical services, and more — if you don't have one, visit your MSWD.")

    # Household too large and poor but no 4Ps
    four_ps = next((r for r in results if r.program_id == "4ps"), None)
    if four_ps and not four_ps.eligible and req.household_size >= 5 and req.monthly_income < 8000:
        gaps.append("With a large household and low income, you may still want to ask your MSWDO to re-assess using the Listahanan database.")

    # Informal worker with no SSS
    sss_result = next((r for r in results if r.program_id == "sss"), None)
    if req.employment_status == "informal" and sss_result and not req.has_sss:
        gaps.append("As an informal worker, voluntary SSS membership protects you against sickness, maternity, and disability — consider enrolling even at low contribution rates.")

    return gaps


def build_reasoning_trace(req: EligibilityRequest, results: List[ProgramResult]) -> List[str]:
    """
    Builds a human-readable audit trail of how eligibility was determined.
    """
    trace = []
    trace.append(f"Profile: Age {req.age}, ₱{req.monthly_income:,.0f}/month, {req.household_size}-person household")
    trace.append(f"Employment: {req.employment_status.replace('_', ' ').title()}")
    
    income_per_capita = req.monthly_income / max(req.household_size, 1)
    trace.append(f"Income per capita: ₱{income_per_capita:,.0f}/month")

    if req.is_pwd:
        trace.append("PWD status: Yes")
    if req.is_senior:
        trace.append("Senior citizen: Yes (60+)")
    if req.has_philhealth:
        trace.append("Existing PhilHealth: Yes")
    if req.has_sss:
        trace.append("Existing SSS: Yes")

    trace.append("---")

    for result in results:
        status = "✅ ELIGIBLE" if result.eligible else "❌ NOT ELIGIBLE"
        trace.append(f"{result.name}: {status} (confidence: {result.confidence:.0%})")
        for gap in result.gaps:
            trace.append(f"  • {gap}")

    return trace