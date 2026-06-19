import json
import os
from typing import List, Dict, Any
from models.schemas import EligibilityRequest, ProgramResult


PROGRAMS_DIR = os.path.join(os.path.dirname(__file__), "..", "configs", "programs")


def load_program_config(program_id: str) -> Dict[str, Any]:
    path = os.path.join(PROGRAMS_DIR, f"{program_id}.json")
    with open(path) as f:
        return json.load(f)


def check_4ps_eligibility(req: EligibilityRequest) -> ProgramResult:
    config = load_program_config("4ps")
    gaps = []
    trace = []
    eligible = True
    confidence = 1.0

    income_per_capita = req.monthly_income / max(req.household_size, 1)
    
    if req.monthly_income > 3000:
        eligible = False
        gaps.append(f"Monthly income ₱{req.monthly_income:,.0f} exceeds ₱3,000 threshold")
        confidence -= 0.5
    else:
        trace.append(f"✓ Income ₱{req.monthly_income:,.0f} is within 4Ps threshold")

    if req.household_size < 2:
        eligible = False
        gaps.append("Household must have at least 2 members")
        confidence -= 0.3
    else:
        trace.append(f"✓ Household size of {req.household_size} qualifies")

    if income_per_capita > 1500:
        eligible = False
        gaps.append(f"Income per capita ₱{income_per_capita:,.0f} exceeds ₱1,500 limit")
        confidence -= 0.3

    return ProgramResult(
        program_id="4ps",
        name=config["name"],
        agency=config["agency"],
        eligible=eligible,
        confidence=max(0.0, min(1.0, confidence)),
        gaps=gaps,
        next_steps=config["next_steps"] if eligible else ["Consider applying once household income decreases or family size grows"],
        description=config["description"],
        benefits=config["benefits"],
        office=config["office"],
    )


def check_philhealth_eligibility(req: EligibilityRequest) -> ProgramResult:
    config = load_program_config("philhealth")
    gaps = []
    eligible = True
    confidence = 0.95

    if req.has_philhealth:
        return ProgramResult(
            program_id="philhealth",
            name=config["name"],
            agency=config["agency"],
            eligible=True,
            confidence=1.0,
            gaps=[],
            next_steps=["You are already a PhilHealth member — ensure contributions are up to date"],
            description=config["description"],
            benefits=config["benefits"],
            office=config["office"],
        )

    if req.employment_status == "employed":
        note = "Employer must register you — ask your HR department"
    elif req.employment_status in ["self_employed", "informal"]:
        note = "You can register as a self-paying member"
    else:
        note = "You may qualify as an indigent member (free) if income is below threshold"
        if req.monthly_income > 10000:
            eligible = False
            gaps.append("Income may be too high for indigent PhilHealth — you can still register as voluntary member")
            confidence = 0.7

    return ProgramResult(
        program_id="philhealth",
        name=config["name"],
        agency=config["agency"],
        eligible=eligible,
        confidence=confidence,
        gaps=gaps,
        next_steps=config["next_steps"],
        description=config["description"],
        benefits=config["benefits"],
        office=config["office"],
    )


def check_tupad_eligibility(req: EligibilityRequest) -> ProgramResult:
    config = load_program_config("tupad")
    gaps = []
    eligible = True
    confidence = 1.0

    if req.employment_status == "employed":
        eligible = False
        gaps.append("TUPAD is only for displaced, seasonal, or informal workers — regular employment disqualifies")
        confidence = 0.0

    if req.age < 18:
        eligible = False
        gaps.append("Minimum age for TUPAD is 18 years old")
        confidence -= 0.5

    if req.age > 59:
        eligible = False
        gaps.append("Maximum age for regular TUPAD is 59 (senior programs available through OSCA)")
        confidence -= 0.5

    if req.employment_status in ["unemployed", "informal", "self_employed"] and 18 <= req.age <= 59:
        confidence = 0.85

    return ProgramResult(
        program_id="tupad",
        name=config["name"],
        agency=config["agency"],
        eligible=eligible,
        confidence=max(0.0, confidence),
        gaps=gaps,
        next_steps=config["next_steps"] if eligible else ["Check DOLE Senior Worker programs if 60+"],
        description=config["description"],
        benefits=config["benefits"],
        office=config["office"],
    )


def check_sss_eligibility(req: EligibilityRequest) -> ProgramResult:
    config = load_program_config("sss")
    gaps = []
    eligible = True
    confidence = 0.9

    if req.has_sss:
        return ProgramResult(
            program_id="sss",
            name=config["name"],
            agency=config["agency"],
            eligible=True,
            confidence=1.0,
            gaps=[],
            next_steps=["You are already an SSS member — check your contribution history at my.sss.gov.ph"],
            description=config["description"],
            benefits=config["benefits"],
            office=config["office"],
        )

    if req.age < 18:
        eligible = False
        gaps.append("Minimum age for SSS membership is 18")
        confidence = 0.0
    elif req.age >= 60 and req.is_senior:
        gaps.append("As a senior, you may only claim benefits if you have prior contributions — check retirement eligibility")
        confidence = 0.6

    if req.employment_status == "unemployed" and not req.has_sss:
        gaps.append("Unemployed individuals can register as voluntary members but must have prior employment history for most benefits")
        confidence = 0.6

    return ProgramResult(
        program_id="sss",
        name=config["name"],
        agency=config["agency"],
        eligible=eligible,
        confidence=max(0.0, confidence),
        gaps=gaps,
        next_steps=config["next_steps"],
        description=config["description"],
        benefits=config["benefits"],
        office=config["office"],
    )


def run_all_rules(req: EligibilityRequest) -> List[ProgramResult]:
    results = []
    results.append(check_4ps_eligibility(req))
    results.append(check_philhealth_eligibility(req))
    results.append(check_tupad_eligibility(req))
    results.append(check_sss_eligibility(req))
    return results