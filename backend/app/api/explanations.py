# -*- coding: utf-8 -*-
"""
Article explanation endpoint — generates a plain-language explanation + a
real-world example for ONE legal article, on demand, and caches it in the
`articles` table so each article is generated only once.

ضعه في:  backend/app/routers/explanations.py
وسجّله في  backend/app/main.py  بسطر واحد:

    from app.routers import explanations
    app.include_router(explanations.router)

(لو عندك prefix موحّد للراوترات زي /api، سجّله بنفس طريقة باقي الراوترات.)
"""
import os
import re
import json
import sqlite3
import logging

from fastapi import APIRouter, HTTPException

from app.rag.engine import call_gemini_with_retry, GeminiUnavailableError

logger = logging.getLogger(__name__)
router = APIRouter(tags=["explanations"])


def _db_path() -> str:
    """يلاقي ملف legal_ai.db اللي الـbackend بيستخدمه."""
    try:
        from app.config import settings
        url = (getattr(settings, "DATABASE_URL", None)
               or getattr(settings, "SQLALCHEMY_DATABASE_URI", None)
               or getattr(settings, "DB_URL", None) or "")
        url = str(url)
        if "sqlite" in url:
            p = url.split("sqlite:///")[-1].split("sqlite://")[-1]
            p = os.path.abspath(p)
            if os.path.exists(p):
                return p
    except Exception:
        pass
    for cand in (os.path.join(os.getcwd(), "legal_ai.db"),
                 os.path.join(os.path.dirname(os.getcwd()), "legal_ai.db")):
        if os.path.exists(cand):
            return cand
    for dp, _dn, fn in os.walk(os.getcwd()):
        if "legal_ai.db" in fn:
            return os.path.join(dp, "legal_ai.db")
    raise HTTPException(500, "لم أجد legal_ai.db")


def _ensure_columns(con: sqlite3.Connection) -> None:
    cols = {r[1] for r in con.execute("PRAGMA table_info(articles)")}
    if "explanation" not in cols:
        con.execute("ALTER TABLE articles ADD COLUMN explanation TEXT")
    if "example" not in cols:
        con.execute("ALTER TABLE articles ADD COLUMN example TEXT")
    con.commit()


_SYS = (
    "أنت شارح قانوني مصري خبير. مهمتك تبسيط المواد القانونية لأي شخص عادي بدون خلفية قانونية. "
    "اشرح معنى المادة بلغة واضحة ومباشرة، ثم اضرب مثالاً عملياً واقعياً واحداً من الحياة اليومية في مصر "
    "يوضّح كيف تنطبق المادة فعلياً. لا تخترع أرقام مواد أو قوانين أخرى. اكتب بالعربية فقط."
)


@router.post("/articles/{article_id}/explain")
def explain_article(article_id: str, regenerate: bool = False):
    """
    يرجّع شرح المادة + مثال. لو متخزّن قبل كده بيرجّعه فوراً (cached=true)،
    وإلا بيولّده بـGemini ويخزّنه. regenerate=true يعيد التوليد ويستبدل المخزّن.
    """
    con = sqlite3.connect(_db_path())
    try:
        _ensure_columns(con)
        row = con.execute(
            "SELECT a.article_number, a.text, a.explanation, a.example, l.title "
            "FROM articles a JOIN laws l ON a.law_id = l.id WHERE a.id = ?",
            (article_id,),
        ).fetchone()
        if not row:
            raise HTTPException(404, "المادة غير موجودة")
        number, text, cached_expl, cached_ex, law_title = row

        if cached_expl and cached_ex and not regenerate:
            return {"articleNumber": number, "explanation": cached_expl,
                    "example": cached_ex, "cached": True}

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

        con.execute("UPDATE articles SET explanation = ?, example = ? WHERE id = ?",
                    (explanation, example, article_id))
        con.commit()
        return {"articleNumber": number, "explanation": explanation,
                "example": example, "cached": False}
    finally:
        con.close()
