import re, shutil, pathlib
root = pathlib.Path.cwd()

def rd(rel):
    p = root / rel
    b = p.with_name(p.name + ".bak_all")
    if not b.exists(): shutil.copy(p, b)
    return p, p.read_text(encoding="utf-8-sig")

def report(ok, already, label):
    print(("ALREADY " if already else ("OK      " if ok else "FAILED  ")) + label)

# ===== 1) front end: timeout 30s -> 120s
p, s = rd("frontend/lib/api.ts")
if "120_000" in s:
    report(True, True, "timeout 120s")
elif "30_000" in s:
    p.write_text(s.replace("30_000", "120_000"), encoding="utf-8"); report(True, False, "timeout 120s")
else:
    report(False, False, "timeout (DEFAULT_TIMEOUT_MS not found)")

# ===== 2) /ask page: remove the yellow box, set the headline
p, s = rd("frontend/app/ask/page.tsx")
s, n1 = re.subn(r'[ \t]*<Disclaimer />[ \t]*\r?\n', '', s)
s, n2 = re.subn(r'import Disclaimer from "@/components/Disclaimer";[ \t]*\r?\n', '', s)
report(True, n1 == 0, "/ask: yellow box removed")
HEAD = "أنا أضع النص. غيري يضع الظنّ."
s, n3 = re.subn(r'(<h1 className="[^"]*">).*?(</h1>)', lambda m: m.group(1) + HEAD + m.group(2), s, count=1, flags=re.S)
report(n3 == 1, False, "/ask: headline")
p.write_text(s, encoding="utf-8")

# ===== 3) footer: short disclaimer, bold
p, s = rd("frontend/app/layout.tsx")
new_p = ('<p className="max-w-2xl text-xl font-bold leading-[1.8] text-ink">'
         '<span className="text-seal">معلومات قانونية</span>، وليست استشارة قانونية</p>')
pat = r'<p className="max-w-2xl text-(?:sm leading-\[1\.9\] text-muted|xl font-bold leading-\[1\.8\] text-ink)">.*?</p>'
s, n = re.subn(pat, lambda m: new_p, s, count=1, flags=re.S)
report(n == 1, False, "footer disclaimer")
p.write_text(s, encoding="utf-8")

# ===== 4) home: headline + slogan band
p, s = rd("frontend/app/page.tsx")
s, n = re.subn(r'(<h1 className="[^"]*">).*?(</h1>)',
               lambda m: m.group(1) + "\n          أنا أضع النص.\n          <br />\n          غيري يضع الظنّ.\n        " + m.group(2),
               s, count=1, flags=re.S)
report(n == 1, False, "home headline")
NEW = "مش معنى إنك عملتها يبقى إنت مذنب."
OLD = "عندي المادة. وعند غيري الرأي."
anchor = '<section className="mt-12 bg-ink text-[#F4F1EC]">'
band = ('<section className="mt-12 border-y-[1.5px] border-ink bg-paper-deep">\n'
        '        <div className="mx-auto max-w-6xl px-6 py-14 text-center">\n'
        '          <p className="font-legal text-4xl font-bold leading-[1.4] text-seal sm:text-6xl">' + NEW + '</p>\n'
        '        </div>\n      </section>\n\n      <section className="bg-ink text-[#F4F1EC]">')
if NEW in s:
    report(True, True, "home slogan band")
elif OLD in s:
    s = s.replace(OLD, NEW, 1); report(True, False, "home slogan band (text replaced)")
elif anchor in s:
    s = s.replace(anchor, band, 1); report(True, False, "home slogan band (added)")
else:
    report(False, False, "home slogan band (anchor not found)")
p.write_text(s, encoding="utf-8")

# ===== 5) backend: citation matching + colloquial query expansion
p, s = rd("backend/app/rag/postprocess.py")
old = '_ART_TITLE = re.compile(r"المادة\\s*([~\\d٠-٩]+)")'
new = '_ART_TITLE = re.compile(r"المادة\\s*(.+?)\\s*[-–—]\\s")'
if new in s: report(True, True, "backend: title regex")
elif old in s: s = s.replace(old, new, 1); report(True, False, "backend: title regex")
else: report(False, False, "backend: title regex")

