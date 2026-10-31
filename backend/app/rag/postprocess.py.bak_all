"""Law-aware reranking, citation verification and deadline flagging."""
import re
from typing import Any, Dict, List

_AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
_STOP = {"رقم", "لسنة", "لسنه", "قانون", "القانون", "مادة", "المادة"}

_RULES = [
    (r"فصل|عامل|موظف|صاحب العمل|مرتب|راتب|اجاز|إجاز|نهاية الخدمة|مستحقات|إنذار|انذار|عقد عمل|تأمينات|استقال", ["العمل"]),
    (r"إيجار|ايجار|مؤجر|مستأجر|شقة|شقه|طرد|إخلاء|اخلاء", ["تأجير", "الإيجار", "ايجار", "إيجار"]),
    (r"مستهلك|منتج|استرجاع|ضمان|فاتورة|بضاعة", ["المستهلك"]),
    (r"شيك|كمبيالة|إفلاس|افلاس|تاجر", ["التجارة", "التجاري"]),
    (r"ابتزاز|تهديد|اختراق|انترنت|إنترنت|قذف|جريمة إلكترونية|فيسبوك|واتساب|حسابي|صوري|صور", ["تقنية المعلومات", "المعلوماتية", "العقوبات"]),
    (r"طلاق|نفقة|حضانة|خلع|زواج|رؤية|أحوال شخصية", ["الأحوال الشخصية", "الاحوال الشخصية", "الأسرة"]),
    (r"سرقة|ضرب|قتل|جنحة|جناية|عقوبة|نصب|احتيال", ["العقوبات"]),
    (r"ملكية فكرية|حق مؤلف|علامة تجارية|براءة", ["الملكية الفكرية"]),
    (r"رفع دعوى|اختصاص|استئناف|نقض|طعن|صحيفة|إعلان", ["المرافعات", "الإجراءات"]),
]

_ART_REF = re.compile(r"(?:المادة|مادة)\s*[\d٠-٩]+")
_ART_TITLE = re.compile(r"المادة\s*(.+?)\s*[-–—]\s")
_DEADLINE = re.compile(r"([\d٠-٩]+)\s*(يوماً|يوما|يوم|أيام|ايام|شهراً|شهرا|شهر|أشهر|اشهر|شهور|سنة|سنوات|سنين|ساعة|ساعات)")
_STRAY = re.compile(r"(?<=[\u0600-\u06FF])[A-Za-z\u0400-\u04FF]+|[A-Za-z\u0400-\u04FF]+(?=[\u0600-\u06FF])")
_TYPOS = {"القحمة": "المحكمة", "المحكة": "المحكمة"}
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
    t = str(s or "").translate(_AR_DIGITS)
    t = re.sub(r"^\s*(?:ال)?مادة\s*", "", t)
    t = re.sub(r"[\u064B-\u0652~]", "", t)
    t = re.sub(r"مكرر[ا]?", "مكرر", t)
    t = re.sub(r"(أولا|ثانيا|ثالثا|رابعا)", lambda m: m.group(1) + "ً", t)
    return re.sub(r"\s+", " ", t).strip()


def _words(s):
    return set(re.findall(r"[\u0600-\u06FF]{3,}", s or "")) - _STOP


def _clean(t):
    if not isinstance(t, str):
        return t
    t = _STRAY.sub("", t)
    for a, b in _TYPOS.items():
        t = t.replace(a, b)
    return t


def _two_sentences(t):
    if not isinstance(t, str) or len(t) <= 300:
        return t
    parts = re.split(r"(?<=[.!؟?])\s+", t.strip())
    out = " ".join(parts[:2])
    return parts[0] if len(out) > 330 and len(parts[0]) > 40 else out


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


_W = r"(?<![\u0600-\u06FF])"
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
