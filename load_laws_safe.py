import re, unicodedata
from pathlib import Path

_DIG = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
_SUF = r"(?:مكرر[اً]{0,2}|ثالثة|رابعة|ثانية|ثانيا|ثانياً|ثالثا|ثالثاً|رابعا|رابعاً|أولا|أولاً|\([^)\n]{1,6}\))"
_HDR = re.compile(r"^[ \t]*(?:ال)?مادة[ \t]+([0-9٠-٩]+(?:[ \t]+" + _SUF + r")*)[ \t]*(?::[ \t]*(.*))?$", re.M)
_SKIP = re.compile(r"^\s*(?:الباب|الكتاب|القسم|الفصل|المخالفات المتعلقة|المخالفات المنصوص|التعديل الأخير|تم تعديل|\(مضافة بالقانون|عن الموقع|اتصل بنا|شارك في تطوير)")

def _key(s):
    s = s.translate(_DIG)
    s = re.sub(r"[\u064B-\u0652]", "", s)
    s = re.sub(r"مكرر[ا]?", "مكرر", s)
    s = re.sub(r"(أولا|ثانيا|ثالثا|رابعا)", lambda m: m.group(1) + "\u064B", s)
    return re.sub(r"\s+", " ", s).strip()

def split_text(raw):
    m = re.search(r"الكتاب الأول\s+أحكام ابتدائية", raw)
    if m:
        raw = raw[m.start():]
    raw = raw.replace("\u200f", "").replace("\u200e", "").replace("\u0640", "").replace("\r", "")
    marks = list(_HDR.finditer(raw))
    seen, order = {}, []
    for i, h in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(raw)
        body = (h.group(2) or "") + "\n" + raw[h.end():end]
        lines = [l.strip() for l in body.split("\n") if l.strip() and not _SKIP.match(l)]
        text = " ".join(lines).strip()
        if len(text) < 12 or re.fullmatch(r"ملغ[اى]ة?\.?|ملغي\.?", text):
            continue
        k = _key(h.group(1))
        if k not in seen or len(text) > len(seen[k]):
            seen[k] = text
            if k not in order:
                order.append(k)
    return [{"n": k, "t": seen[k]} for k in order]


def norm_pdf_text(t):
    t = unicodedata.normalize("NFKC", t)
    for a, b in {"ھ": "ه", "ی": "ي", "ک": "ك", "ۀ": "ه", "ە": "ه", "ٔ": ""}.items():
        t = t.replace(a, b)
    return t

def load_law(db, Law, Article, articles, number, year, category, title, min_articles):
    """Replace a law only if the parse looks complete; otherwise leave the DB untouched."""
    if len(articles) < min_articles:
        print("  SKIPPED %s: parsed only %d articles (needs >= %d). Database NOT changed." % (title, len(articles), min_articles))
        return False
    old = db.query(Law).filter(Law.law_number == number, Law.year == year).all()
    for L in old:
        db.query(Article).filter(Article.law_id == L.id).delete()
        db.delete(L)
    db.flush()
    law = Law(law_number=number, year=year, category=category, status="active", title=title)
    db.add(law)
    db.flush()
    for a in articles:
        db.add(Article(law_id=law.id, article_number=a["n"], text=a["t"], status="active"))
    db.commit()
    print("  LOADED %s: %d articles (replaced %d old row(s))" % (title, len(articles), len(old)))
    return True


import re, sys, subprocess, unicodedata
from pathlib import Path

def readtxt(f):
    for enc in ("utf-8-sig", "utf-16", "cp1256"):
        try:
            return Path(f).read_text(encoding=enc)
        except Exception:
            pass
    return ""

dl = Path.home() / "Downloads"

import html as _html, urllib.request

