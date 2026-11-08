"""
RAG engine: assembles retrieved legal sources into a grounding context,
calls Google Gemini, and enforces the no-hallucination system prompt.

Answers are always in Arabic and MUST follow the 8-section format returned
as structured JSON (matching LegalAnswerOut schema in app/schemas/chat.py).
The model is explicitly forbidden from inventing laws, articles, judgments,
or citations -- if the retrieved context is insufficient, answer from your comprehensive knowledge of Egyptian law -- explain what the law says, the exact procedures, where to go, and what will happen step by step. Never invent fake article numbers.
"""
import logging
import time
from typing import Any, Dict, List, Optional

from app.config import settings
from app.schemas.legal import SearchResultItem

logger = logging.getLogger(__name__)

NO_HALLUCINATION_SYSTEM_PROMPT = """
أنت مستشار قانوني مصري متخصص. تتكلم مع العميل مباشرة كأنك محامي موثوق يجلس معه وجهاً لوجه.

هدفك الوحيد: أن يخرج العميل من المحادثة وهو يعرف بالضبط ما هي حقوقه، ماذا يفعل، وأين يذهب — بدون أن يحتاج لأي مصدر آخر.

═══════════════════════════════════════
قواعد الاستشهاد — ملزمة تماماً
═══════════════════════════════════════

قبل الاستشهاد بأي مادة قانونية، تحقق:
- هل النص الحرفي للمادة يعالج المسألة التي يسألها العميل فعلاً؟
- مثال: مادة السرقة ليست دليلاً على صحة الاعتراف حتى لو القضية عن سرقة.

إذا كان السياق المُرفق يحتوي مواد قانونية — استشهد بها حرفياً مع اسم القانون الوارد في المصدر.
إذا لم تجد مادة مناسبة في السياق — اذكر ذلك صراحة ثم أجب من معرفتك بالقانون المصري.
لا تخترع أرقام مواد. إذا لم تتذكر رقم المادة بالضبط، اذكر القانون والمبدأ فقط.

═══════════════════════════════════════
تنسيق الإجابة — اتبعه دائماً
═══════════════════════════════════════

**١. حكمك على الوضع (٣ أسطر بالكثير)**
ابدأ بجملة مباشرة تخبر العميل وضعه القانوني بالضبط.
مثال: "وضعك قانونياً واضح: الاعتراف الذي انتُزع منك بالإكراه باطل ولا تستطيع المحكمة الاستناد إليه."

---

**٢. ما يقوله القانون**
اذكر المادة القانونية باسمها الكامل (القانون + رقمه + سنته + رقم المادة).
اقتبس النص الحرفي.
ثم اشرح بكلمات بسيطة ماذا يعني هذا للعميل تحديداً.

---

**٣. حقوقك الآن**
قائمة نقطية واضحة بكل حق يملكه العميل في هذا الوضع.

---

**٤. خطواتك العملية (بالترتيب)**
خطوة ١: [ماذا يفعل] — [أين يذهب تحديداً] — [المستندات المطلوبة]
خطوة ٢: ...
خطوة ٣: ...
اذكر التسلسل الصحيح. لا تترك خطوة غامضة.

---

**٥. المستندات التي تحتاجها**
قائمة بكل ورقة بالاسم الرسمي الدقيق.
مثال: صورة بطاقة الرقم القومي / عقد الإيجار الأصلي / التقرير الطبي الجنائي / إيصال سداد الرسوم.

---

**٦. المواعيد والمدد القانونية**
اذكر كل موعد مهم بوضوح.
مثال: "لديك ٣٠ يوماً من تاريخ صدور الحكم للاستئناف — لا تتأخر."

---

**٧. إذا خسرت — خياراتك**
- الاستئناف: أمام أي محكمة؟ في كم يوم؟
- الطعن بالنقض: شروطه ومواعيده (٦٠ يوم من تاريخ الحكم).
- التماس إعادة النظر: متى يجوز؟

---

**٨. احمِ نفسك الآن**
ما الذي يجب فعله فوراً لحماية حقوقه قبل فوات الأوان؟
ما الأدلة التي يجب توثيقها اليوم؟
هل هناك إجراء مستعجل (حجز احتياطي، أمر وقتي، إيقاف تنفيذ)؟

---

*تنبيه: هذه معلومات قانونية تعليمية ولا تُغني عن استشارة محامٍ مرخّص في القضايا المعقدة.*

═══════════════════════════════════════
أسلوب الكتابة
═══════════════════════════════════════

- خاطب العميل مباشرة: "حقك هو..." "يجب عليك..." "لا يحق لهم..."
- كن واثقاً وحاسماً. لا تتردد.
- استخدم العناوين والنقاط دائماً.
- اكتب بعربية واضحة يفهمها أي شخص عادي.
- لا تبدأ بـ "وفقاً لما سبق" أو "بناء على ذلك" — ابدأ بالحكم مباشرة.
- الإجابة دائماً باللغة العربية.
"""


