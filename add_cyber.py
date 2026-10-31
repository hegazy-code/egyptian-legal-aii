import re, shutil, pathlib, urllib.request, urllib.parse
root = pathlib.Path.cwd()

# --- 1) keyword / summary patch ---
p = root / "backend/app/rag/postprocess.py"
b = p.with_suffix(".py.bak")
if not b.exists(): shutil.copy(p, b)
s = p.read_text(encoding="utf-8")
edits = [
 ('["الإيجار", "ايجار", "إيجار"]', '["تأجير", "الإيجار", "ايجار", "إيجار"]'),
 ('["تقنية المعلومات", "جرائم تقنية", "العقوبات"]', '["تقنية المعلومات", "المعلوماتية", "العقوبات"]'),
 ('r"ابتزاز|تهديد|اختراق|انترنت|إنترنت|قذف|جريمة إلكترونية"', 'r"ابتزاز|تهديد|اختراق|انترنت|إنترنت|قذف|جريمة إلكترونية|فيسبوك|واتساب|حسابي|صوري|صور"'),
 ('len(t) <= 450', 'len(t) <= 300'),
 ('    return " ".join(parts[:2])', '    out = " ".join(parts[:2])\n    return parts[0] if len(out) > 330 and len(parts[0]) > 40 else out'),
 ('_WARN = " (', '_TYPOS = {"القحمة": "المحكمة", "المحكة": "المحكمة"}\n_WARN = " ('),
 ('    return _STRAY.sub("", t) if isinstance(t, str) else t',
  '    if not isinstance(t, str):\n        return t\n    t = _STRAY.sub("", t)\n    for a, b in _TYPOS.items():\n        t = t.replace(a, b)\n    return t'),
]
for old, new in edits:
    if old in s:
        s = s.replace(old, new, 1); print("OK      " + old[:36])
    elif new in s:
        print("ALREADY " + old[:36])
    else:
        print("FAILED  " + old[:36])
p.write_text(s, encoding="utf-8")

# --- 2) download the official Cybercrime Law PDF ---
url = "https://fra.gov.eg/wp-content/uploads/2025/01/قانون-رقم-175-لسنة-2018-بتاريخ-2018-08-14.pdf"
dest = pathlib.Path.home() / "Downloads" / "law-175-2018.pdf"
try:
    if not dest.exists():
        req = urllib.request.Request(urllib.parse.quote(url, safe=":/"), headers={"User-Agent": "Mozilla/5.0"})
        dest.write_bytes(urllib.request.urlopen(req, timeout=90).read())
    print("DOWNLOAD OK", dest.stat().st_size, "bytes")
except Exception as e:
    print("DOWNLOAD FAILED:", e)
    raise SystemExit(1)

# --- 3) load it with your existing build_laws.py logic ---
src = (root / "build_laws.py").read_text(encoding="utf-8")
new_targets = 'TARGETS = [\n    (r"%s", "175", 2018, "cybercrime", "قانون مكافحة جرائم تقنية المعلومات رقم 175 لسنة 2018"),\n]\n' % dest
src2, n = re.subn(r"TARGETS = \[.*?\n\]\n", lambda m: new_targets, src, count=1, flags=re.S)
print("TARGETS replaced:", n == 1)
exec(compile(src2, "build_laws_run", "exec"), {"__name__": "__main__"})
print("FINISHED")
