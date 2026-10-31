import pathlib
p = pathlib.Path("backend/app/search/keyword.py")
lines = p.read_text(encoding="utf-8").split("\n")
out = []
i = 0
while i < len(lines):
    ln = lines[i]
    if "from sqlalchemy.orm import Session" in ln and "joinedload" not in ln:
        out.append("from sqlalchemy.orm import Session, joinedload")
        i += 1
        continue
    if ln.strip() == ".filter(or_(*conditions))":
        out.append("        .options(joinedload(Article.law))")
        out.append(ln)
        i += 1
        continue
    if "score = sum(1 for w in words if w in text_lower)" in ln:
        out.append("        score = 0.0")
        out.append("        matched = 0")
        out.append("        for w in words:")
        out.append("            if w in text_lower:")
        out.append("                matched += 1")
        out.append("                score += 10.0 / (DF.get(w) or 1)")
        out.append("                score += text_lower.count(w) * 0.5")
        out.append("        if len(words) >= 3 and matched < 2:")
        out.append("            score *= 0.2")
        out.append("        if len(text_lower) < 80:")
        out.append("            score *= 0.4")
        i += 1
        continue
    if ln.strip() == "scored = []":
        out.append("    DF = {}")
        out.append("    for w in words:")
        out.append("        DF[w] = sum(1 for a in rows if w in (a.text or '').lower()) or 1")
        out.append(ln)
        i += 1
        continue
    if "rows = [a for _, a in scored[:limit]]" in ln:
        out.append("    scored = [(s, a) for s, a in scored[:limit] if s > 0]")
        i += 1
        continue
    if ln.strip() == "for a in rows:" and i > 40:
        out.append("    for computed_score, a in scored:")
        i += 1
        continue
    if "score = _match_score(text, normalized)" in ln:
        out.append("        law_title = a.law.title if getattr(a, 'law', None) else ''")
        i += 1
        continue
    if "title=f" in ln and "article_number" in ln:
        out.append('                title=f"' + chr(1575) + chr(1604) + chr(1605) + chr(1575) + chr(1583) + chr(1577) + ' {a.article_number} - {law_title}",')
        i += 1
        continue
    if "score=score," in ln:
        out.append("                score=computed_score,")
        i += 1
        continue
    out.append(ln)
    i += 1

p.write_text("\n".join(out), encoding="utf-8")
print("patched")