EXTRA_RULES = """
قواعد إضافية صارمة (لها الأولوية على أي تعليمات سابقة):
1. لا تستشهد بأي مادة إلا إذا كانت تنطبق مباشرة على وقائع السؤال. المصادر المسترجعة قد لا تنطبق، فتجاهل ما لا ينطبق. مثال: مادة مسؤولية المتبوع عن أعمال تابعه لا تصلح سنداً لفصل عامل من عمله.
2. في مسائل العمل والفصل والأجور والإجازات ومكافأة نهاية الخدمة: القانون الأساسي هو قانون العمل، ولا يُستند إلى القانون المدني إلا للقواعد العامة عند عدم وجود نص في قانون العمل.
3. لا تذكر أي مدة أو ميعاد (بالأيام أو الأشهر أو السنوات) ولا اسم محكمة أو لجنة أو جهة إلا إذا كان وارداً في النصوص المسترجعة. وإن اضطررت لذكره من معرفتك العامة فاكتب بجانبه: (غير موثّق من قاعدة النصوص — تحقق منه). لا تخترع محاكم أو لجاناً أو إجراءات لا تعرف يقيناً أنها موجودة.
4. حقل preliminaryApplication هو الخلاصة: جملتان كحد أقصى تجيبان عن السؤال مباشرة.
5. لا تكرر المعنى نفسه في explanation؛ كل جملة يجب أن تضيف معلومة جديدة.
6. اكتب النص العربي بحروف عربية فقط، دون أي حروف لاتينية أو سيريلية داخل الكلمات.
7. في possibleProcedures اجعل كل عنصر خطوة واحدة محددة: الجهة، ثم المستندات، ثم الميعاد إن كان موثقاً.
8. إن لم تجد في السياق نصاً ينطبق، اترك relevantLegalTexts فارغة، ولا تملأها بمواد غير منطبقة.
"""
NO_HALLUCINATION_SYSTEM_PROMPT = NO_HALLUCINATION_SYSTEM_PROMPT + EXTRA_RULES


class GeminiUnavailableError(Exception):
    """Raised when the Gemini API cannot be reached or is not configured."""


def _get_client():
    """Lazily construct a genai client so import doesn't fail without a key."""
    if not settings.GEMINI_API_KEY:
        raise GeminiUnavailableError("GEMINI_API_KEY is not configured.")
    from google import genai

    # Use v1beta: Render previously returned 404 for the configured models on v1.
    from google.genai import types
    return genai.Client(
        api_key=settings.GEMINI_API_KEY,
        http_options=types.HttpOptions(api_version="v1beta"),
    )


