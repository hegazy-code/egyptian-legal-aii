"""Fix keyword search to split query into words instead of one big LIKE."""
import pathlib

p = pathlib.Path("backend/app/search/keyword.py")
old = '''def keyword_search_articles(db: Session, query: str, limit: int = 10) -> List[SearchResultItem]:
    normalized = simple_normalize(query)
    if not normalized:
        return []
    like_pattern = f"%{normalized}%"
    rows = (
        db.query(Article)
        .filter(or_(Article.text.ilike(like_pattern), Article.article_number.ilike(like_pattern)))
        .limit(limit)
        .all()
    )'''

new = '''# Arabic stop words to exclude from keyword search
_ARABIC_STOPWORDS = {
    "ما","هي","هو","هل","من","في","عن","إلى","الى","على","عند","كيف",
    "ماذا","لماذا","متى","اين","أين","هذا","هذه","ذلك","تلك","التي","الذي",
    "مع","بين","حول","خلال","بعد","قبل","حتى","لكن","او","أو","و","ف",
    "ب","ل","ك","لا","ليس","كان","يكون","يجب","هناك",
}

def keyword_search_articles(db: Session, query: str, limit: int = 10) -> List[SearchResultItem]:
    normalized = simple_normalize(query)
    if not normalized:
        return []
    # Split into meaningful words (>=3 chars, not stopwords)
    words = [w for w in normalized.split() if len(w) >= 3 and w not in _ARABIC_STOPWORDS]
    if not words:
        words = [normalized]  # fallback to full query
    # OR search: any article containing any keyword
    conditions = []
    for word in words[:6]:  # max 6 keywords to avoid huge queries
        pat = f"%{word}%"
        conditions.append(Article.text.ilike(pat))
        conditions.append(Article.article_number.ilike(pat))
    rows = (
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
    rows = [a for _, a in scored[:limit]]'''

content = p.read_text(encoding="utf-8")
if old in content:
    p.write_text(content.replace(old, new), encoding="utf-8")
    print("✅ keyword.py fixed - now splits query into keywords")
else:
    print("❌ Pattern not found - check keyword.py manually")