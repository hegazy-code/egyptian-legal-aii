import pathlib

p = pathlib.Path("backend/app/search/keyword.py")
c = p.read_text(encoding="utf-8")

A = lambda *n: "".join(chr(x) for x in n)
# Arabic letters by codepoint to survive any editor
alef=1575; baa=1576; taa=1578; jeem=1580; haa=1581; kha=1582; dal=1583
raa=1585; zay=1586; seen=1587; sheen=1588; sad=1589; dad=1590; tah=1591
ayn=1593; ghayn=1594; fa=1601; qaf=1602; kaf=1603; lam=1604; meem=1605
noon=1606; ha=1607; waw=1608; ya=1610; ta_marbuta=1577; space=32

def w(*cps): return "".join(chr(x) for x in cps)

# Build the synonym map: colloquial -> legal terms to ALSO search
SYN = {
  w(fa,sad,lam,noon,ya): [w(fa,sad,lam), w(taa,ayn,seen,fa,ya)],                 # فصلني -> فصل, تعسفي
  w(fa,sad,lam,noon,alef): [w(fa,sad,lam), w(taa,ayn,seen,fa,ya)],               # فصلنا
  w(tah,raa,dal,noon,ya): [w(fa,sad,lam), w(alef,noon,ha,alef,ab:=1569)] if False else [w(fa,sad,lam)],
}

# Simpler: append an explicit expansion table as Python source
TABLE = """
# colloquial -> legal term expansion
_SYNONYMS = {
    "\\u0641\\u0635\\u0644\\u0646\\u064a": ["\\u0641\\u0635\\u0644", "\\u062a\\u0639\\u0633\\u0641\\u064a"],
    "\\u0637\\u0631\\u062f\\u0646\\u064a": ["\\u0641\\u0635\\u0644", "\\u062a\\u0639\\u0633\\u0641\\u064a"],
    "\\u0637\\u0631\\u062f": ["\\u0641\\u0635\\u0644", "\\u0625\\u062e\\u0644\\u0627\\u0621"],
    "\\u0634\\u063a\\u0644": ["\\u0639\\u0645\\u0644", "\\u0627\\u0644\\u0639\\u0627\\u0645\\u0644"],
    "\\u0645\\u0631\\u062a\\u0628": ["\\u0623\\u062c\\u0631", "\\u0627\\u0644\\u0623\\u062c\\u0631"],
    "\\u0645\\u0631\\u062a\\u0628\\u064a": ["\\u0623\\u062c\\u0631", "\\u0627\\u0644\\u0623\\u062c\\u0631"],
    "\\u0641\\u0644\\u0648\\u0633": ["\\u0645\\u0628\\u0644\\u063a", "\\u0646\\u0642\\u0648\\u062f"],
    "\\u0646\\u0635\\u0628": ["\\u0627\\u062d\\u062a\\u064a\\u0627\\u0644", "\\u0627\\u0644\\u0646\\u0635\\u0628"],
    "\\u0633\\u0631\\u0642\\u0648\\u0646\\u064a": ["\\u0627\\u0644\\u0633\\u0631\\u0642\\u0629", "\\u0633\\u0631\\u0642\\u0629"],
    "\\u0636\\u0631\\u0628\\u0648\\u0646\\u064a": ["\\u0627\\u0644\\u0636\\u0631\\u0628", "\\u062c\\u0631\\u062d"],
    "\\u0637\\u0644\\u0642\\u0646\\u064a": ["\\u0627\\u0644\\u0637\\u0644\\u0627\\u0642", "\\u0637\\u0644\\u0627\\u0642"],
    "\\u0645\\u0639\\u0627\\u0634": ["\\u0645\\u0643\\u0627\\u0641\\u0623\\u0629", "\\u0646\\u0647\\u0627\\u064a\\u0629 \\u0627\\u0644\\u062e\\u062f\\u0645\\u0629"],
    "\\u0634\\u064a\\u0643": ["\\u0627\\u0644\\u0634\\u064a\\u0643", "\\u0631\\u0635\\u064a\\u062f"],
    "\\u0625\\u064a\\u062c\\u0627\\u0631": ["\\u0627\\u0644\\u0625\\u064a\\u062c\\u0627\\u0631", "\\u0627\\u0644\\u0645\\u0633\\u062a\\u0623\\u062c\\u0631"],
    "\\u0627\\u0639\\u062a\\u0631\\u0641\\u062a": ["\\u0627\\u0644\\u0627\\u0639\\u062a\\u0631\\u0627\\u0641", "\\u0625\\u0643\\u0631\\u0627\\u0647"],
}

def _expand(words):
    out = list(words)
    for word in words:
        for key, vals in _SYNONYMS.items():
            if key in word or word in key:
                out.extend(vals)
    seen = set(); res = []
    for x in out:
        if x not in seen:
            seen.add(x); res.append(x)
    return res

"""

if "_SYNONYMS" not in c:
    anchor = "def keyword_search_articles"
    c = c.replace(anchor, TABLE + "\n" + anchor, 1)

old = '        words = [normalized]  # fallback to full query'
new = '        words = [normalized]  # fallback to full query\n    words = _expand(words)'
if "_expand(words)" not in c:
    c = c.replace(old, new, 1)

c = c.replace("for word in words[:6]:", "for word in words[:10]:")

p.write_text(c, encoding="utf-8")
print("ok" if "_SYNONYMS" in c and "_expand(words)" in c else "FAILED")