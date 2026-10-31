"""
Question-understanding step of the RAG pipeline (mirrors the "analyzer" of
the 5-agent pattern: analyzer -> search -> rag -> answer_builder -> [critic,
future]). Extracts a structured JSON summary of the user's question via
Gemini: legal_area, facts, dates, missing_info.
"""
import json
import logging
from typing import Any, Dict

from app.rag.engine import GeminiUnavailableError, call_gemini_with_retry

logger = logging.getLogger(__name__)

ANALYZER_SYSTEM_PROMPT = """\
أنت محلل أسئلة قانونية للقانون المصري. مهمتك الوحيدة هي قراءة سؤال المستخدم واستخراج
معلومات منظمة عنه بصيغة JSON فقط، دون أي إجابة قانونية أو استنتاج قانوني. لا تخترع وقائع
لم يذكرها المستخدم صراحة.
"""

_ANALYZER_SCHEMA_INSTRUCTIONS = """أعد النتيجة بصيغة JSON فقط بالمخطط التالي بالضبط:
{
  "legal_area": "<المجال القانوني الأقرب للسؤال، مثل: قانون مدني، قانون جنائي، قانون عمل...>",
  "facts": ["<وقائع صريحة مذكورة في السؤال>"],
  "dates": ["<أي تواريخ مذكورة في السؤال>"],
  "missing_info": ["<معلومات ناقصة قد تلزم لإجابة أدق>"]
}"""

_DEFAULT_ANALYSIS: Dict[str, Any] = {
    "legal_area": "غير محدد",
    "facts": [],
    "dates": [],
    "missing_info": ["تعذر تحليل السؤال آلياً -- يرجى إضافة تفاصيل إضافية."],
}


def analyze_question(question: str) -> Dict[str, Any]:
    """
    Returns a dict with keys: legal_area, facts, dates, missing_info.
    Falls back to a safe default (and logs a warning) if Gemini is not
    configured or the call/parse fails -- callers should treat this as
    best-effort, not a hard dependency.
    """
    prompt = f"سؤال المستخدم:\n{question}\n\n{_ANALYZER_SCHEMA_INSTRUCTIONS}"
    try:
        raw = call_gemini_with_retry(
            contents=prompt,
            system_instruction=ANALYZER_SYSTEM_PROMPT,
            response_mime_type="application/json",
            max_output_tokens=512,
        )
        data = json.loads(raw)
        # Make sure required keys always exist even if the model omits one.
        for key in ("legal_area", "facts", "dates", "missing_info"):
            data.setdefault(key, _DEFAULT_ANALYSIS[key])
        return data
    except GeminiUnavailableError as exc:
        logger.warning("Analyzer: Gemini unavailable, using default analysis: %s", exc)
        return dict(_DEFAULT_ANALYSIS)
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        logger.warning("Analyzer: failed to parse Gemini JSON response: %s", exc)
        return dict(_DEFAULT_ANALYSIS)
