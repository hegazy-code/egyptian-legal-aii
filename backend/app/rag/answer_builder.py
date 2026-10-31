"""
Parses and builds the structured Arabic legal answer (8-section JSON dict).

All public functions return a plain Python dict whose keys match LegalAnswerOut
(see app/schemas/chat.py). The dict is passed directly to LegalAnswerOut(**dict)
in the API layer, so every key must be present and correctly typed.
"""
import json
import logging
from typing import Any, Dict, List, Optional

from app.schemas.legal import SearchResultItem

logger = logging.getLogger(__name__)

_DISCLAIMER = (
    "هذه الإجابة لأغراض تعليمية وإرشادية فقط ولا تُغني عن استشارة محامٍ مختص "
    "مرخّص له بمزاولة المهنة."
)

_EMPTY_ANSWER: Dict[str, Any] = {
    "understandingOfQuestion": "",
    "legalDomain": "غير محدد",
    "relevantLegalTexts": [],
    "explanation": "",
    "preliminaryApplication": "",
    "missingInformation": [],
    "possibleProcedures": [],
    "answerSources": [],
    "disclaimer": _DISCLAIMER,
}


def parse_gemini_answer(raw_response: str) -> Dict[str, Any]:
    """
    Parse the structured JSON dict from Gemini's response.

    The engine prompts Gemini to return JSON with exactly the 8 LegalAnswerOut
    fields. This function extracts and validates that dict, falling back to a
    safe skeleton when the response can't be parsed.
    """
    try:
        data = json.loads(raw_response)
        if isinstance(data, dict) and any(
            k in data for k in ("understandingOfQuestion", "explanation", "legalDomain")
        ):
            # Fill any missing optional keys with safe defaults.
            result = dict(_EMPTY_ANSWER)
            result.update(data)
            return result
    except (json.JSONDecodeError, AttributeError, TypeError) as exc:
        logger.warning("answer_builder: failed to parse Gemini JSON: %s", exc)

    # If it's not structured JSON, wrap the raw text in the explanation field.
    result = dict(_EMPTY_ANSWER)
    result["explanation"] = raw_response.strip() if raw_response else "تعذر توليد إجابة."
    return result


def build_fallback_answer(
    question: str,
    analysis: Optional[Dict[str, Any]],
    context_results: List[SearchResultItem],
    note: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Deterministically assembles a valid 8-section answer dict without calling
    any model -- used when Gemini is unavailable so the endpoint still returns
    a well-formed, non-fabricated reply.
    """
    analysis = analysis or {}
    legal_area = analysis.get("legal_area", "غير محدد")
    missing_info: List[str] = analysis.get("missing_info") or []

    answer_sources = [
        {
            "id": r.id or "",
            "lawName": r.title or "",
            "articleNumber": None,
            "kind": "other",
            "status": "current",
            "excerpt": (r.snippet or "")[:300],
            "basis": "ai_inference",
        }
        for r in context_results
    ]

    return {
        "understandingOfQuestion": question or "لم يتم استلام سؤال واضح.",
        "legalDomain": legal_area,
        "relevantLegalTexts": [],
        "explanation": (
            note
            or "خدمة الذكاء الاصطناعي غير متاحة حالياً. يرجى إعادة المحاولة لاحقاً."
        ),
        "preliminaryApplication": (
            "لا يمكن تقديم تطبيق مبدئي موثوق دون نصوص قانونية مسترجعة كافية."
        ),
        "missingInformation": (
            missing_info if missing_info else ["يرجى تزويدنا بمزيد من تفاصيل الواقعة."]
        ),
        "possibleProcedures": [
            "يُنصح باستشارة محامٍ مختص لتحديد الإجراءات القانونية المناسبة لحالتك."
        ],
        "answerSources": answer_sources,
        "disclaimer": _DISCLAIMER,
    }