NUM_NEW = '''def _num(s):
    t = str(s or "").translate(_AR_DIGITS)
    t = re.sub(r"^\\s*(?:ال)?مادة\\s*", "", t)
    t = re.sub(r"[\\u064B-\\u0652~]", "", t)
    t = re.sub(r"مكرر[ا]?", "مكرر", t)
    t = re.sub(r"(أولا|ثانيا|ثالثا|رابعا)", lambda m: m.group(1) + "ً", t)
    return re.sub(r"\\s+", " ", t).strip()
'''
if 'r"^\\s*(?:ال)?مادة\\s*"' in s:
    report(True, True, "backend: article-number normaliser")
else:
    s, n2 = re.subn(r'def _num\(s\):\n    return .*\n', lambda m: NUM_NEW, s, count=1)
    report(n2 == 1, False, "backend: article-number normaliser")

if "def expand_query" in s:
    report(True, True, "backend: query expansion")
else:
    s += '''

_W = r"(?<![\\u0600-\\u06FF])"
_EXPAND = [
    (_W + r"(?:سرق|سرقة|سارق|موبايل|محفظة|شنطة|نشل)", "السرقة اختلس منقولا مملوكا لغيره سارق السرقات"),
    (_W + r"(?:ضرب|اتضرب|اعتد|إصاب|اصاب|مشاجر|خناق)", "الضرب الجرح عمدا إيذاء الأشغال الشخصية"),
    (_W + r"(?:نصب|احتيال|نصاب|استولى)", "النصب الاحتيال الاستيلاء على نقود"),
    (_W + r"(?:ابتز|هدد|تهديد|بيهدد)", "التهديد الحصول بالتهديد على مبلغ من النقود"),
    (_W + r"(?:قتل|قتله)", "القتل عمدا"),
    (_W + r"(?:سب|شتم|قذف|اهان|إهان)", "السب القذف خدش الشرف والاعتبار"),
    (_W + r"(?:تحرش|معاكس)", "التعرض للغير إيحاءات جنسية التحرش"),
    (_W + r"(?:تزوير|مزور|زور)", "التزوير محرر مزور"),
    (_W + r"(?:خيانة|وصل امانة|وصل أمانة|إيصال أمانة|ايصال امانة)", "خيانة الأمانة اختلس بدد وديعة"),
    (_W + r"(?:اختراق|هاك|هكر|حسابي|فيسبوك|واتساب)", "الدخول غير المشروع النظام المعلوماتي الحساب الخاص"),
    (_W + r"(?:صور|فيديو|تسريب)", "الاعتداء على حرمة الحياة الخاصة الصور المحادثات"),
]


def expand_query(q):
    q = q or ""
    extra = [e for pat, e in _EXPAND if re.search(pat, q)]
    return (q + " " + " ".join(extra)).strip() if extra else q
'''
    report(True, False, "backend: query expansion")
ns = {}
exec(compile(s, "postprocess_check", "exec"), ns)
for pat, e in ns["_EXPAND"]:
    re.compile(pat)
    assert "?" not in e, "corrupted Arabic detected - nothing written"
p.write_text(s, encoding="utf-8")

p, s = rd("backend/app/services/chat_service.py")
o1 = "from app.rag.postprocess import rerank_for_question, finalize_answer"
n1_ = "from app.rag.postprocess import rerank_for_question, finalize_answer, expand_query"
o2 = "hybrid_search(self.db, question, limit=40, legal_area=legal_area)"
n2_ = "hybrid_search(self.db, expand_query(question), limit=40, legal_area=legal_area)"
for o, n, name in ((o1, n1_, "import"), (o2, n2_, "search call")):
    if n in s: report(True, True, "backend: chat_service " + name)
    elif o in s: s = s.replace(o, n, 1); report(True, False, "backend: chat_service " + name)
    else: report(False, False, "backend: chat_service " + name)
p.write_text(s, encoding="utf-8")
print("FINISHED")
