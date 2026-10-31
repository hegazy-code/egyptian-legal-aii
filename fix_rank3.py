import pathlib

p = pathlib.Path("backend/app/search/keyword.py")
c = p.read_text(encoding="utf-8")

if "joinedload" not in c:
    c = c.replace("from sqlalchemy.orm import Session",
                  "from sqlalchemy.orm import Session, joinedload")

c = c.replace(
    "    rows = (\n        db.query(Article)\n        .filter(or_(*conditions))",
    "    rows = (\n        db.query(Article)\n        .options(joinedload(Article.law))\n        .filter(or_(*conditions))"
)

old_score = "\n".join([
    "    # Score by number of keyword matches",
    "    scored = []",
    "    for a in rows:",
    '        text_lower = (a.text or "").lower()',
    "        score = sum(1 for w in words if w in text_lower)",
    "        scored.append((score, a))",
    "    scored.sort(key=lambda x: x[0], reverse=True)",
    "    rows = [a for _, a in scored[:limit]]",
])

new_score = "\n".join([
    "    # IDF-weighted scoring",
    "    df = {}",
    "    for w in words:",
    '        df[w] = sum(1 for a in rows if w in (a.text or "").lower()) or 1',
    "    scored = []",
    "    for a in rows:",
    '        text_lower = (a.text or "").lower()',
    "        score = 0.0",
    "        matched = 0",
    "        for w in words:",
    "            if w in text_lower:",
    "                matched += 1",
    "                score += (10.0 / df[w])",
    "                score += text_lower.count(w) * 0.5",
    "        if