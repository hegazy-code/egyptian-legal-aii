# -*- coding: utf-8 -*-
"""
add_laws_web.py — يسحب النص الرسمي النظيف للقوانين من اللينكات ويحمّلها في legal_ai.db مباشرة.

شغّله من داخل فولدر backend:
    python add_laws_web.py

- محتاج إنترنت عادي بس. مفيش OCR ومفيش مكتبات خارجية.
- بيستبدل أي stubs قديمة بنفس رقم القانون (مش بيكرر).
- الإجراءات الجنائية: بيحمّل القديم 150/1950 (الساري فعلاً لحد أكتوبر 2027، بآخر تعديل يناير 2024).
  القديم ما بيتشالش. الجديد 174/2025 (مؤجّل) نضيفه بعدين لو حبيت.
- آمن: كل قانون في transaction لوحده.
- بعد ما يخلّص: ابعت الناتج (سطر لكل قانون) عشان أظبط أي قانون طلّع عدد غلط.
"""
import sqlite3, os, sys, re, json, uuid, time, html as _html, datetime, glob
import urllib.request, urllib.parse

DB  = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "legal_ai.db")
WS_API = "https://ar.wikisource.org/w/api.php"
UA = {"User-Agent": "EgyLegalLoader/3.0 (personal use)"}
DIG = str.maketrans('٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹', '01234567890123456789')

# kind: "ws_title" عنوان ويكي مصدر بالظبط | "ws_search" بحث ويكي مصدر | "html" صفحة ويب عادية
LAWS = [
    dict(num="150", year=1950, cat="criminal_procedure",
         title="قانون الإجراءات الجنائية رقم 150 لسنة 1950 (معمول به — آخر تعديل يناير 2024)",
         kind="html",
         src="https://alberonsy.com/%D9%82%D8%A7%D9%86%D9%88%D9%86-%D8%B1%D9%82%D9%85-%DB%B1%D9%A5%DB%B0-%D9%84%D8%B3%D9%86%D8%A9-%DB%B1%DB%B9%D9%A5%DB%B0-%D9%82%D8%A7%D9%86%D9%88%D9%86-%D8%B1%D9%82%D9%85-150-%D9%84%D8%B3%D9%86%D8%A9-19/"),
    dict(num="82",  year=2002, cat="intellectual_property",
         title="قانون حماية حقوق الملكية الفكرية رقم 82 لسنة 2002",
         kind="ws_title",  src="قانون 82 لسنة 2002 - مصر"),
    dict(num="1",   year=2000, cat="family",
         title="قانون تنظيم بعض أوضاع وإجراءات التقاضي في مسائل الأحوال الشخصية رقم 1 لسنة 2000",
         kind="ws_title",  src="قانون رقم 1 لسنة 2000 - مصر"),
    dict(num="13",  year=1968, cat="civil_procedure",
         title="قانون المرافعات المدنية والتجارية رقم 13 لسنة 1968 (آخر تعديل يوليو 2024)",
         kind="html",
         src="https://alberonsy.com/%d9%82%d8%a7%d9%86%d9%88%d9%86-%d8%b1%d9%82%d9%85-%db%b1%db%b3-%d9%84%d8%b3%d9%86%d8%a9-%db%b1%db%b9%d9%a6%db%b8-%d9%82%d8%a7%d9%86%d9%88%d9%86-%d8%b1%d9%82%d9%85-13-%d9%84%d8%b3%d9%86%d8%a9-1968-%d8%a8%d8%a5%d8%b5%d8%af%d8%a7%d8%b1-%d9%82%d8%a7%d9%86%d9%88%d9%86-%d8%a7%d9%84%d9%85%d8%b1%d8%a7%d9%81%d8%b9%d8%a7%d8%aa-%d8%a7%d9%84%d9%85%d8%af%d9%86%d9%8a%d8%a9-%d9%88%d8%a7%d9%84%d8%aa%d8%ac%d8%a7%d8%b1%d9%8a%d8%a9-%d9%88%d9%81%d9%82%d8%a7%d9%8b-%d9%84%d8%a2%d8%ae%d8%b1-%d8%aa%d8%b9%d8%af%d9%8a%d9%84-%d8%b5%d8%a7%d8%af%d8%b1-%d9%81%d9%8a-10-%d9%8a%d9%88%d9%84%d9%8a%d8%a9-%d8%b9%d8%a7%d9%85-2024/"),
    dict(num="17",  year=1999, cat="commercial",
         title="قانون التجارة رقم 17 لسنة 1999",
         kind="html",      src="https://lawhub.info/eg/?p=11582"),
    dict(num="181", year=2018, cat="consumer",
         title="قانون حماية المستهلك رقم 181 لسنة 2018",
         kind="html",      src="https://egyptlaw.ai/ar/laws/eg-egyptian-consumer-protection-law-law-181-2018"),
]

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode("utf-8", "replace")

