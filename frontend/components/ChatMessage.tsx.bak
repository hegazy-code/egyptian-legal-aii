import type { ReactNode } from "react";
import type { ChatTurn } from "@/types";
import SourceCard from "./SourceCard";
import Disclaimer from "./Disclaimer";

interface SectionProps {
  title: string;
  children: ReactNode;
}

function Section({ title, children }: SectionProps) {
  return (
    <section className="space-y-2">
      <h3 className="text-sm font-bold text-teal-800 dark:text-teal-400">{title}</h3>
      {children}
    </section>
  );
}

function TextList({ items }: { items: string[] }) {
  if (items.length === 0) {
    return <p className="text-sm text-slate-500 dark:text-slate-400">لا يوجد.</p>;
  }
  return (
    <ul className="list-disc space-y-1 pr-5 text-sm leading-relaxed text-slate-800 dark:text-slate-200">
      {items.map((item, i) => (
        <li key={i}>{item}</li>
      ))}
    </ul>
  );
}

/** Renders one question/answer exchange in the 8-section Arabic answer format. */
export default function ChatMessage({ turn, pending }: { turn: ChatTurn; pending?: boolean }) {
  const { question, answer, error } = turn;

  return (
    <article className="space-y-4">
      {/* User question bubble */}
      <div className="flex justify-start">
        <div className="max-w-2xl rounded-2xl rounded-tl-sm bg-teal-700 px-4 py-3 text-sm font-medium text-white shadow-sm">
          {question}
        </div>
      </div>

      {/* Assistant answer */}
      <div className="max-w-3xl rounded-2xl rounded-tr-sm border border-slate-200 bg-slate-50 p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900/60">
        {pending && !answer && !error ? (
          <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
            <span
              aria-hidden
              className="h-4 w-4 animate-spin rounded-full border-2 border-teal-700 border-t-transparent"
            />
            جارٍ البحث في النصوص القانونية وإعداد الإجابة...
          </div>
        ) : null}

        {error ? (
          <div className="rounded-lg border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-800 dark:border-red-800 dark:bg-red-950/40 dark:text-red-300">
            {error}
          </div>
        ) : null}

        {answer ? (
          <div className="space-y-5">
            <Section title="١. فهم سؤالك">
              <p className="text-sm leading-relaxed text-slate-800 dark:text-slate-200">
                {answer.understandingOfQuestion}
              </p>
            </Section>

            <Section title="٢. المجال القانوني">
              <span className="inline-block rounded-full bg-teal-100 px-3 py-1 text-sm font-medium text-teal-900 dark:bg-teal-900/50 dark:text-teal-300">
                {answer.legalDomain}
              </span>
            </Section>

            <Section title="٣. النصوص القانونية ذات الصلة">
              {answer.relevantLegalTexts.length === 0 ? (
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  لم يتم العثور على نصوص قانونية محددة مرتبطة مباشرة بالسؤال.
                </p>
              ) : (
                <ul className="space-y-2">
                  {answer.relevantLegalTexts.map((s) => (
                    <SourceCard key={s.id} source={s} />
                  ))}
                </ul>
              )}
            </Section>

            <Section title="٤. الشرح">
              <p className="text-sm leading-relaxed text-slate-800 dark:text-slate-200">
                {answer.explanation}
              </p>
            </Section>

            <Section title="٥. تطبيق مبدئي على الوقائع">
              <p className="text-sm leading-relaxed text-slate-800 dark:text-slate-200">
                {answer.preliminaryApplication}
              </p>
            </Section>

            <Section title="٦. معلومات ناقصة">
              <TextList items={answer.missingInformation} />
            </Section>

            <Section title="٧. الإجراءات المحتملة">
              <TextList items={answer.possibleProcedures} />
            </Section>

            <Section title="٨. مصادر الإجابة">
              {answer.answerSources.length === 0 ? (
                <p className="text-sm text-slate-500 dark:text-slate-400">لا توجد مصادر إضافية.</p>
              ) : (
                <ul className="space-y-2">
                  {answer.answerSources.map((s) => (
                    <SourceCard key={s.id} source={s} />
                  ))}
                </ul>
              )}
            </Section>

            <Disclaimer text={answer.disclaimer} />
          </div>
        ) : null}
      </div>
    </article>
  );
}
