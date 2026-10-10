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


# When Google rejects the search-grounded call (e.g. free-tier quota), skip search for a while
# so users don't pay the extra latency on every question.
_search_disabled_until = 0.0
_SEARCH_COOLDOWN_SECONDS = 600


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
    use_search: bool = False,
    sources_out: Optional[List[Dict[str, str]]] = None,
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
                config=_build_config(types, system_instruction, response_mime_type, max_output_tokens, use_search),
            )
            if use_search and sources_out is not None:
                sources_out.extend(_extract_web_sources(response))
            return response.text or ""
        except genai_errors.APIError as exc:  # type: ignore[attr-defined]
            last_error = exc
            code = getattr(exc, "code", None)
            if code in (429, 503) and attempts < 2 and not (use_search and code == 429):
                logger.warning("Gemini APIError %s, retrying once after backoff...", code)
                time.sleep(2)
                continue
            raise GeminiUnavailableError(f"Gemini API call failed: {exc}") from exc
        except Exception as exc:  # pragma: no cover - defensive
            last_error = exc
            raise GeminiUnavailableError(f"Gemini API call failed: {exc}") from exc

    raise GeminiUnavailableError(f"Gemini API call failed after retries: {last_error}")


def _build_config(types, system_instruction, response_mime_type, max_output_tokens, use_search):
    """Google Search grounding can't be combined with forced-JSON output, so the
    mime type is only set when search is off."""
    kwargs = dict(system_instruction=system_instruction, max_output_tokens=max_output_tokens)
    if use_search:
        kwargs["tools"] = [types.Tool(google_search=types.GoogleSearch())]
    else:
        kwargs["response_mime_type"] = response_mime_type
    return types.GenerateContentConfig(**kwargs)


def _extract_web_sources(response) -> List[Dict[str, str]]:
    """Pull the web pages Gemini used (title + url) out of the grounding metadata."""
    found: List[Dict[str, str]] = []
    try:
        meta = response.candidates[0].grounding_metadata
        for chunk in (meta.grounding_chunks or []):
            web = getattr(chunk, "web", None)
            if web and getattr(web, "uri", None):
                found.append({"title": getattr(web, "title", "") or web.uri, "uri": web.uri})
    except (AttributeError, IndexError, TypeError):
        pass
    return found


def build_context_block(results: List[SearchResultItem]) -> str:
    """Renders retrieved search results into a labeled context block for the prompt."""
    if not results:
        return "لا توجد نتائج بحث ذات صلة في قاعدة البيانات الحالية."
    lines = []
    for idx, r in enumerate(results, start=1):
        lines.append(f"[مصدر {idx}] النوع: {r.result_type} | العنوان: {r.title}\nالنص: {r.snippet}")
    return "\n\n".join(lines)


HYBRID_SYSTEM_PROMPT = """\
أنت مساعد قانوني متخصص في القانون المصري يخدم عملاء عاديين. هدفك أن يحصل العميل على إجابة
مفيدة وعملية في أي مسألة قانونية مصرية، تشمل دائماً الخطوات العملية التي يجب أن يتبعها.

القواعد:
1. اعتمد أولاً على المصادر المُرفقة في سياق البحث إن وُجدت، ثم على نتائج البحث على الإنترنت
   (يُفضّل المصادر الرسمية: الجريدة الرسمية، المحكمة الدستورية، وزارة العدل، البوابة القانونية)،
   ثم على معرفتك العامة بالقانون المصري.
2. لا تختلق أبداً رقم مادة أو رقم قانون أو رقم حكم. اذكر رقم المادة أو القانون فقط إذا كنت
   متأكداً منه؛ وإلا صِف الحكم بصيغة عامة (مثل: "يجرّم قانون العقوبات السرقة ...").
3. بيّن بوضوح ما هو مؤكد من مصدر وما هو معلومة عامة تحتاج إلى تحقق؛ ولا تُظهر تأكيداً زائداً.
4. أجب بالعربية الفصحى المبسطة، بلغة يفهمها غير المتخصص.
5. في "الإجراءات المحتملة" اذكر خطوات عملية مرتبة: ماذا يفعل العميل أولاً، المستندات اللازمة،
   الجهة المختصة (نيابة، محكمة، شهر عقاري، مكتب العمل... إلخ)، والمهل الزمنية إن كانت معروفة.
6. اختم دائماً بقسم تنبيه يذكر أن الإجابة إرشادية وليست استشارة قانونية.
7. أجب بصيغة Markdown فقط (بدون JSON) وبالأقسام التسعة التالية بالترتيب، وكل عنوان على سطر مستقل
   بالصيغة المحددة، ومحتوى كل قسم في الأسطر التي تليه:
### 1. فهم سؤالك
### 2. المجال القانوني
### 3. النصوص القانونية ذات الصلة
### 4. الشرح
### 5. تطبيق مبدئي على الوقائع
### 6. معلومات ناقصة
### 7. الإجراءات المحتملة
### 8. مصادر الإجابة
### 9. تنبيه
"""


def _insert_before_disclaimer(markdown: str, extra: str) -> str:
    """Put extra lines at the end of section 8, i.e. just before the disclaimer heading."""
    import re

    matches = list(re.finditer(r"\n#+\s*(?:\d+\.\s*)?تنبيه", markdown))
    if matches:
        at = matches[-1].start()
        return markdown[:at] + "\n" + extra + "\n" + markdown[at:]
    return markdown + "\n\n" + extra


def generate_answer(
    question: str,
    context_results: List[SearchResultItem],
    analysis: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Produces the final answer. Primary path: Gemini with Google Search grounding plus
    any retrieved database sources, returned as Markdown in the 8-section format. If that call
    is refused, retries without search (model knowledge only); as a last resort uses the strict JSON, context-only call.
    """
    context_block = build_context_block(context_results)
    analysis_block = f"\nتحليل أولي للسؤال: {analysis}\n" if analysis else ""

    prompt = f"""سؤال العميل:
{question}
{analysis_block}
مصادر من قاعدة البيانات الداخلية (إن وُجدت، ولها الأولوية):
{context_block}

أجب الآن بالأقسام التسعة المطلوبة."""
    global _search_disabled_until
    for use_search in (True, False):
        if use_search and time.time() < _search_disabled_until:
            continue
        web_sources: List[Dict[str, str]] = []
        try:
            text = call_gemini_with_retry(
                contents=prompt,
                system_instruction=HYBRID_SYSTEM_PROMPT,
                response_mime_type="text/plain",
                max_output_tokens=4096,
                use_search=use_search,
                sources_out=web_sources,
            )
        except GeminiUnavailableError as exc:
            logger.warning("Hybrid answer failed (search=%s): %s", use_search, exc)
            if use_search:
                _search_disabled_until = time.time() + _SEARCH_COOLDOWN_SECONDS
            continue
        if text and text.strip():
            if web_sources:
                seen, lines = set(), []
                for src in web_sources:
                    if src["uri"] not in seen:
                        seen.add(src["uri"])
                        lines.append(f"- {src['title']}: {src['uri']}")
                text = _insert_before_disclaimer(text, "\n".join(lines[:6]))
            return text

    return _generate_strict_answer(question, context_block, analysis_block)


def _generate_strict_answer(question: str, context_block: str, analysis_block: str) -> str:
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
