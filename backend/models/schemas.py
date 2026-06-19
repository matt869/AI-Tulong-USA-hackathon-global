from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class EligibilityRequest(BaseModel):
    age: int
    monthly_income: float
    household_size: int
    employment_status: str  # employed, unemployed, self_employed, informal
    is_pwd: bool = False
    is_senior: bool = False
    has_philhealth: bool = False
    has_sss: bool = False
    location_type: str = "urban"  # urban, rural
    barangay: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    language: str = "en"  # en, fil


class ProgramResult(BaseModel):
    program_id: str
    name: str
    agency: str
    eligible: bool
    confidence: float
    gaps: List[str] = []
    next_steps: List[str] = []
    description: str
    benefits: str
    office: Optional[str] = None
    ngo_alternatives: List[Dict[str, str]] = []


class ConflictFlag(BaseModel):
    programs: List[str]
    reason: str
    resolution: str


class EligibilityResponse(BaseModel):
    programs: List[ProgramResult]
    conflicts: List[ConflictFlag] = []
    reasoning_trace: List[str] = []
    recommended_path: List[str] = []
    documents_needed: List[str] = []
    language: str = "en"
    
    