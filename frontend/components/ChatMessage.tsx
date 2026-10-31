import type { ReactNode } from "react";
import type { ChatTurn } from "@/types";

type Answer = NonNullable<ChatTurn["answer"]>;
type Cite = Answer["relevantLegalTexts"][number];

function Label({ n, children }: { n: string; children: ReactNode }) {
  return <p className="mb-3 text-sm font-semibold text-seal">{n} · {children}</p>;
}

function badge(c: Cite) {
  const num = c.articleNumber ?? "";
  if (num.startsWith("~")) return { text: "رقم غير مؤكَّد — راجع المصدر", cls: "border-[#8A6410] text-[#8A6410]" };
  if (/unverif/i.test(c.status ?? "")) return { text: "غير موثّق من قاعدة النصوص — تحقق منه", cls: "border-[#8A6410] text-[#8A6410]" };
  if (/verif/i.test(c.status ?? "")) return { text: "نص موثّق", cls: "border-verified text-verified" };
  return null;
}

function Citation({ c }: { c: Cite }) {
  const b = badge(c);
  return (
    <div className="border-r-4 border-seal bg-paper-deep px-7 py-6">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2.5">
        <span className="text-sm font-semibold text-seal">
          {c.lawName}{c.articleNumber ? ` — مادة ${String(c.articleNumber).replace(/^~/, "")}` : ""}
        </span>
        {b && <span className={`border px-2.5 py-0.5 text-xs font-semibold ${b.cls}`}>{b.text}</span>}
      </div>
      {c.excerpt && <p className="font-legal text-2xl leading-[2]">{c.excerpt}</p>}
      {c.sourceUrl && (
        <a href={c.sourceUrl} target="_blank" rel="noreferrer" className="mt-3 inline-block text-[13px] text-seal underline">
          المصدر
        </a>
      )}
    </div>
  );
}

export default function ChatMessage({ turn, pending }: { turn: ChatTurn; pending?: boolean }) {
  const { question, answer, error } = turn;

  return (
    <article className="space-y-8">
      <div className="border-b-[1.5px] border-ink pb-5">
        <p className="mb-2 text-[13px] font-semibold tracking-wide text-muted">سؤالك</p>
        <h2 className="font-legal text-4xl font-bold leading-[1.5]">{question}</h2>
      </div>

      {pending && !answer && !error && (
        <p className="text-lg text-muted">جارٍ البحث في النصوص القانونية…</p>
      )}

      {error && (
        <div className="border-[1.5px] border-seal bg-white px-6 py-5 text-seal">{String(error)}</div>
      )}

      {answer && (
        <div className="space-y-10">
          {(answer.preliminaryApplication || answer.understandingOfQuestion) && (
            <section>
              <Label n="١">الخلاصة</Label>
              <p className="whitespace-pre-line text-[22px] font-medium leading-[1.9]">
                {answer.preliminaryApplication || answer.understandingOfQuestion}
              </p>
              {answer.legalDomain && answer.legalDomain !== "غير محدد" && (
                <p className="mt-2 text-sm text-muted">المجال القانوني: {answer.legalDomain}</p>
              )}
            </section>
          )}

          <section>
            <Label n="٢">النص الذي نستند إليه</Label>
            {answer.relevantLegalTexts.length > 0 ? (
              <div className="space-y-4">
                {answer.relevantLegalTexts.map((c, i) => <Citation key={c.id ?? i} c={c} />)}
              </div>
            ) : (
              <div className="border-[1.5px] border-ink bg-white px-6 py-5">
                <p className="font-semibold">لم نجد مادة في قاعدة النصوص تنطبق مباشرة على سؤالك.</p>
                <p className="mt-1 text-[#3A4450]">ما يلي مبني على المعرفة العامة بالقانون المصري وليس على نص موثّق من قاعدتنا — تحقق منه قبل أي إجراء.</p>
              </div>
            )}
          </section>

          {answer.explanation && (
            <section>
              <Label n="٣">الشرح</Label>
              <p className="whitespace-pre-line leading-[2]">{answer.explanation}</p>
            </section>
          )}

          {answer.possibleProcedures.length > 0 && (
            <section>
              <Label n="٤">خطواتك بالترتيب</Label>
              <ol className="border-t border-[#C9C1B2]">
                {answer.possibleProcedures.map((p, i) => (
                  <li key={i} className="flex gap-5 border-b border-sand py-5">
                    <span className="w-11 shrink-0 font-legal text-4xl font-bold leading-none text-seal">
                      {(i + 1).toLocaleString("ar-EG")}
                    </span>
                    <span className="whitespace-pre-line text-lg">{p}</span>
                  </li>
                ))}
              </ol>
            </section>
          )}

          {answer.missingInformation.length > 0 && (
            <section className="border-[1.5px] border-ink bg-white px-6 py-5">
              <p className="mb-2 text-sm font-semibold">معلومات ناقصة قد تغيّر الإجابة</p>
              <ul className="list-disc space-y-1 pr-5 text-[#3A4450]">
                {answer.missingInformation.map((m, i) => <li key={i}>{m}</li>)}
              </ul>
            </section>
          )}

          {answer.answerSources.length > 0 && (
            <section>
              <Label n="٥">مصادر الإجابة</Label>
              <ul className="space-y-1 text-sm">
                {answer.answerSources.map((s, i) => (
                  <li key={s.id ?? i}>
                    {s.sourceUrl ? (
                      <a href={s.sourceUrl} target="_blank" rel="noreferrer" className="text-seal underline">
                        {s.lawName}{s.articleNumber ? ` — مادة ${String(s.articleNumber).replace(/^~/, "")}` : ""}
                      </a>
                    ) : (
                      <span>{s.lawName}{s.articleNumber ? ` — مادة ${String(s.articleNumber).replace(/^~/, "")}` : ""}</span>
                    )}
                  </li>
                ))}
              </ul>
            </section>
          )}

          <p className="border-t border-sand pt-4 text-[13px] leading-[1.9] text-muted">
            {answer.disclaimer} قبل أي إجراء رسمي أو إذا كانت مهلة قريبة، راجع محامياً مقيّداً بالنقابة.
          </p>
        </div>
      )}
    </article>
  );
}