def html_to_text(h):
    h = re.sub(r"(?is)<(script|style|nav|header|footer)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?i)<br\s*/?>", "\n", h)
    h = re.sub(r"(?i)</(p|div|h[1-6]|li|tr|ul|ol|section|article)>", "\n", h)
    h = re.sub(r"(?s)<[^>]+>", "", h)
    h = _html.unescape(h).replace("\xa0", " ")
    return re.sub(r"[ \t]+\n", "\n", h)

def download_penal():
    try:
        req = urllib.request.Request("https://manshurat.org/node/14677", headers={"User-Agent": "Mozilla/5.0"})
        h = urllib.request.urlopen(req, timeout=90).read().decode("utf-8", "ignore")
        t = html_to_text(h)
        if "الكتاب الأول" in t and "أحكام ابتدائية" in t:
            print("Penal Code downloaded from manshurat.org:", len(t), "characters")
            return t
        print("Downloaded page did not contain the Penal Code text")
    except Exception as e:
        print("Penal Code download failed:", e)
    return ""

# ---- 1) Penal Code text: download, else newest matching .txt in Downloads, else the clipboard
penal_text = download_penal()
for f in ([] if penal_text else sorted(dl.glob("*.txt"), key=lambda x: x.stat().st_mtime, reverse=True)[:60]):
    t = readtxt(f)
    if "قانون العقوبات" in t[:800] and "1937" in t[:800]:
        penal_text = t
        print("Penal Code text file:", f.name)
        break
if not penal_text:
    ps = "[Console]::OutputEncoding=[Text.Encoding]::UTF8; Get-Clipboard -Raw"
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True)
    t = r.stdout.decode("utf-8", "ignore")
    if "الكتاب الأول" in t and "أحكام ابتدائية" in t:
        penal_text = t
        (dl / "penal-58-1937.txt").write_text(t, encoding="utf-8")
        print("Penal Code text taken from the clipboard and saved to Downloads/penal-58-1937.txt")
if not penal_text:
    print("Penal Code text NOT FOUND (open manshurat.org/node/14677, Ctrl+A, Ctrl+C, then run again)")

# ---- 2) Cybercrime Law PDF
cyber_text = ""
pdf = dl / "law-175-2018.pdf"
if pdf.exists():
    try:
        from pypdf import PdfReader
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "pypdf", "-q"])
        from pypdf import PdfReader
    raw = pdf.read_bytes()
    end = raw.rfind(b"%%EOF")
    if end > 0 and len(raw) - (end + 5) > 1000:
        pdf2 = pdf.with_name("repaired_" + pdf.name)
        pdf2.write_bytes(raw[:end + 5])
        pdf = pdf2
    cyber_text = norm_pdf_text("\n".join((p.extract_text() or "") for p in PdfReader(str(pdf)).pages))
    cyber_text = re.sub(r"(?m)^[ \t]*([0-9٠-٩]+)[ \t]+المادة[ \t]*$", r"المادة \1", cyber_text)
    print("Cybercrime PDF read:", len(cyber_text), "characters")
else:
    print("Cybercrime PDF not found in Downloads")

# ---- 3) load into the database (only if the parse looks complete)
import os
os.chdir("backend")
sys.path.insert(0, os.getcwd())
from app.database import SessionLocal
from app.models.legal import Law, Article
from app.database import engine
print("DATABASE:", engine.url)
db = SessionLocal()
try:
    if penal_text:
        arts = split_text(penal_text)
        print("Penal Code parsed:", len(arts), "articles")
        load_law(db, Law, Article, arts, "58", 1937, "criminal", "قانون العقوبات رقم 58 لسنة 1937", 300)
    if cyber_text:
        arts = split_text(cyber_text)
        print("Cybercrime Law parsed:", len(arts), "articles")
        if len(arts) < 30:
            print("  first 400 characters of the PDF text, for diagnosis:")
            print(cyber_text[:400])
        load_law(db, Law, Article, arts, "175", 2018, "cybercrime", "قانون مكافحة جرائم تقنية المعلومات رقم 175 لسنة 2018", 30)
finally:
    db.close()
print("FINISHED")
