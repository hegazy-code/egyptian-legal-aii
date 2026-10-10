"""
RAG engine: assembles retrieved legal sources into a grounding context,
calls Google Gemini, and enforces the no-hallucination system prompt.

Answers are always in Arabic and MUST follow the 8-section format (see
app/rag/answer_builder.py for the section headers). The model is explicitly
forbidden from inventing laws, articles, judgments, or citations -- if the
retrieved context is insufficient it must say so rather than guess.
"""
import logging
import time
from typing import Any, Dict, List, Optional

from app.config import settings
from app.schemas.legal import SearchResultItem

logger = logging.getLogger(__name__)

NO_HALLUCINATION_SYSTEM_PROMPT = """\
أنت مساعد قانوني تعليمي متخصص في القانون المصري. مهمتك الإجابة على الأسئلة القانونية
بالاعتماد حصرياً على النصوص القانونية والأحكام القضائية المُرفقة لك في سياق البحث (context).

قواعد صارمة يجب الالتزام بها دائماً:
1. لا تختلق أبداً اسم قانون أو رقم مادة أو رقم حكم قضائي أو أي استشهاد (citation) غير موجود
   فعلياً في السياق المُرفق. الاستشهاد بمصدر غير موجود في السياق يُعد خطأ جسيماً.
2. إذا كان السياق المُرفق لا يحتوي على معلومات كافية للإجابة، صرّح بذلك بوضوح للمستخدم
   بدلاً من التخمين أو الاجتهاد الشخصي.
3. أجب دائماً باللغة العربية الفصحى الواضحة.
4. اتبع دائماً تنسيق الإجابة المكوّن من 8 أقسام كما هو محدد لك في التعليمات.
5. هذه أداة تعليمية/إرشادية فقط ولا تُغني عن استشارة محامٍ مرخّص؛ يجب التنبيه لذلك دائماً
   في القسم الأخير من الإجابة.
6. أعد الإجابة بصيغة JSON حصراً حسب المخطط المطلوب في كل طلب.
"""


class GeminiUnavailableError(Exception):
    """Raised when the Gemini API cannot be reached or is not configured."""


def _get_client():
    """Lazily construct a genai client so import doesn't fail without a key."""
    if not settings.GEMINI_API_KEY:
        raise GeminiUnavailableError("GEMINI_API_KEY is not configured.")
    from google import genai

    return genai.Client(api_key=settings.GEMINI_API_KEY)


def call_gemini_with_retry(
    contents: str,
    system_instruction: str,
    response_mime_type: str = "application/json",
    max_output_tokens: int = 2048,
    model: Optional[str] = None,
) -> str:
    """
    Calls Gemini via google-genai, retrying once after a short sleep if the
    API responds with 429 (rate limited) or 503 (overloaded).

    Returns the raw text of the model's response. Raises GeminiUnavailableError
    if the API key isn't configured or both attempts fail.
    """
    from google.genai import types
    from google.genai import errors as genai_errors

    client = _get_client()
    model_name = model or settings.GEMINI_MODEL

    attempts = 0
    last_error: Optional[Exception] = None
    while attempts < 2:
        attempts += 1
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type=response_mime_type,
                    max_output_tokens=max_output_tokens,
                ),
            )
            return response.text or ""
        except genai_errors.APIError as exc:  # type: ignore[attr-defined]
            last_error = exc
            code = getattr(exc, "code", None)
            if code in (429, 503) and attempts < 2:
                logger.warning("Gemini APIError %s, retrying once after backoff...", code)
                time.sleep(2)
                continue
            raise GeminiUnavailableError(f"Gemini API call failed: {exc}") from exc
        except Exception as exc:  # pragma: no cover - defensive
            last_error = exc
            raise GeminiUnavailableError(f"Gemini API call failed: {exc}") from exc

    raise GeminiUnavailableError(f"Gemini API call failed after retries: {last_error}")


def build_context_block(results: List[SearchResultItem]) -> str:
    """Renders retrieved search results into a labeled context block for the prompt."""
    if not results:
        return "لا توجد نتائج بحث ذات صلة في قاعدة البيانات الحالية."
    lines = []
    for idx, r in enumerate(results, start=1):
        lines.append(f"[مصدر {idx}] النوع: {r.result_type} | العنوان: {r.title}\nالنص: {r.snippet}")
    return "\n\n".join(lines)


def generate_answer(
    question: str,
    context_results: List[SearchResultItem],
    analysis: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Calls Gemini to produce the final answer text (already formatted per the
    8-section structure by the prompt itself; app/rag/answer_builder.py can
    additionally normalize/validate the structure before it's returned to
    the user).
    """
    context_block = build_context_block(context_results)
    analysis_block = ""
    if analysis:
        analysis_block = f"\nتحليل أولي للسؤال (JSON): {analysis}\n"

    prompt = f"""سؤال المستخدم:
{question}
{analysis_block}
سياق البحث (المصادر القانونية المسترجعة فقط -- لا تستخدم أي معلومة من خارج هذا السياق):
{context_block}

المطلوب: أجب في صيغة JSON بالشكل التالي فقط:
{{"answer_markdown": "<نص الإجابة الكامل منسقاً بصيغة Markdown يتبع الأقسام الثمانية بالترتيب>"}}
"""
    raw = call_gemini_with_retry(
        contents=prompt,
        system_instruction=NO_HALLUCINATION_SYSTEM_PROMPT,
        response_mime_type="application/json",
        max_output_tokens=3072,
    )
    return raw
