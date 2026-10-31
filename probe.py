import re, unicodedata
from pypdf import PdfReader

MARKS = dict.fromkeys([0x200B,0x200C,0x200D,0x200E,0x200F,0x202A,0x202B,
                       0x202C,0x202D,0x202E,0x2066,0x2067,0x2068,0x2069,0xFEFF])

r = PdfReader(r"C:\Users\Yousssef\Downloads\repaired_qnwn_lml_ljdyd_14_lsn_2025_m_q.pdf")
t = "\n".join(p.extract_text() or "" for p in r.pages[:25])
t = unicodedata.normalize("NFKC", t).translate(MARKS).replace("\u0640", "")

print("pages:", len(r.pages), "chars:", len(t))
print("count of مادة:", t.count("مادة"))
print()
for h in re.findall(r".{0,12}مادة.{0,24}", t)[:20]:
    print(repr(h))