def ws_api(params):
    params["format"] = "json"
    return json.loads(fetch(WS_API + "?" + urllib.parse.urlencode(params)))

def ws_find_title(q):
    hits = ws_api({"action": "query", "list": "search", "srsearch": q, "srlimit": 5}).get("query", {}).get("search", [])
    return hits[0]["title"] if hits else None

def ws_wikitext(title):
    return ws_api({"action": "parse", "page": title, "prop": "wikitext"}).get("parse", {}).get("wikitext", {}).get("*", "")

def clean_wiki(t):
    t = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", t)
    t = re.sub(r"\{\{[^{}]*\}\}", "", t); t = re.sub(r"'''?", "", t)
    t = re.sub(r"<[^>]+>", "", t); t = re.sub(r"^\s*[\*#:]+\s?", "", t, flags=re.M)
    t = re.sub(r"[ \t]{2,}", " ", t); t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()

def html_to_text(h):
    h = re.sub(r"(?is)<script.*?</script>", " ", h)
    h = re.sub(r"(?is)<style.*?</style>", " ", h)
    h = re.sub(r"(?is)<(p|div|br|li|h[1-6]|tr)[^>]*>", "\n", h)
    h = re.sub(r"<[^>]+>", " ", h); h = _html.unescape(h)
    h = re.sub(r"[ \t]{2,}", " ", h); h = re.sub(r"\n{2,}", "\n", h)
    return h.strip()

SUF = r"(مكرر[ًةا]?(?:\s*[/(]\s*[أ-ي]\s*\)?)*)?"   # مكرر / مكرر أ / مكرر ب ...

def split_articles_wikitext(wt):
    pat = re.compile(r"^\s*=+\s*(?:ال)?مادة\s*\(?\s*([0-9٠-٩۰-۹]+)\s*\)?\s*" + SUF + r"\s*=+\s*$", re.M)
    hs = [(int(m.group(1).translate(DIG)), (m.group(2) or "").strip(), m.start(), m.end()) for m in pat.finditer(wt)]
    out = []
    for i, (n, suf, s, e) in enumerate(hs):
        nxt = hs[i + 1][2] if i + 1 < len(hs) else len(wt)
        body = clean_wiki(wt[e:nxt])
        if len(body) > 10:
            out.append(((f"{n} {suf}".strip()), body))
    return out

def split_articles_text(txt):
    pat = re.compile(r"(?:^|\n)\s*(?:ال)?ماد[ةه]\s*(?:رقم\s*)?\(?\s*([0-9٠-٩۰-۹]+)\s*" + SUF + r"\s*\)?\s*[\.\:\-]?", re.M)
    hs = [(int(m.group(1).translate(DIG)), (m.group(2) or "").strip(), m.start(), m.end()) for m in pat.finditer(txt)]
    best = {}
    for i, (n, suf, s, e) in enumerate(hs):
        nxt = hs[i + 1][2] if i + 1 < len(hs) else len(txt)
        body = txt[e:nxt]
        body = re.sub(r"(?m)^\s*[\*\-–—_]{2,}\s*$", "", body)   # شيل سطور الفواصل
        body = re.sub(r"\n{2,}", "\n", body).strip()
        if len(body) >= 15:
            best[(n, suf)] = body                              # نثبت على آخر نسخة للرقم المطبوع
    return [((f"{n} {suf}").strip(), b)
            for (n, suf), b in sorted(best.items(), key=lambda kv: (kv[0][0], kv[0][1] != ""))]

def get_articles(law):
    if law["kind"] == "ws_title":
        return split_articles_wikitext(ws_wikitext(law["src"]))
    if law["kind"] == "ws_search":
        t = ws_find_title(law["src"])
        if not t: raise RuntimeError("مفيش صفحة ويكي مصدر: " + law["src"])
        return split_articles_wikitext(ws_wikitext(t))
    if law["kind"] == "html":
        return split_articles_text(html_to_text(fetch(law["src"])))
    raise RuntimeError("نوع غير معروف: " + law["kind"])

HERE = os.path.dirname(os.path.abspath(__file__))

# (1) اسحب كل القوانين من النت مرة واحدة
print(">> جاري سحب القوانين من النت...")
fetched = []
for law in LAWS:
    try:
        arts = get_articles(law)
        if len(arts) < 5:
            print(f"   ⚠ {law['title']}: {len(arts)} مادة بس — اتعدّى."); continue
        fetched.append((law, arts))
        print(f"   ✓ {law['title']}: {len(arts)} مادة")
    except Exception as ex:
        print(f"   ✗ فشل سحب {law['title']}: {ex}")
    time.sleep(1)

