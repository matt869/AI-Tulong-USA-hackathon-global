import json
import os
from typing import List
from models.schemas import EligibilityRequest, ProgramResult, ConflictFlag


CONFLICTS_PATH = os.path.join(os.path.dirname(__file__), "..", "configs", "conflicts.json")


def load_conflicts():
    with open(CONFLICTS_PATH) as f:
        return json.load(f)["conflicts"]


def detect_conflicts(req: EligibilityRequest, results: List[ProgramResult]) -> List[ConflictFlag]:
    """
    Detects conflicts between programs the user is eligible for,
    or between user's current status and program rules.
    """
    flags = []
    eligible_ids = {r.program_id for r in results if r.eligible}
    
    # 4Ps + TUPAD conflict for active beneficiaries
    if "4ps" in eligible_ids and "tupad" in eligible_ids:
        flags.append(ConflictFlag(
            programs=["4ps", "tupad"],
            reason="Both 4Ps and TUPAD can technically be accessed, but LGUs often prioritize TUPAD slots for non-4Ps households.",
            resolution="Secure your 4Ps enrollment first, then apply for TUPAD during displacement periods. Inform both offices of your dual status."
        ))

    # Employed person trying to access TUPAD
    if req.employment_status == "employed":
        tupad = next((r for r in results if r.program_id == "tupad"), None)
        if tupad and tupad.eligible:
            flags.append(ConflictFlag(
                programs=["tupad"],
                reason="TUPAD is restricted to displaced/informal workers. Formal employment may disqualify you.",
                resolution="Apply for TUPAD only after verified displacement. Keep separation documents."
            ))

    return flags


def get_documents_needed(results: List[ProgramResult]) -> List[str]:
    """
    Aggregates and deduplicates all documents needed across eligible programs.
    """
    seen = set()
    docs = []

    for result in results:
        if result.eligible:
            program_config_path = os.path.join(
                os.path.dirname(__file__), "..", "configs", "programs", f"{result.program_id}.json"
            )
            try:
                with open(program_config_path) as f:
                    config = json.load(f)
                    for doc in config.get("documents", []):
                        normalized = doc.strip().lower()
                        if normalized not in seen:
                            seen.add(normalized)
                            docs.append(doc)
            except FileNotFoundError:
                continue

    return docs