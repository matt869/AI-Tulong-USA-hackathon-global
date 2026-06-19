import json
import os
import re
import anthropic
from models.schemas import EligibilityRequest


def load_prompt(language: str) -> str:
    lang = "fil" if language == "fil" else "en"
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", f"input_parser_{lang}.txt")
    with open(prompt_path) as f:
        return f.read()


def parse_free_text(text: str, language: str = "en") -> EligibilityRequest:
    """
    Uses Claude to parse free-form text into a structured EligibilityRequest.
    Falls back to defaults if parsing fails.
    """
    system_prompt = load_prompt(language)
    
    client = anthropic.Anthropic()
    
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=system_prompt,
        messages=[{"role": "user", "content": text}]
    )
    
    raw = message.content[0].text.strip()
    
    # Strip markdown fences if present
    raw = re.sub(r"```json|```", "", raw).strip()
    
    parsed = json.loads(raw)
    
    # Ensure required fields have defaults
    defaults = {
        "age": 30,
        "monthly_income": 5000.0,
        "household_size": 4,
        "employment_status": "unemployed",
        "is_pwd": False,
        "is_senior": False,
        "has_philhealth": False,
        "has_sss": False,
        "location_type": "urban",
        "language": language,
    }
    
    for key, default in defaults.items():
        if key not in parsed or parsed[key] is None:
            parsed[key] = default

    # Auto-detect senior from age
    if parsed.get("age", 0) >= 60:
        parsed["is_senior"] = True

    return EligibilityRequest(**parsed)