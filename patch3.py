import re, shutil, pathlib
root = pathlib.Path.cwd()

p = root / "backend/app/rag/postprocess.py"
b = p.with_suffix(".py.bak3")
if not b.exists(): shutil.copy(p, b)
s = p.read_text(encoding="utf-8-sig")

old = '_ART_TITLE = re.compile(r"المادة\\s*([~\\d٠-٩]+)")'
new = '_ART_TITLE = re.compile(r"المادة\\s*(.+?)\\s*[-–—]\\s")'
print(("OK     " if old in s else "FAILED ") + "title regex")
s = s.replace(old, new, 1)

NUM_NEW = '''def _num(s):
    t = str(s or "").translate(_AR_DIGITS)
    t = re.sub(r"^\\s*(?:ال)?مادة\\s*", "", t)
    t = re.sub(r"[\\u064B-\\u0652~]", "", t)
    t = re.sub(r"مكرر[ا]?", "مكرر", t)
    t = re.sub(r"(أولا|ثانيا|ثالثا|رابعا)", lambda m: m.group(1) + "ً", t)
    return re.sub(r"\\s+", " ", t).strip()
'''
s, n2 = re.subn(r'def _num\(s\):\n    return .*\n', lambda m: NUM_NEW, s, count=1)
print(("OK     " if n2 == 1 else "FAILED ") + "_num normaliser")

if "def expand_query" not in s:
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
    print("OK     expand_query added")
else:
    print("ALREADY expand_query")
ns = {}
exec(compile(s, "postprocess_check", "exec"), ns)
for pat, e in ns["_EXPAND"]:
    re.compile(pat)
    assert "?" not in e, "corrupted text detected"
p.write_text(s, encoding="utf-8")

p = root / "backend/app/services/chat_service.py"
b = p.with_suffix(".py.bak3")
if not b.exists(): shutil.copy(p, b)
s = p.read_text(encoding="utf-8-sig")
old1 = "from app.rag.postprocess import rerank_for_question, finalize_answer"
new1 = "from app.rag.postprocess import rerank_for_question, finalize_answer, expand_query"
old2 = "hybrid_search(self.db, question, limit=40, legal_area=legal_area)"
new2 = "hybrid_search(self.db, expand_query(question), limit=40, legal_area=legal_area)"
for o, n, name in ((old1, new1, "import"), (old2, new2, "search call")):
    if o in s:
        s = s.replace(o, n, 1); print("OK      chat_service " + name)
    elif n in s:
        print("ALREADY chat_service " + name)
    else:
        print("FAILED  chat_service " + name)
p.write_text(s, encoding="utf-8")
print("FINISHED")
