"""Split a flat 'code table' text (heading words + article number + text, repeated per row) into articles.

Candidates = integer tokens that look like article numbers; the real article numbers form the longest
increasing sequence (by number, then 'مكرر' rank) over the text, so spurious numbers inside article text
(amounts, years, enumerations) are dropped.
"""
import bisect
import re

REJECT_BEFORE = {"المادة","المواد","مادة","رقم","و","من","الى","إلى","بين","تجاوز","تقل","تزيد","عن","على","فى","في","بعد","قبل","حتى","مبلغ","بمبلغ","غرامة","بغرامة","الفقرة","البند","بند","القانون","قانون","لسنة","سنة","عام","نحو","قدره","قدرها","مقدار","يوم","يوما","نسبة","بنسبة","البابين","الباب","الفصل","الكتاب","ال"}
REJECT_AFTER = re.compile(r"^(?:جنيه|جنيها|جنيهات|يوم|يوما|ايام|اشهر|شهر|اسبوع|سنة|سنوات|سنه|عاما|اعوام|ساعة|ساعات|%|فى الالف|في الالف|فى المائة|فى المئة|بالمائة|مرة|مرات|متر|كيلو|مليم|الف|الاف|ألف|قرش|قروش|من هذا|من القانون|لسنة|\)|-\s*\d)")
RANKS = {"": 0, "مكرر": 1, "ثانيا": 2, "ثانياً": 2, "ثالثا": 3, "ثالثاً": 3, "رابعا": 4, "رابعاً": 4, "خامسا": 5, "سادسا": 6, "سابعا": 7, "ثامنا": 8, "تاسعا": 9, "عاشرا": 10}
TOKEN = re.compile(r"(?<![\d/(\-])(\d{1,4})((?:\s*مكرر(?:ا|اً)?(?:\s*(?:ثانيا|ثانياً|ثالثا|ثالثاً|رابعا|رابعاً|خامسا|سادسا|سابعا|ثامنا|تاسعا|عاشرا))?)?)(?=\s)")

def _rank(suffix):
    words = suffix.split()
    if not words: return 0
    r = 1
    for w in words[1:]:
        r = RANKS.get(w, r)
    return r

def candidates(text, max_n):
    out = []
    for m in TOKEN.finditer(text):
        n = int(m.group(1))
        if n < 1 or n > max_n: continue
        before = text[max(0, m.start()-25):m.start()].split()
        prev = before[-1] if before else ""
        after = text[m.end():m.end()+16].lstrip()
        if prev in REJECT_BEFORE or prev.endswith("(") : continue
        if REJECT_AFTER.match(after): continue
        out.append((m.start(), m.end(), (n, _rank(m.group(2))), re.sub(r"\s+", " ", m.group(0)).strip()))
    return out

def split_articles(text, max_n=1000):
    cands = candidates(text, max_n)
    # longest strictly increasing subsequence on key (n, rank)
    tails, tails_idx, prev = [], [], [-1]*len(cands)
    for i, c in enumerate(cands):
        k = c[2]
        j = bisect.bisect_left(tails, k)
        if j == len(tails): tails.append(k); tails_idx.append(i)
        else: tails[j] = k; tails_idx[j] = i
        prev[i] = tails_idx[j-1] if j > 0 else -1
    seq, i = [], tails_idx[-1] if tails_idx else -1
    while i != -1:
        seq.append(cands[i]); i = prev[i]
    seq.reverse()
    out = []
    for idx, (s, e, key, label) in enumerate(seq):
        nxt = seq[idx+1][0] if idx+1 < len(seq) else len(text)
        out.append((label, text[e:nxt].strip()))
    return out


def attach_chapters(arts, min_words=2, max_words=14, min_freq=2):
    """The body of article i ends with the heading words of article i+1 (table layout).
    Strip those trailing headings; return [{number, chapter, text}] with chapter = heading of that article."""
    from collections import Counter
    def suffixes(words):
        for k in range(min_words, min(max_words, len(words)) + 1):
            yield " ".join(words[-k:])
    cnt = Counter()
    for _, body in arts:
        for s in set(suffixes(body.split())):
            cnt[s] += 1
    trailing = []  # heading found at the end of each body
    cleaned = []
    for _, body in arts:
        words = body.split()
        best = None
        for s in suffixes(words):
            if cnt[s] >= min_freq:
                best = s
        if best:
            body = body[: len(body) - len(best)].rstrip(" .-/") if body.endswith(best) else body
        trailing.append(best or "")
        cleaned.append(body.strip())
    out = []
    for i, ((label, _), body) in enumerate(zip(arts, cleaned)):
        chapter = trailing[i-1] if i > 0 else ""
        out.append({"number": label, "chapter": chapter, "text": body})
    return out


# ---- keyword mode: "مادة 12 - ..." / "المادة (12)" ----
KW_TOKEN = re.compile(r"(?:^|(?<=\s)|(?<=[\.\-–:؛،]))(?:ال)?ماد[ةه]\s*(?:رقم\s*)?\(?\s*(\d{1,4})\s*\)?((?:\s*مكرر(?:ا|اً)?(?:\s*(?:ثانيا|ثانياً|ثالثا|ثالثاً|رابعا|رابعاً|خامسا|سادسا|سابعا|ثامنا|تاسعا|عاشرا|\(\s*[أ-ي]\s*\)))?)?)")

def split_keyword(text, max_n=1500):
    cands = []
    for m in KW_TOKEN.finditer(text):
        n = int(m.group(1))
        if n < 1 or n > max_n: continue
        after = text[m.end():m.end()+6].lstrip()
        # a heading-like article start is followed by punctuation or text, but "المادة 5 من" is a reference
        if re.match(r"^(?:من|فى|في|و|او|أو|الى|إلى|السابقة|المذكورة)\b", after) and not re.match(r"^[\-–:\.]", after):
            continue
        cands.append((m.start(), m.end(), (n, _rank(m.group(2))), re.sub(r"\s+", " ", m.group(0)).strip()))
    tails, tails_idx, prev = [], [], [-1]*len(cands)
    for i, c in enumerate(cands):
        k = c[2]
        j = bisect.bisect_left(tails, k)
        if j == len(tails): tails.append(k); tails_idx.append(i)
        else: tails[j] = k; tails_idx[j] = i
        prev[i] = tails_idx[j-1] if j > 0 else -1
    seq, i = [], tails_idx[-1] if tails_idx else -1
    while i != -1:
        seq.append(cands[i]); i = prev[i]
    seq.reverse()
    out = []
    for idx, (s, e, key, label) in enumerate(seq):
        nxt = seq[idx+1][0] if idx+1 < len(seq) else len(text)
        num = re.sub(r"^(?:ال)?ماد[ةه]\s*(?:رقم\s*)?\(?\s*", "", label).replace(")", "").strip()
        out.append((num, text[e:nxt].strip(" -–:.\n")))
    return out

def chunk_paragraphs(text, size=900):
    """Fallback for non-article texts (explanations, encyclopedias): ~size-char chunks on sentence boundaries."""
    parts, buf, k = [], "", 1
    for sent in re.split(r"(?<=[\.\!\?؟])\s+", text):
        if len(buf) + len(sent) > size and buf:
            parts.append((f"فقرة {k}", buf.strip())); k += 1; buf = ""
        buf += sent + " "
    if buf.strip(): parts.append((f"فقرة {k}", buf.strip()))
    return parts
