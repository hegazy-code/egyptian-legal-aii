import re, shutil, pathlib
root = pathlib.Path.cwd()
B = root / "backend" / "app"
F = root / "frontend"

def rd(p): return p.read_text(encoding="utf-8")
def wr(p, s): p.write_text(s, encoding="utf-8")
def bak(p):
    b = p.with_suffix(p.suffix + ".bak")
    if p.exists() and not b.exists(): shutil.copy(p, b)
def report(name, ok): print(("OK     " if ok else "FAILED ") + name)

POST = r'''"""Law-aware reranking, citation verification and deadline flagging."""
import re
from typing import Any, Dict, List

_AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
_STOP = {"رقم", "لسنة", "لسنه", "قانون", "القانون", "مادة", "المادة"}

_RULES = [
    (r"فصل|عامل|موظف|صاحب العمل|مرتب|راتب|اجاز|إجاز|نهاية الخدمة|مستحقات|إنذار|انذار|عقد عمل|تأمينات|استقال", ["العمل"]),
    (r"إيجار|ايجار|مؤجر|مستأجر|شقة|شقه|طرد|إخلاء|اخلاء", ["الإيجار", "ايجار", "إيجار"]),
    (r"مستهلك|منتج|استرجاع|ضمان|فاتورة|بضاعة", ["المستهلك"]),
    (r"شيك|كمبيالة|إفلاس|افلاس|تاجر", ["التجارة", "التجاري"]),
    (r"ابتزاز|تهديد|اختراق|انترنت|إنترنت|قذف|جريمة إلكترونية", ["تقنية المعلومات", "جرائم تقنية", "العقوبات"]),
    (r"طلاق|نفقة|حضانة|خلع|زواج|رؤية|أحوال شخصية", ["الأحوال الشخصية", "الاحوال الشخصية", "الأسرة"]),
    (r"سرقة|ضرب|قتل|جنحة|جناية|عقوبة|نصب|احتيال", ["العقوبات"]),
    (r"ملكية فكرية|حق مؤلف|علامة تجارية|براءة", ["الملكية الفكرية"]),
    (r"رفع دعوى|اختصاص|استئناف|نقض|طعن|صحيفة|إعلان", ["المرافعات", "الإجراءات"]),
]

_ART_REF = re.compile(r"(?:المادة|مادة)\s*[\d٠-٩]+")
_ART_TITLE = re.compile(r"المادة\s*([~\d٠-٩]+)")
_DEADLINE = re.compile(r"([\d٠-٩]+)\s*(يوماً|يوما|يوم|أيام|ايام|شهراً|شهرا|شهر|أشهر|اشهر|شهور|سنة|سنوات|سنين|ساعة|ساعات)")
_STRAY = re.compile(r"(?<=[\u0600-\u06FF])[A-Za-z\u0400-\u04FF]+|[A-Za-z\u0400-\u04FF]+(?=[\u0600-\u06FF])")
_WARN = " (⚠ الميعاد غير موثّق من قاعدة النصوص — تحقق منه قبل الاعتماد عليه)"
_NOTE = "\n\nتنبيه: المواعيد والجهات التي لم يرد لها نص في قاعدة النصوص مأخوذة من المعرفة العامة وتحتاج إلى تحقق قبل الاعتماد عليها."


def rerank_for_question(results, question, limit=8):
    """Boost articles of the law the question is actually about."""
    q = question or ""
    if _ART_REF.search(q):
        return list(results)[:limit]
    wanted = []
    for pat, subs in _RULES:
        if re.search(pat, q):
            wanted.extend(subs)

    def key(item):
        i, r = item
        score = float(getattr(r, "score", 0) or 0)
        title = getattr(r, "title", "") or ""
        if wanted and any(s in title for s in wanted):
            score = score * 3 + 5
        return (-score, i)

    ordered = [r for _, r in sorted(enumerate(results), key=key)]
    return ordered[:limit]


def _num(s):
    return str(s or "").translate(_AR_DIGITS).replace("~", "").strip()


def _words(s):
    return set(re.findall(r"[\u0600-\u06FF]{3,}", s or "")) - _STOP


def _clean(t):
    return _STRAY.sub("", t) if isinstance(t, str) else t


def _two_sentences(t):
    if not isinstance(t, str) or len(t) <= 450:
        return t
    parts = re.split(r"(?<=[.!؟?])\s+", t.strip())
    return " ".join(parts[:2])


def finalize_answer(answer: Dict[str, Any], results: List[Any]) -> Dict[str, Any]:
    try:
        index = []
        for r in results:
            title = getattr(r, "title", "") or ""
            m = _ART_TITLE.search(title)
            if m:
                index.append((_num(m.group(1)), title, getattr(r, "snippet", "") or "", m.group(1).startswith("~")))
        corpus = " ".join((getattr(r, "title", "") or "") + " " + (getattr(r, "snippet", "") or "") for r in results).translate(_AR_DIGITS)

        for key in ("relevantLegalTexts", "answerSources"):
            fixed = []
            for c in answer.get(key) or []:
                if not isinstance(c, dict):
                    continue
                num = _num(c.get("articleNumber"))
                hit = next((e for e in index if e[0] == num and (_words(c.get("lawName")) & _words(e[1]))), None)
                if hit:
                    if key == "relevantLegalTexts":
                        c["excerpt"] = hit[2][:600]
                    c["status"] = "unverified" if hit[3] else "verified"
                    c["basis"] = "from_law"
                else:
                    c["status"] = "unverified"
                    c["basis"] = "ai_inference"
                    if key == "relevantLegalTexts":
                        c["excerpt"] = None
                fixed.append(c)
            answer[key] = fixed

        for k in ("understandingOfQuestion", "explanation", "preliminaryApplication"):
            answer[k] = _clean(answer.get(k))
        answer["preliminaryApplication"] = _two_sentences(answer.get("preliminaryApplication"))
        for k in ("missingInformation", "possibleProcedures"):
            answer[k] = [_clean(x) for x in (answer.get(k) or [])]

        def unverified(text):
            for m in _DEADLINE.finditer(text or ""):
                n = m.group(1).translate(_AR_DIGITS)
                if not re.search(re.escape(n) + r"\s*" + re.escape(m.group(2)[:2]), corpus):
                    return True
            return False

        flagged = False
        steps = []
        for s in answer.get("possibleProcedures") or []:
            if isinstance(s, str) and "غير موثّق" not in s and unverified(s):
                s += _WARN
                flagged = True
            steps.append(s)
        answer["possibleProcedures"] = steps
        ex = answer.get("explanation") or ""
        if (unverified(ex) or flagged) and "تنبيه: المواعيد" not in ex:
            answer["explanation"] = ex + _NOTE
    except Exception:
        pass
    return answer
'''

