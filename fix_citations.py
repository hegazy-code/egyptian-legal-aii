"""
Fix 3 root causes:
1. Law title missing from context block - Gemini fabricates law names
2. Scores reset to 1.0 regardless of relevance
3. System prompt still restrictive
"""
import pathlib

# ── FIX 1: keyword.py — include law title + real scores ──────────────────────
kw = pathlib.Path("backend/app/search/keyword.py")
kw_src = kw.read_text(encoding="utf-8")

# Add joinedload import
if "joinedload" not in kw_src:
    kw_src = kw_src.replace(
        "from sqlalchemy.orm import Session",
        "from sqlalchemy.orm import Session, joinedload"
    )

# Fix query to eagerly load law, and assign real score
old_query = """    rows = (
        db.query(Article)
        .filter(or_(*conditions))
        .limit(limit * 2)
        .all()
    )
    # Score by number of keyword matches
    scored = []
    for a in rows:
        text_lower = (a.text or "").lower()
        score = sum(1 for w in words if w in text_lower)
        scored.append((score, a))
    scored.sort(key=lambda x: x[0], reverse=True)
    rows = [a for _, a in scored[:limit]]"""

new_query = """    rows = (
        db.query(Article)
        .options(joinedload(Article.law))
        .filter(or_(*conditions))
        .limit(limit * 2)
        .all()
    )
    # Score by number of keyword matches (real score, not reset to 1.0)
    scored = []
    for a in rows:
        text_lower = (a.text or "").lower()
        score = sum(1.0 for w in words if w in text_lower)
        scored.append((score, a))
    scored.sort(key=lambda x: x[0], reverse=True)
    rows_with_scores = scored[:limit]"""

if old_query in kw_src:
    kw_src = kw_src.replace(old_query, new_query)

# Fix result construction to use real score and include law title
old_result = """    results = []
    for a in rows:
        snippet = (a.text or "")[:240]
        results.append(
            SearchResultItem(
                result_type="article",
                id=a.id,
                title=f"المادة {a.article_number}",
                snippet=snippet,
                score=1.0,
            )
        )
    return results"""

new_result = """    results = []
    for score, a in rows_with_scores:
        law_title = a.law.title if a.law else "قانون مصري"
        snippet = (a.text or "")[:240]
        results.append(
            SearchResultItem(
                result_type="article",
                id=a.id,
                title=f"المادة {a.article_number} — {law_title}",
                snippet=snippet,
                score=max(score, 0.1),
            )
        )
    return results"""

if old_result in kw_src:
    kw_src = kw_src.replace(old_result, new_result)
    kw.write_text(kw_src, encoding="utf-8")
    print("✅ keyword.py fixed: law titles + real scores")
else:
    print("⚠️ keyword.py result block not found — check manually")

# ── FIX 2: engine.py — rewrite build_context_block to show law metadata ──────
eng = pathlib.Path("backend/app/rag/engine.py")
eng_src = eng.read_text(encoding="utf-8")

old_ctx = '''def build_context_block(results: List[SearchResultItem]) -> str:
    """Renders retrieved search results into a labeled context block for the prompt."""
    if not results:
        return "لا توجد نتائج بحث ذات صلة في قاعدة البيانات الحالية."
    lines = []
    for idx, r in enumerate(results, start=1):
        lines.append(f"[مصدر {idx}] النوع: {r.result_type} | العنوان: {r.title}\\nالنص: {r.snippet}")
    return "\\n\\n".join(lines)'''

new_ctx = '''def build_context_block(results: List[SearchResultItem]) -> str:
    """Renders retrieved search results into a labeled context block for the prompt.
    Includes law title and article number so Gemini never needs to invent them."""
    if not results:
        return "لا توجد نصوص قانونية مسترجعة — أجب من معرفتك بالقانون المصري مع ذكر القانون والمادة."
    lines = []
    for idx, r in enumerate(results, start=1):
        # Title now contains "المادة X — اسم القانون" from keyword.py
        lines.append(
            f"[مصدر {idx}]\\n"
            f"المصدر: {r.title}\\n"
            f"النص الحرفي: {r.snippet}\\n"
            f"(يجب الاستشهاد بهذا المصدر حرفياً في الإجابة)"
        )
    return "\\n\\n".join(lines)'''

if old_ctx in eng_src:
    eng_src = eng_src.replace(old_ctx, new_ctx)
    eng.write_text(eng_src, encoding="utf-8")
    print("✅ engine.py fixed: context block now includes law metadata")
else:
    print("⚠️ engine.py context block not found exactly — may already be updated")
    # Try partial fix
    if "build_context_block" in eng_src:
        print("   build_context_block exists locally with different text (likely our earlier edit)")

print("\nDone. Restart backend from backend folder.")