"""Find wherever the structured JSON schema is defined and make the fields rich."""
import pathlib, re

root = pathlib.Path("backend/app")
targets = []

# Find any file mentioning the structured field names
for f in root.rglob("*.py"):
    try:
        txt = f.read_text(encoding="utf-8")
    except Exception:
        continue
    if "preliminaryApplication" in txt or "understandingOfQuestion" in txt:
        targets.append((f, txt))

print(f"Found {len(targets)} file(s) with the schema:")
for f, _ in targets:
    print(f"  - {f}")

if not targets:
    print("❌ No schema files found.")
    raise SystemExit

# Patch each: inject rich-content instructions into the prompt
RICH_INSTRUCTIONS = """

تعليمات إلزامية لمحتوى كل حقل — لا تختصر أبداً:

"explanation" (الشرح): يجب أن يكون ٤٠٠ كلمة على الأقل. اشرح:
- النص القانوني الحرفي للمادة ومعناها.
- الحق القانوني للعميل بالتحديد.
- التزامات الطرف الآخر.
- الاستثناءات والحالات الخاصة.
- كيف تحسب المبالغ أو التعويضات إن وجدت (بالأرقام والمعادلة).

"preliminaryApplication" (التطبيق): يجب أن يكون ٢٠٠ كلمة على الأقل.
خاطب العميل مباشرة: "في حالتك أنت..." واشرح النتيجة المتوقعة بالتفصيل والأرقام.

"possibleProcedures" (الإجراءات): يجب أن تكون ٦ خطوات على الأقل، كل خطوة جملة كاملة تتضمن:
- الفعل المطلوب بالضبط.
- الجهة المختصة بالاسم (مكتب العمل / المحكمة العمالية الابتدائية / النيابة / الشهر العقاري).
- المستندات المطلوبة بالاسم.
- الميعاد القانوني بالأيام أو الشهور.
- خطوة عن الاستئناف (٣٠ يوماً) وخطوة عن الطعن بالنقض (٦٠ يوماً).

"missingInformation": ٣ عناصر على الأقل — ما الذي يغيّر النتيجة لو عرفناه.

اكتب بأسلوب محامٍ واثق يخاطب موكله: "حقك هو..." "يجب عليك..." "لا يحق لهم...".
لا تكتب جملاً عامة. كل جملة يجب أن تحمل معلومة عملية.
"""

patched_count = 0
for f, txt in targets:
    # Find the prompt string that contains the JSON schema request
    # Inject instructions right before the closing of the prompt f-string
    if "RICH_INSTRUCTIONS_INJECTED" in txt:
        print(f"  (already patched: {f.name})")
        continue

    # Strategy: find 'المطلوب' or 'JSON' instruction in a prompt and append after it
    markers = [
        'المطلوب: أجب في صيغة JSON',
        'أعد الإجابة بصيغة JSON',
        'المطلوب:',
    ]
    done = False
    for m in markers:
        if m in txt:
            # find the end of that prompt line block (next triple quote)
            idx = txt.find(m)
            # find the closing of the f-string (next """)
            close = txt.find('"""', idx)
            if close == -1:
                continue
            txt = txt[:close] + "\n# RICH_INSTRUCTIONS_INJECTED\n" + RICH_INSTRUCTIONS + "\n" + txt[close:]
            f.write_text(txt, encoding="utf-8")
            print(f"  ✅ patched {f.name}")
            patched_count += 1
            done = True
            break
    if not done:
        print(f"  ⚠️ couldn't find injection point in {f.name}")

# Also bump max_output_tokens so longer answers aren't cut off
eng = pathlib.Path("backend/app/rag/engine.py")
e = eng.read_text(encoding="utf-8")
e2 = e.replace("max_output_tokens=3072", "max_output_tokens=8192")
e2 = e2.replace("max_output_tokens: int = 2048", "max_output_tokens: int = 8192")
if e != e2:
    eng.write_text(e2, encoding="utf-8")
    print("✅ token limit raised to 8192 (longer answers)")

print(f"\nDone — {patched_count} file(s) patched. Restart backend.")