EXTRA = '''
EXTRA_RULES = """
قواعد إضافية صارمة (لها الأولوية على أي تعليمات سابقة):
1. لا تستشهد بأي مادة إلا إذا كانت تنطبق مباشرة على وقائع السؤال. المصادر المسترجعة قد لا تنطبق، فتجاهل ما لا ينطبق. مثال: مادة مسؤولية المتبوع عن أعمال تابعه لا تصلح سنداً لفصل عامل من عمله.
2. في مسائل العمل والفصل والأجور والإجازات ومكافأة نهاية الخدمة: القانون الأساسي هو قانون العمل، ولا يُستند إلى القانون المدني إلا للقواعد العامة عند عدم وجود نص في قانون العمل.
3. لا تذكر أي مدة أو ميعاد (بالأيام أو الأشهر أو السنوات) ولا اسم محكمة أو لجنة أو جهة إلا إذا كان وارداً في النصوص المسترجعة. وإن اضطررت لذكره من معرفتك العامة فاكتب بجانبه: (غير موثّق من قاعدة النصوص — تحقق منه). لا تخترع محاكم أو لجاناً أو إجراءات لا تعرف يقيناً أنها موجودة.
4. حقل preliminaryApplication هو الخلاصة: جملتان كحد أقصى تجيبان عن السؤال مباشرة.
5. لا تكرر المعنى نفسه في explanation؛ كل جملة يجب أن تضيف معلومة جديدة.
6. اكتب النص العربي بحروف عربية فقط، دون أي حروف لاتينية أو سيريلية داخل الكلمات.
7. في possibleProcedures اجعل كل عنصر خطوة واحدة محددة: الجهة، ثم المستندات، ثم الميعاد إن كان موثقاً.
8. إن لم تجد في السياق نصاً ينطبق، اترك relevantLegalTexts فارغة، ولا تملأها بمواد غير منطبقة.
"""
NO_HALLUCINATION_SYSTEM_PROMPT = NO_HALLUCINATION_SYSTEM_PROMPT + EXTRA_RULES


'''

