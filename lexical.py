"""
In-memory lexical (BM25-style) search over law articles.

Why: the legal corpus is small (thousands of articles), Arabic full-text search is weak in SQLite/Postgres, and
the old whole-phrase LIKE match almost never matched a natural-language question. This tokenizes + normalizes
the question and the articles the same way and ranks by term overlap, with a boost when the question names the law.
"""
import math
import re
import threading
from collections import Counter
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.legal import Article, Law
from app.schemas.legal import SearchResultItem
from app.utils.arabic import normalize_arabic_digits, strip_diacritics

_TOKEN = re.compile(r"[ء-ي0-9]+")
_STOP = set(
    """في من على الى الي عن مع ان انه انها هذا هذه ذلك تلك هو هي هم هن ما ماذا متي كيف اين لماذا هل
    لو اذا اذ او ثم قد لا لم لن ليس كان يكون تكون كل بعض غير اي ايه ايضا فقط بعد قبل بين حتي عند لدي
    الذي التي الذين اللذان ومن وما وفي وعلي والي وهل وان كما حيث اما اما ولا بل لكن علي منذ خلال
    انا نحن انت انتي هو يجوز يمكن اريد اريدان عايز كم ماهو ماهي ما هو ما هي لي لنا له لها لهم به بها بهم
    حكم احكام قانون القانون المصري مصر المصريه وما الخطوات اتبع اتبعه افعل ماذا افعل""".split()
)
_STOP = {w for w in _STOP}


def normalize(text: str) -> str:
    text = strip_diacritics(text or "")
    text = normalize_arabic_digits(text).replace("ـ", "")
    for a, b in (("أ", "ا"), ("إ", "ا"), ("آ", "ا"), ("ى", "ي"), ("ة", "ه"), ("ؤ", "و"), ("ئ", "ي")):
        text = text.replace(a, b)
    return text


def _stem(tok: str) -> str:
    # light prefix/suffix stripping: ال / وال / بال / لل / فال, plural/dual/pronoun suffixes
    for p in ("وال", "بال", "كال", "فال", "لل", "ال", "و"):
        if tok.startswith(p) and len(tok) - len(p) >= 3:
            tok = tok[len(p):]
            break
    for s in ("ات", "ون", "ين", "ان", "ها", "هم", "ه", "ي"):
        if tok.endswith(s) and len(tok) - len(s) >= 3:
            tok = tok[: -len(s)]
            break
    return tok


def tokenize(text: str) -> List[str]:
    toks = []
    for raw in _TOKEN.findall(normalize(text)):
        if raw in _STOP or len(raw) < 2:
            continue
        toks.append(_stem(raw))
    return [t for t in toks if t and t not in _STOP]


class _Index:
    def __init__(self, rows: List[Tuple[str, str, str, str, str]]):
        # rows: (article_id, law_title, article_number, chapter, text)
        self.rows = rows
        self.tf: List[Counter] = []
        self.lens: List[int] = []
        self.df: Counter = Counter()
        self.law_tokens: List[set] = []
        for (_, law_title, number, chapter, text) in rows:
            toks = tokenize(f"{chapter} {text}")
            c = Counter(toks)
            self.tf.append(c)
            self.lens.append(max(len(toks), 1))
            for t in c:
                self.df[t] += 1
            self.law_tokens.append(set(tokenize(law_title)))
        self.n = len(rows)
        self.avg = sum(self.lens) / self.n if self.n else 1.0

    def score(self, q_tokens: List[str], boost_law_tokens: set) -> List[Tuple[float, int]]:
        k1, b = 1.4, 0.75
        out = []
        qset = list(dict.fromkeys(q_tokens))
        idf = {t: math.log(1 + (self.n - self.df.get(t, 0) + 0.5) / (self.df.get(t, 0) + 0.5)) for t in qset}
        for i in range(self.n):
            c = self.tf[i]
            s = 0.0
            matched = 0
            for t in qset:
                f = c.get(t, 0)
                if not f:
                    continue
                matched += 1
                s += idf[t] * (f * (k1 + 1)) / (f + k1 * (1 - b + b * self.lens[i] / self.avg))
            if not s:
                continue
            # reward articles that cover many distinct query terms
            s *= 1 + 0.35 * (matched - 1)
            if boost_law_tokens and (self.law_tokens[i] & boost_law_tokens):
                s *= 1.25
            out.append((s, i))
        out.sort(reverse=True)
        return out


_lock = threading.Lock()
_cache: Dict[str, object] = {"key": None, "index": None}


def _get_index(db: Session) -> Optional[_Index]:
    count = db.query(Article).count()
    if count == 0:
        return None
    with _lock:
        if _cache["key"] != count:
            rows = (
                db.query(Article.id, Law.title, Article.article_number, Article.chapter, Article.text)
                .join(Law, Law.id == Article.law_id)
                .all()
            )
            _cache["index"] = _Index([tuple(r) for r in rows])
            _cache["key"] = count
        return _cache["index"]  # type: ignore[return-value]


def _law_warnings() -> Dict[str, str]:
    """title -> currency warning (e.g. law replaced/amended since this edition), from the manifest."""
    try:
        from app.seed.law_manifest import MANIFEST

        return {m[2]: m[6].strip() for m in MANIFEST if m[6].strip()}
    except Exception:
        return {}


_WARNINGS = _law_warnings()


def lexical_search_articles(db: Session, query: str, limit: int = 8, snippet_chars: int = 1100) -> List[SearchResultItem]:
    index = _get_index(db)
    if index is None:
        return []
    q_tokens = tokenize(query)
    if not q_tokens:
        return []
    ranked = index.score(q_tokens, boost_law_tokens=set(q_tokens))
    results: List[SearchResultItem] = []
    for s, i in ranked[:limit]:
        art_id, law_title, number, chapter, text = index.rows[i]
        results.append(
            SearchResultItem(
                result_type="article",
                id=art_id,
                title=f"{law_title} — المادة {number}",
                snippet=(f"[{_WARNINGS[law_title]}] " if law_title in _WARNINGS else "") + (text or "")[:snippet_chars],
                score=float(s),
            )
        )
    return results
