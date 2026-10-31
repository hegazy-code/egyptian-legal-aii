import pathlib

p = pathlib.Path("backend/app/search/keyword.py")
c = p.read_text(encoding="utf-8")

# 1. eager-load the law so we can show its title
if "joinedload" not in c:
    c = c.replace("from sqlalchemy.orm import Session",
                  "from sqlalchemy.orm import Session, joinedload")

c = c.replace(
    "    rows = (\n        db.query(Article)\n        .filter(or_(*conditions))",
    "    rows = (\n        db.query(Article)\n        .options(joinedload(Article.law))\n        .filter(or_(*conditions))"
)

# 2. replace flat scoring with IDF-weighted scoring
old_score = '''    # Score by number of keyword matches
    scored = []
    for a in rows:
        text_lower = (a.text or "").lower()
        score = sum(1 for w in words if w in text_lower)
        scored.append((score, a))
    scored.sort(key=lambda x: x[0], reverse=True)
    rows = [a for _, a in scored[:limit]]'''

new_score = '''    # IDF-weighted scoring: rare/specific terms rank higher than common ones
    df = {}
    for w in words:
        df[w] = sum(1 for a in rows if w in (a.text or "").lower()) or 1

    scored = []
    for a in rows:
        text_lower = (a.text or "").lower()
        score = 0.0
        matched = 0