# -*- coding: utf-8 -*-
"""
Article explanation endpoint -- generates a plain-language explanation + a
real-world example for ONE legal article, on demand, via Gemini.

Rewritten to use the app's SQLAlchemy session (works on Postgres/Neon in
production) instead of a local SQLite file.
"""
import re
import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.legal import Article
from app.rag.engine import call_gemini_with_retry, GeminiUnavailableError

logger = logging.getLogger(__name__)
router = APIRouter(tags=["explanations"])


_SYS = (
    "أنت شارح قانوني مصري خبير. مهمتك تبسيط المواد القانونية لأي شخص عادي بدون خلفية قانونية. "
    "اشرح معنى المادة بلغة واضحة ومباشرة، ثم اضرب مثالاً عملياً واقعياً واحداً من الحياة اليومية في مصر "
    "يوضّح كيف تنطبق المادة فعلياً. لا تخترع أرقام مواد أو قوانين أخرى. اكتب بالعربية فقط."
)


@router.post("/articles/{article_id}/explain")
def explain_article(article_id: str, regenerate: bool = False, db: Session = Depends(get_db)):
    """يرجّع شرح المادة + مثال، يولّده بـGemini من نص المادة المخزّن في قاعدة البيانات."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(404, "المادة غير موجودة")

    number = article.article_number
    text = article.text
    law_title = article.law.title if article.law else ""

    prompt = (
        f"المادة رقم {number} من {law_title}:\n«{text}»\n\n"
        "اشرح هذه المادة لشخص عادي، ثم اضرب مثالاً عملياً واقعياً واحداً يوضّح تطبيقها.\n"
        "أرجع JSON فقط بهذا الشكل بالضبط (بدون أي نص خارج الـJSON):\n"
        '{"explanation": "<شرح مفصّل واضح بالعربية، من 4 إلى 8 أسطر>", '
        '"example": "<مثال عملي واقعي واحد من الحياة اليومية في مصر يوضّح تطبيق المادة>"}'
    )
    try:
        raw = call_gemini_with_retry(
            contents=prompt, system_instruction=_SYS,
            response_mime_type="application/json", max_output_tokens=2048,
        )
    except GeminiUnavailableError as exc:
        raise HTTPException(503, "خدمة الشرح مزدحمة مؤقتاً، حاول بعد لحظات.") from exc

    raw = (raw or "").strip()
    m = re.search(r"\{.*\}", raw, re.S)
    try:
        data = json.loads(m.group(0) if m else raw)
    except Exception as exc:
        raise HTTPException(502, "تعذّر قراءة الشرح المُولَّد.") from exc

    explanation = (data.get("explanation") or "").strip()
    example = (data.get("example") or "").strip()
    if not explanation:
        raise HTTPException(502, "تعذّر توليد الشرح.")

    return {"articleNumber": number, "explanation": explanation,
            "example": example, "cached": False}
