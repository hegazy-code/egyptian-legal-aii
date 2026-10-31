import re, shutil, pathlib
root = pathlib.Path.cwd()

p = root / "frontend/app/ask/page.tsx"
b = p.with_suffix(".tsx.bak4")
if not b.exists(): shutil.copy(p, b)
s = p.read_text(encoding="utf-8-sig")
s, n1 = re.subn(r'[ \t]*<Disclaimer />[ \t]*\r?\n', '', s)
s, n2 = re.subn(r'import Disclaimer from "@/components/Disclaimer";[ \t]*\r?\n', '', s)
print(("OK     " if n1 >= 1 else "FAILED ") + "removed <Disclaimer /> (%d)" % n1)
print(("OK     " if n2 >= 1 else "FAILED ") + "removed unused import")
p.write_text(s, encoding="utf-8")

p = root / "frontend/app/layout.tsx"
b = p.with_suffix(".tsx.bak4")
if not b.exists(): shutil.copy(p, b)
s = p.read_text(encoding="utf-8-sig")
new_p = ('<p className="max-w-2xl text-xl font-bold leading-[1.8] text-ink">'
         '<span className="text-seal">معلومات قانونية عامة</span>، وليست استشارة قانونية</p>')
s, n3 = re.subn(r'<p className="max-w-2xl text-sm leading-\[1\.9\] text-muted">.*?</p>', lambda m: new_p, s, count=1, flags=re.S)
print(("OK     " if n3 == 1 else "FAILED ") + "footer disclaimer text")
p.write_text(s, encoding="utf-8")
print("FINISHED")
