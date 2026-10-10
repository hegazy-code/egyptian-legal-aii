"""
Formats the final Arabic answer in the required 8-section structure:

1. فهم سؤالك              (Understanding your question)
2. المجال القانوني         (Legal area)
3. النصوص القانونية ذات الصلة (Relevant legal texts)
4. الشرح                   (Explanation)
5. تطبيق مبدئي على الوقائع  (Preliminary application to the facts)
6. معلومات ناقصة           (Missing information)
7. الإجراءات المحتملة       (Possible procedures)
8. مصادر الإجابة           (Answer sources)
9. تنبيه                   (Disclaimer)  -- kept as the closing safety notice

Gemini is prompted (see app/rag/engine.py) to return the fully formatted
Markdown answer directly as JSON: {"answer_markdown": "..."}. This module
parses that response and, as a safety net, assembles a valid 8-section
answer from raw pieces if the model response can't be parsed -- so callers
never get a blank or malformed reply even when the model output is off-spec.
"""
import json
import logging
from typing import Any, Dict, List, Optional

from app.schemas.legal import SearchResultItem

logger = logging.getLogger(__name__)

SECTION_HEADERS = [
    "فهم سؤالك",
    "المجال القانوني",
    "النصوص القانونية ذات الصلة",
    "الشرح",
    "تطبيق مبدئي على الوقائع",
    "معلومات ناقصة",
    "الإجراءات المحتملة",
    "مصادر الإجابة",
    "تنبيه",
]

DISCLAIMER_TEXT = (
    "هذه الإجابة لأغراض تعليمية وإرشادية فقط ولا تُغني عن استشارة محامٍ مختص مرخّص له "
    "بمزاولة المهنة، خاصة في الوقائع الدقيقة لحالتك."
)


def parse_gemini_answer(raw_response: str) -> str:
    """Extract answer_markdown from the model's JSON response, or fall back gracefully."""
    try:
        data = json.loads(raw_response)
        text = data.get("answer_markdown")
        if isinstance(text, str) and text.strip():
            return text.strip()
    except (json.JSONDecodeError, AttributeError, TypeError):
        pass
    # Fall back: if it's not valid JSON, the raw text might still be usable
    # (e.g. the model ignored the JSON instruction) -- use it as-is.
    if raw_response and raw_response.strip():
        return raw_response.strip()
    return build_fallback_answer(
        question="",
        analysis={},
        context_results=[],
        note="تعذر توليد إجابة من نموذج الذكاء الاصطناعي.",
    )


def build_fallback_answer(
    question: str,
    analysis: Optional[Dict[str, Any]],
    context_results: List[SearchResultItem],
    note: Optional[str] = None,
) -> str:
    """
    Deterministically assembles a valid 8-section answer without calling the
    model -- used when Gemini is unavailable (no API key, network error,
    etc.) so the endpoint still returns a well-formed, non-fabricated reply.
    """
    analysis = analysis or {}
    legal_area = analysis.get("legal_area", "غير محدد")
    missing_info = analysis.get("missing_info") or []

    sources_lines = (
        "\n".join(f"- {r.title}" for r in context_results)
        if context_results
        else "- لا توجد مصادر مسترجعة من قاعدة البيانات الحالية لهذا السؤال."
    )

    body = f"""### {SECTION_HEADERS[0]}
{question or 'لم يتم استلام سؤال واضح.'}

### {SECTION_HEADERS[1]}
{legal_area}

### {SECTION_HEADERS[2]}
{sources_lines}

### {SECTION_HEADERS[3]}
{note or 'تعذر توليد شرح تفصيلي تلقائياً في الوقت الحالي (خدمة الذكاء الاصطناعي غير متاحة أو لم يتم العثور على نصوص قانونية كافية). يرجى إعادة صياغة السؤال أو المحاولة لاحقاً.'}

### {SECTION_HEADERS[4]}
لا يمكن تقديم تطبيق مبدئي موثوق دون نصوص قانونية مسترجعة كافية.

### {SECTION_HEADERS[5]}
{chr(10).join(f'- {m}' for m in missing_info) if missing_info else '- يرجى تزويدنا بمزيد من تفاصيل الواقعة.'}

### {SECTION_HEADERS[6]}
يُنصح باستشارة محامٍ مختص لتحديد الإجراءات القانونية المناسبة لحالتك.

### {SECTION_HEADERS[7]}
{sources_lines}

### {SECTION_HEADERS[8]}
{DISCLAIMER_TEXT}
"""
    return body
