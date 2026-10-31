"""Fix Arabic prefix stripping in keyword search."""
import pathlib

p = pathlib.Path("backend/app/search/keyword.py")
content = p.read_text(encoding="utf-8")

old = "# Arabic stop words to exclude from keyword search\n_ARABIC_STOPWORDS"

new = '''# Arabic prefixes to strip for root matching
_ARABIC_PREFIXES = ("وال", "بال", "كال", "فال", "لل", "وب", "وك", "ول",
                    "وف", "ال", "و", "ب", "ل", "ك", "ف")

def _extract_root(word: str) -> str:
    """Strip common Arabic prefixes to get a matchable root."""
    for prefix in _ARABIC_PREFIXES:
        if word.startswith(prefix) and len(word) - len(prefix) >= 3:
            return word[len(prefix):]
    return word

# Arabic stop words to exclude from keyword search
_ARABIC_STOPWORDS'''

if old in content:
    content = content.replace(old, new)
    # Also update the conditions to include root form
    old2 = "    conditions = []\n    for word in words[:6]:  # max 6 keywords to avoid huge queries\n        pat = f\"%{word}%\"\n        conditions.append(Article.text.ilike(pat))\n        conditions.append(Article.article_number.ilike(pat))"
    new2 = """    conditions = []
    for word in words[:6]:  # max 6 keywords to avoid huge queries
        pat = f\"%{word}%\"
        conditions.append(Article.text.ilike(pat))
        conditions.append(Article.article_number.ilike(pat))
        # Also search for root form (without Arabic prefixes)
        root = _extract_root(word)
        if root != word and len(root) >= 3:
            root_pat = f\"%{root}%\"
            conditions.append(Article.text.ilike(root_pat))"""
    if old2 in content:
        content = content.replace(old2, new2)
        p.write_text(content, encoding="utf-8")
        print("✅ Arabic prefix stripping added to keyword search")
    else:
        print("❌ conditions block not found")
else:
    print("❌ stopwords block not found")