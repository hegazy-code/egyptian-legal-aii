import re, shutil, pathlib
root = pathlib.Path.cwd()

def rd(rel):
    p = root / rel
    b = p.with_name(p.name + ".bak10")
    if not b.exists(): shutil.copy(p, b)
    return p, p.read_text(encoding="utf-8-sig")

p, s = rd("frontend/app/layout.tsx")
old_style = '<p className="max-w-2xl text-sm leading-[1.9] text-muted">معلومات قانونية، وليست استشارة قانونية</p>'
pat = r'<p className="max-w-2xl text-(?:sm leading-\[1\.9\] text-muted|xl font-bold leading-\[1\.8\] text-ink)">.*?</p>'
s, n = re.subn(pat, lambda m: old_style, s, count=1, flags=re.S)
print(("OK     " if n == 1 else "FAILED ") + "footer: old font, text: معلومات قانونية، وليست استشارة قانونية")
p.write_text(s, encoding="utf-8")

p, s = rd("frontend/app/ask/page.tsx")
SLOGAN = "مش معنى إنك عملتها يبقى إنت مذنب."
if SLOGAN in s:
    print("ALREADY /ask slogan")
else:
    anchor = '<div className="space-y-6">'
    add = anchor + '\n          <p className="font-legal text-4xl font-bold leading-[1.4] text-seal">' + SLOGAN + '</p>'
    if anchor in s:
        s = s.replace(anchor, add, 1)
        print("OK     /ask slogan added above the example questions")
    else:
        print("FAILED /ask anchor not found")
p.write_text(s, encoding="utf-8")
print("FINISHED")
