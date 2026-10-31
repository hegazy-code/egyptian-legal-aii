import re, sys, unicodedata, subprocess
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "pypdf",
                    "--break-system-packages", "-q"])
    from pypdf import PdfReader

TARGETS = [
    (r"C:\Users\Yousssef\Downloads\law-131-1948.pdf",
     "131", 1948, "civil", "القانون المدني رقم 131 لسنة 1948"),
    (r"C:\Users\Yousssef\Downloads\qnwn_lml_ljdyd_14_lsn_2025_m_q.pdf",
     "14", 2025, "labor", "قانون العمل رقم 14 لسنة 2025"),
]

GENUINE = ["آخر","آخرين","الآن","آلاف","مكافآت","منشآت","القرآن","آية",
           "آيات","آثار","الآثار","مرآة","آجل","آتية","الآتية","الآتي"]
MARKS = dict.fromkeys([0x200B,0x200C,0x200D,0x200E,0x200F,0x202A,0x202B,
                       0x202C,0x202D,0x202E,0x2066,0x2067,0x2068,0x2069,0xFEFF])
DIG = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")

def norm(t):
    t = unicodedata.normalize("NFKC", t).translate(MARKS).replace("\u0640", "")
    if t.count("آ") >= 20:
        hold = {}
        for i, w in enumerate(GENUINE):
            if w in t:
                hold["\x00" + str(i) + "\x00"] = w
                t = t.replace(w, "\x00" + str(i) + "\x00")
        t = t.replace("آ", "ك")
        for k, v in hold.items():
            t = t.replace(k, v)
    return re.sub(r"[ \t]+", " ", t)

STD = re.compile(r"(?:^|\n|(?<=[.\u061B:\u060C])\s{0,4})\s*(?:ال)?مادة\s*"
                 r"(?:\(\s*[\u0660-\u0669\d]{1,2}\s*\)\s*)?[-\u2013\u2014:]?\s*"
                 r"(?P<num>[\u0660-\u0669\d]{1,4})"
                 r"(?P<suffix>\s*مكرر(?:\s*ا)?)?\s*[-\u2013\u2014:]?\s*")
RTL = re.compile(r"(?<!ال)مادة\s*\)\s*"
                 r"(?P<num>[\u0660-\u0669\u06F0-\u06F9\d]{1,4})"
                 r"(?P<suffix>\s*مكرر(?:\s*ا)?)?"
                 r"\s*\(\s*:")

def split_articles(text):
    text = norm(text)
    rx = RTL if len(RTL.findall(text)) > len(STD.findall(text)) else STD
    ms = list(rx.finditer(text))
    order, seen = [], {}
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        body = re.sub(r"\s{2,}", " ", text[m.end():end].replace("\n", " ")).strip()
        if len(body) < 25 or re.fullmatch(r"ملغاة[\s.]*", body):
            continue
        n = m.group("num").translate(DIG).strip()
        sfx = (m.groupdict().get("suffix") or "").strip()
        key = (n + " " + sfx).strip()
        if key not in seen or len(body) > len(seen[key]):
            seen[key] = body
            order.append(key)
    return [{"n": k, "t": seen[k]} for k in dict.fromkeys(order)]

def read_pdf(path):
    p = Path(path)
    raw = p.read_bytes()
    end = raw.rfind(b"%%EOF")
    if end > 0 and len(raw) - (end + 5) > 1000:
        p = p.with_name("repaired_" + p.name)
        p.write_bytes(raw[:end + 5])
        print("    repaired truncated PDF")
    return "\n".join(pg.extract_text() or "" for pg in PdfReader(str(p)).pages)

sys.path.insert(0, "backend")
from app.database import SessionLocal
from app.models.legal import Law, Article

db = SessionLocal()
total = 0
for path, num, yr, cat, title in TARGETS:
    if not Path(path).exists():
        print("MISSING:", path)
        continue
    print(Path(path).name)
    arts = split_articles(read_pdf(path))
    print("   ", len(arts), "articles")
    if not arts:
        continue
    old = db.query(Law).filter(Law.law_number == num, Law.year == yr).first()
    if old:
        db.query(Article).filter(Article.law_id == old.id).delete()
        db.delete(old)
        db.flush()
    law = Law(law_number=num, year=yr, category=cat, status="active", title=title)
    db.add(law)
    db.flush()
    for i, a in enumerate(arts):
        db.add(Article(law_id=law.id, article_number=a["n"],
                       text=a["t"], order_index=i))
    total += len(arts)

db.commit()
db.close()
print("\nImported", total, "articles. Restart the backend.")