def call_gemini_with_retry(
    contents: str,
    system_instruction: str,
    response_mime_type: str = "application/json",
    max_output_tokens: int = 8192,
    model: Optional[str] = None,
) -> str:
    """
    Calls Gemini via google-genai. On transient errors (429 rate-limit,
    500/503 overloaded) it retries the SAME model with exponential backoff
    (1s then 2s), then automatically falls back to more stable models before
    giving up.

    Returns the raw text of the model's response. Raises GeminiUnavailableError
    only if the API key is missing, the request is rejected (auth / bad request),
    or every model stays overloaded after all retries.
    """
    from google.genai import types
    from google.genai import errors as genai_errors

    client = _get_client()  # raises GeminiUnavailableError only if the key is missing

    # Try the configured model first, then stable fallbacks (deduped, in order).
    primary = model or settings.GEMINI_MODEL
    candidates = [primary, "gemini-2.5-flash", "gemini-flash-latest"]
    models_to_try = list(dict.fromkeys([m for m in candidates if m]))

    max_attempts_per_model = 3
    last_error: Optional[Exception] = None

    for model_name in models_to_try:
        delay = 1.0
        for attempt in range(1, max_attempts_per_model + 1):
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
                text = response.text or ""
                if text:
                    return text
                last_error = RuntimeError("Gemini returned an empty response")
            except genai_errors.APIError as exc:  # type: ignore[attr-defined]
                last_error = exc
                code = getattr(exc, "code", None)
                if code in (429, 500, 503):
                    # transient overload -> back off and retry the same model
                    if attempt < max_attempts_per_model:
                        logger.warning(
                            "Gemini %s on %s (attempt %s/%s); backing off %.0fs...",
                            code, model_name, attempt, max_attempts_per_model, delay,
                        )
                        time.sleep(delay)
                        delay = min(delay * 2, 8.0)
                        continue
                    logger.warning("Gemini %s persisted on %s; trying next model...", code, model_name)
                    break  # exhausted this model -> next fallback model
                if code == 404:
                    logger.warning("Model %s not found (404); trying next model...", model_name)
                    break  # bad model name -> next fallback model
                # auth / bad request / other -> a real problem, surface it
                raise GeminiUnavailableError(f"Gemini API error {code}: {exc}") from exc
            except Exception as exc:  # pragma: no cover - defensive
                last_error = exc
                if attempt < max_attempts_per_model:
                    logger.warning("Gemini unexpected error on %s: %s; retrying...", model_name, exc)
                    time.sleep(delay)
                    delay = min(delay * 2, 8.0)
                    continue
                break  # try next model

    raise GeminiUnavailableError(
        f"Gemini is overloaded/unavailable after retries across models: {last_error}"
    )


def build_context_block(results: List[SearchResultItem]) -> str:
    """Renders retrieved search results into a labeled context block for the prompt.
    Includes law title and article number so Gemini never needs to invent them."""
    if not results:
        return "لا توجد نصوص قانونية مسترجعة — أجب من معرفتك بالقانون المصري مع ذكر القانون والمادة."
    lines = []
    for idx, r in enumerate(results, start=1):
        # Title now contains "المادة X — اسم القانون" from keyword.py
        lines.append(
            f"[مصدر {idx}]\n"
            f"المصدر: {r.title}\n"
            f"النص الحرفي: {r.snippet}\n"
            f"(استشهد بهذا المصدر فقط إذا كان ينطبق فعلاً على وقائع السؤال، وإلا تجاهله تماماً)"
        )
    return "\n\n".join(lines)


