import type { Metadata } from "next";

export const metadata: Metadata = { title: "كيف يعمل -- المساعد القانوني المصري" };

const STEPS = [
  {
    title: "١. فهم السؤال",
    body: "يحلل النظام سؤالك لتحديد المجال القانوني والنقاط الأساسية المطلوب الإجابة عنها.",
  },
  {
    title: "٢. البحث في المصادر",
    body: "يبحث النظام في النصوص القانونية والأحكام القضائية ذات الصلة، بدءاً من مصادر موثوقة ومعتمدة.",
  },
  {
    title: "٣. التحقق ومنع الهلوسة",
    body: "تُراجَع كل معلومة للتأكد من استنادها إلى مصدر فعلي قبل تضمينها في الإجابة -- لا يُسمح باختلاق نصوص أو أرقام مواد.",
  },
  {
    title: "٤. تنسيق الإجابة",
    body: "تُبنى الإجابة النهائية في ثمانية أقسام ثابتة: فهم السؤال، المجال القانوني، النصوص ذات الصلة، الشرح، التطبيق المبدئي، المعلومات الناقصة، الإجراءات المحتملة، ومصادر الإجابة -- مع تنبيه دائم بأنها ليست استشارة قانونية رسمية.",
  },
];

export default function HowItWorksPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6">
      <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">كيف يعمل المساعد القانوني</h1>
      <p className="mt-3 text-sm leading-relaxed text-slate-600 dark:text-slate-400">
        عندما تطرح سؤالاً، يمر عبر عدة مراحل قبل أن تصلك الإجابة النهائية:
      </p>

      <ol className="mt-8 space-y-6">
        {STEPS.map((step) => (
          <li key={step.title} className="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
            <h2 className="font-bold text-teal-800 dark:text-teal-400">{step.title}</h2>
            <p className="mt-2 text-sm leading-relaxed text-slate-700 dark:text-slate-300">{step.body}</p>
          </li>
        ))}
      </ol>
    </div>
  );
}
