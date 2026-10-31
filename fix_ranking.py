"""Improve search ranking: prefer specific legal concept matches over generic articles."""
import pathlib

p = pathlib.Path("backend/app/search/keyword.py")
c = p.read_text(encoding="utf-8")

old = """    # Score by number of keyword matches (real score, not reset to 1.0)
    scored = []
    for a in rows:
        text_lower = (a.text or "").lower()
        score = sum(1.0 for w in words if w in text_lower)
        scored.append((score, a))
    scored.sort(key=lambda x: x[0], reverse=True)
    rows_with_scores = scored[:limit]"""

new = '''    # Score with concept weighting: rare/specific terms score higher than common ones
    # Count how many articles contain each word (document frequency)
    df = {}
    for w in words:
        df[w] = sum(1 for a in rows if w in (a.text or "").lower())

    scored = []
    for a in rows:
        text_lower = (a.text or "").lower()
        score = 0.0
        matched = 0
        for w in words:
            if w in text_lower:
                matched += 1
                # Inverse document frequency: rarer word = higher weight
                freq = df.get(w, 1) or 1
                idf = 1.0 / freq
                score += idf * 10
                # Bonus if word appears multiple times (topic focus)
                score += text_lower.count(w) * 0.5
        # Require at least 2 keyword matches for multi-word queries
        if len(words) >= 3 and matched < 2:
            score *= 0.2
        # Penalize very short articles (usually definitions, not substantive rules)
        if len(text_lower) < 80:
            score *= 0.5
        scored.append((score, a))
    scored.sort(key=lambda x: x[0], reverse=True)
    rows_with_scores = [(s, a) for s, a in scored[:limit] if s > 0]'''

if old in c:
    p.write_text(c.replace(old, new), encoding="utf-8")
    print("✅ Ranking improved: IDF weighting + multi-match requirement + definition penalty")
else:
    print("❌ Pattern not found")
