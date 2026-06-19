import os
import anthropic
from models.schemas import EligibilityResponse


def load_prompt(language: str) -> str:
    lang = "fil" if language == "fil" else "en"
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", f"explainer_{lang}.txt")
    with open(prompt_path) as f:
        return f.read()


def generate_explanation(response: EligibilityResponse) -> str:
    """
    Uses Claude to generate a human-friendly explanation of eligibility results.
    """
    system_prompt = load_prompt(response.language)
    
    # Build structured summary for Claude to explain
    eligible = [p for p in response.programs if p.eligible]
    ineligible = [p for p in response.programs if not p.eligible]
    
    summary = {
        "eligible_programs": [
            {
                "name": p.name,
                "benefits": p.benefits,
                "next_steps": p.next_steps[:2]
            }
            for p in eligible
        ],
        "ineligible_programs": [
            {
                "name": p.name,
                "reasons": p.gaps
            }
            for p in ineligible
        ],
        "conflicts": [
            {
                "programs": c.programs,
                "resolution": c.resolution
            }
            for c in response.conflicts
        ],
        "documents_needed": response.documents_needed[:5],
    }
    
    import json
    user_message = f"Please explain these eligibility results to the applicant:\n\n{json.dumps(summary, indent=2)}"
    
    client = anthropic.Anthropic()
    
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    
    return message.content[0].text.strip()