# (2) برضه حمّل أي ملفات lawdata_*.json جنب السكريبت (المدني، العمل لو موجودين)
for f in sorted(glob.glob(os.path.join(HERE, "lawdata_*.json"))):
    try:
        d = json.load(open(f, encoding="utf-8"))
        law = {"num": str(d["law_number"]), "year": d.get("year", 0),
               "cat": d.get("category"), "title": d["title"]}
        arts = [(str(a["article_number"]), a["text"]) for a in d["articles"]]
        if len(arts) >= 5:
            fetched.append((law, arts))
            print(f"   ✓ (ملف) {law['title']}: {len(arts)} مادة")
    except Exception as ex:
        print(f"   ✗ فشل قراءة {os.path.basename(f)}: {ex}")

if not fetched:
    sys.exit("مفيش أي قانون اتسحب. اتأكد من الإنترنت وجرّب تاني.")

# (3) دوّر على كل ملفات legal_ai.db في المشروع كله
def find_dbs():
    root = HERE
    for _ in range(4):                       # اطلع لفوق لحد جذر المشروع
        if os.path.basename(root).lower().startswith("egyptian-legal-ai"): break
        parent = os.path.dirname(root)
        if parent == root: break
        root = parent
    dbs = []
    for dp, dn, fn in os.walk(root):
        low = dp.lower()
        if any(s in low for s in ("node_modules", ".git", ".next", "__pycache__", "site-packages")):
            dn[:] = []; continue
        if "legal_ai.db" in fn:
            dbs.append(os.path.join(dp, "legal_ai.db"))
    if not dbs and os.path.exists(os.path.join(HERE, "legal_ai.db")):
        dbs.append(os.path.join(HERE, "legal_ai.db"))
    return sorted(set(dbs))

def now(): return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")

def load_into(dbpath):
    con = sqlite3.connect(dbpath); cur = con.cursor()
    tabs = {r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if "laws" not in tabs or "articles" not in tabs:
        con.close(); return None
    LC = {r[1] for r in cur.execute("PRAGMA table_info(laws)")}
    AC = {r[1] for r in cur.execute("PRAGMA table_info(articles)")}
    for junk in ("أحوال شخصية",):            # شيل stub الأحوال الشخصية القديم المكرر
        for (jid,) in cur.execute("SELECT id FROM laws WHERE law_number=?", (junk,)).fetchall():
            cur.execute("DELETE FROM articles WHERE law_id=?", (jid,))
            cur.execute("DELETE FROM laws WHERE id=?", (jid,))
    def delete_law(num, cat):
        q, p = "SELECT id FROM laws WHERE law_number=?", [str(num)]
        if cat and "category" in LC: q += " AND category=?"; p.append(cat)
        for (lid,) in cur.execute(q, p).fetchall():
            cur.execute("DELETE FROM articles WHERE law_id=?", (lid,))
            cur.execute("DELETE FROM laws WHERE id=?", (lid,))
    loaded = 0
    for law, arts in fetched:
        delete_law(law["num"], law["cat"])
        lid, n = str(uuid.uuid4()), now()
        row = {"id": lid, "law_number": str(law["num"]), "title": law["title"],
               "year": int(law["year"] or 0), "category": law["cat"], "status": "active",
               "created_at": n, "updated_at": n}
        row = {k: v for k, v in row.items() if k in LC}
        cur.execute(f"INSERT INTO laws ({','.join(row)}) VALUES ({','.join('?'*len(row))})", list(row.values()))
        for an, text in arts:
            n2 = now()
            ar = {"id": str(uuid.uuid4()), "law_id": lid, "article_number": an, "text": text,
                  "status": "verified", "created_at": n2, "updated_at": n2}
            ar = {k: v for k, v in ar.items() if k in AC}
            cur.execute(f"INSERT INTO articles ({','.join(ar)}) VALUES ({','.join('?'*len(ar))})", list(ar.values()))
        loaded += 1
    con.commit()
    nl = cur.execute("SELECT COUNT(*) FROM laws").fetchone()[0]
    na = cur.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    con.close()
    return (loaded, nl, na)

dbs = find_dbs()
if not dbs:
    sys.exit("مفيش أي ملف legal_ai.db اتلاقى في المشروع. حط السكريبت جوه مجلد المشروع وجرّب تاني.")
print(f"\n>> لقيت {len(dbs)} قاعدة بيانات، بكتب فيهم كلهم:")
for db in dbs:
    try:
        res = load_into(db)
        if res is None:
            print(f"   (تخطّيت {db} — مش قاعدة قوانين)")
        else:
            loaded, nl, na = res
            print(f"   ✅ {db}")
            print(f"      حمّلت {loaded} قانون → القاعدة دلوقتي: {nl} قانون / {na} مادة")
    except Exception as ex:
        print(f"   ✗ {db}: {ex}")
print("\n>> خلّص. اعمل Ctrl+C للـbackend وشغّله تاني، وقوللي الناتج ده كله.")