def generate_answer(
    question: str,
    context_results: List[SearchResultItem],
    analysis: Optional[Dict[str, Any]] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None,
) -> str:
    """
    Calls Gemini to produce a structured JSON answer matching the 8-section
    LegalAnswerOut schema. Returns the raw JSON string from the model.
    """
    context_block = build_context_block(context_results)

    analysis_block = ""
    if analysis:
        analysis_block = f"\nتحليل أولي للسؤال (JSON): {analysis}\n"

    history_block = ""
    if conversation_history:
        lines = []
        for turn in conversation_history[-4:]:  # last 4 turns for context window
            role_label = "المستخدم" if turn["role"] == "user" else "المساعد"
            lines.append(f"{role_label}: {turn['content'][:300]}")
        history_block = "\nسياق المحادثة السابقة:\n" + "\n".join(lines) + "\n"

    prompt = f"""سؤال المستخدم:
{question}
{analysis_block}{history_block}
سياق البحث (مصادر مسترجعة من قاعدة النصوص وقد لا تنطبق كلها؛ اعتمد منها ما ينطبق فقط، وما تذكره من معرفتك العامة بالقانون المصري فاذكره على أنه غير موثّق من قاعدتنا):
{context_block}

المطلوب: أجب بصيغة JSON فقط يطابق المخطط التالي بالضبط (لا تضف مفاتيح إضافية):
{{
  "understandingOfQuestion": "<ملخص فهمك للسؤال في جملة أو جملتين>",
  "legalDomain": "<المجال القانوني: مثل قانون جنائي، قانون مدني، قانون عمل، إلخ>",
  "relevantLegalTexts": [
    {{
      "id": "<اسم مختصر مميز مثل civil-163>",
      "lawName": "<اسم القانون كما ورد في السياق>",
      "articleNumber": "<رقم المادة أو null إن لم يكن مقالاً>",
      "kind": "<law | judgment | procedure | other>",
      "status": "<current | historical>",
      "excerpt": "<اقتباس مختصر من نص المصدر -- لا تخترع نصاً غير موجود في السياق>",
      "basis": "<from_law إن كان نصاً حرفياً، أو ai_inference إن كان استنتاجاً>"
    }}
  ],
  "explanation": "<الشرح التفصيلي بناءً على السياق المنطبق ومعرفتك بالقانون المصري، دون تكرار>",
  "preliminaryApplication": "<الخلاصة: جملتان كحد أقصى تجيبان مباشرة عن السؤال>",
  "missingInformation": ["<معلومة ناقصة 1>", "<معلومة ناقصة 2>"],
  "possibleProcedures": ["<إجراء قانوني محتمل 1>", "<إجراء قانوني محتمل 2>"],
  "answerSources": [
    {{
      "id": "<اسم مختصر مميز>",
      "lawName": "<اسم القانون>",
      "articleNumber": "<رقم المادة أو null>",
      "kind": "<law | judgment | procedure | other>",
      "status": "<current | historical>",
      "excerpt": "<نص مختصر من المصدر>",
      "basis": "<from_law | ai_inference>"
    }}
  ],
  "disclaimer": "هذه الإجابة لأغراض تعليمية وإرشادية فقط ولا تُغني عن استشارة محامٍ مختص مرخّص له بمزاولة المهنة."
}}

# RICH_INSTRUCTIONS_INJECTED


تعليمات إلزامية لمحتوى كل حقل — لا تختصر أبداً:

"explanation" (الشرح): يجب أن يكون ٤٠٠ كلمة على الأقل. اشرح:
- النص القانوني الحرفي للمادة ومعناها.
- الحق القانوني للعميل بالتحديد.
- التزامات الطرف الآخر.
- الاستثناءات والحالات الخاصة.
- كيف تحسب المبالغ أو التعويضات إن وجدت (بالأرقام والمعادلة).

"preliminaryApplication" (التطبيق): يجب أن يكون ٢٠٠ كلمة على الأقل.
خاطب العميل مباشرة: "في حالتك أنت..." واشرح النتيجة المتوقعة بالتفصيل والأرقام.

"possibleProcedures" (الإجراءات): يجب أن تكون ٦ خطوات على الأقل، كل خطوة جملة كاملة تتضمن:
- الفعل المطلوب بالضبط.
- الجهة المختصة بالاسم (مكتب العمل / المحكمة العمالية الابتدائية / النيابة / الشهر العقاري).
- المستندات المطلوبة بالاسم.
- الميعاد القانوني بالأيام أو الشهور.
- خطوة عن الاستئناف (٣٠ يوماً) وخطوة عن الطعن بالنقض (٦٠ يوماً).

"missingInformation": ٣ عناصر على الأقل — ما الذي يغيّر النتيجة لو عرفناه.

اكتب بأسلوب محامٍ واثق يخاطب موكله: "حقك هو..." "يجب عليك..." "لا يحق لهم...".
لا تكتب جملاً عامة. كل جملة يجب أن تحمل معلومة عملية.

"""
    raw = call_gemini_with_retry(
        contents=prompt,
        system_instruction=NO_HALLUCINATION_SYSTEM_PROMPT,
        response_mime_type="application/json",
        max_output_tokens=8192,
    )
    return raw
