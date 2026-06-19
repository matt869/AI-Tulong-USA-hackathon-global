import json
import os
from typing import List, Dict, Any
from models.schemas import EligibilityRequest, ProgramResult


NGO_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "configs", "ngo_database.json")


def load_ngos() -> List[Dict[str, Any]]:
    with open(NGO_DB_PATH) as f:
        return json.load(f)["ngos"]


def route_to_ngos(req: EligibilityRequest, results: List[ProgramResult]) -> List[Dict[str, str]]:
    """
    Returns relevant NGO alternatives based on profile and eligibility gaps.
    """
    ngos = load_ngos()
    relevant = []
    eligible_programs = [r.program_id for r in results if r.eligible]

    needed_focus = set()

    # If no health coverage
    if not req.has_philhealth and "philhealth" not in eligible_programs:
        needed_focus.add("health")

    # If no income support
    if req.employment_status in ["unemployed", "informal"] and "tupad" not in eligible_programs:
        needed_focus.add("livelihood")

    # If PWD
    if req.is_pwd:
        needed_focus.add("pwd")

    # If no social protection
    if not req.has_sss and "sss" not in eligible_programs:
        needed_focus.add("social_protection")

    # Default: always suggest livelihood and community
    needed_focus.update(["community"])

    for ngo in ngos:
        ngo_focus = set(ngo.get("focus", []))
        if ngo_focus & needed_focus:
            relevant.append({
                "name": ngo["name"],
                "description": ngo["description"],
                "contact": ngo.get("contact", ""),
                "website": ngo.get("website", ""),
            })
            if len(relevant) >= 3:
                break

    return relevant