import type { Metadata } from "next";

export const metadata: Metadata = { title: "الشروط والأحكام -- المساعد القانوني المصري" };

export default function TermsPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6">
      <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">الشروط والأحكام</h1>

      <div className="mt-6 space-y-4 text-sm leading-relaxed text-slate-700 dark:text-slate-300">
        <p>
          باستخدامك هذا الموقع، فإنك توافق على أن المحتوى المقدَّم هو لأغراض
          المعلومات العامة فقط، وفقاً لما هو موضح في{" "}
          <a href="/legal-disclaimer" className="font-medium text-teal-700 underline dark:text-teal-400">
            إخلاء المسؤولية القانونية
          </a>
          .
        </p>
        <p>
          يلتزم المستخدم بعدم استخدام الموقع في أي غرض غير قانوني، وبعدم محاولة
          استخراج أو إساءة استخدام البيانات المعروضة على نطاق واسع دون إذن.
        </p>
        <p>
          يحتفظ فريق المشروع بحق تعديل هذه الشروط أو تعليق الخدمة أو تغييرها في أي
          وقت دون إشعار مسبق، نظراً لكون المشروع لا يزال في مرحلة التطوير المبكرة.
        </p>
        <p>
          <strong className="text-slate-900 dark:text-slate-100">ملاحظة:</strong> هذا نص
          مبدئي (placeholder) سيُستبدل بشروط وأحكام كاملة ومراجَعة قانونياً عند
          إطلاق الخدمة رسمياً.
        </p>
      </div>
    </div>
  );
}