# 1 postprocess module
p = B / "rag" / "postprocess.py"
wr(p, POST); report("create rag/postprocess.py", True)

# 2 keyword.py: stop the 300-row cap from hiding later laws
p = B / "search" / "keyword.py"; bak(p); s = rd(p)
i = s.find("def keyword_search_articles")
ok = i >= 0 and ".limit(300)" in s[i:]
if ok:
    s = s[:i] + s[i:].replace(".limit(300)", ".limit(5000)", 1); wr(p, s)
report("keyword.py candidate cap 300 -> 5000", ok)

# 3 engine.py prompt fixes
p = B / "rag" / "engine.py"; bak(p); s = rd(p)
edits = [
 ("(يجب الاستشهاد بهذا المصدر حرفياً في الإجابة)",
  "(استشهد بهذا المصدر فقط إذا كان ينطبق فعلاً على وقائع السؤال، وإلا تجاهله تماماً)"),
 ("سياق البحث (المصادر القانونية المسترجعة فقط -- لا تستخدم أي معلومة من خارج هذا السياق):",
  "سياق البحث (مصادر مسترجعة من قاعدة النصوص وقد لا تنطبق كلها؛ اعتمد منها ما ينطبق فقط، وما تذكره من معرفتك العامة بالقانون المصري فاذكره على أنه غير موثّق من قاعدتنا):"),
 ("<الشرح التفصيلي للإجابة بناءً على السياق المسترجع فقط>",
  "<الشرح التفصيلي بناءً على السياق المنطبق ومعرفتك بالقانون المصري، دون تكرار>"),
 ("<تطبيق مبدئي على وقائع السؤال المحددة>",
  "<الخلاصة: جملتان كحد أقصى تجيبان مباشرة عن السؤال>"),
]
for old, new in edits:
    ok = old in s
    if ok: s = s.replace(old, new, 1)
    report("engine.py: " + old[:30], ok)
marker = "class GeminiUnavailableError(Exception):"
ok = marker in s and "EXTRA_RULES" not in s
if ok: s = s.replace(marker, EXTRA.lstrip("\n") + marker, 1)
report("engine.py: extra rules", ok)
wr(p, s)

# 4 chat_service.py hook
p = B / "services" / "chat_service.py"; bak(p); s = rd(p)
s, n1 = re.subn(r"^([ \t]*)search_results = hybrid_search\(self\.db, question, limit=8, legal_area=legal_area\)",
    lambda m: (m.group(1) + "from app.rag.postprocess import rerank_for_question, finalize_answer\n" +
               m.group(1) + "search_results = hybrid_search(self.db, question, limit=40, legal_area=legal_area)\n" +
               m.group(1) + "search_results = rerank_for_question(search_results, question, limit=8)"),
    s, count=1, flags=re.M)
s, n2 = re.subn(r"^([ \t]*)answer_dict = answer_builder\.parse_gemini_answer\(raw\)",
    lambda m: (m.group(0) + "\n" + m.group(1) + "answer_dict = finalize_answer(answer_dict, search_results)"),
    s, count=1, flags=re.M)
wr(p, s)
report("chat_service.py rerank hook", n1 == 1); report("chat_service.py finalize hook", n2 == 1)

# 5 frontend badge + sticky box
p = F / "components" / "ChatMessage.tsx"; bak(p); s = rd(p)
old = '  if (/verif/i.test(c.status ?? "")) return { text: "نص موثّق", cls: "border-verified text-verified" };'
new = ('  if (/unverif/i.test(c.status ?? "")) return { text: "غير موثّق من قاعدة النصوص — تحقق منه", cls: "border-[#8A6410] text-[#8A6410]" };\n' + old)
ok = old in s
if ok: wr(p, s.replace(old, new, 1))
report("ChatMessage.tsx badge", ok)
p = F / "app" / "ask" / "page.tsx"; bak(p); s = rd(p)
ok = "sticky bottom-4 border-[1.5px]" in s
if ok: wr(p, s.replace("sticky bottom-4 border-[1.5px]", "border-[1.5px]", 1))
report("ask/page.tsx unpin input", ok)
print("FINISHED")
