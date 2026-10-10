import type { Metadata } from "next";

export const metadata: Metadata = { title: "سياسة الخصوصية -- المساعد القانوني المصري" };

export default function PrivacyPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6">
      <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">سياسة الخصوصية</h1>

      <div className="mt-6 space-y-4 text-sm leading-relaxed text-slate-700 dark:text-slate-300">
        <p>
          نحرص على التعامل مع الأسئلة والبيانات التي يدخلها المستخدمون بحرص وشفافية.
          هذه الصفحة توضّح -- في هذه المرحلة المبكرة من المشروع -- المبادئ العامة
          التي نتبعها.
        </p>
        <p>
          <strong className="text-slate-900 dark:text-slate-100">البيانات التي نجمعها:</strong>{" "}
          نص السؤال الذي يكتبه المستخدم، بهدف إرساله إلى الخادم لمعالجته وإرجاع
          الإجابة. لا يُطلب حالياً أي تسجيل دخول لاستخدام صفحة الأسئلة.
        </p>
        <p>
          <strong className="text-slate-900 dark:text-slate-100">حسابات المستخدمين:</strong>{" "}
          ميزات الحساب الشخصي (لوحة التحكم، القضايا، الملف الشخصي) غير مفعّلة بعد،
          وسيتم تحديث هذه السياسة بالتفصيل عند إطلاقها فعلياً مع توضيح كيفية تخزين
          البيانات ومدتها وكيفية حذفها.
        </p>
        <p>
          <strong className="text-slate-900 dark:text-slate-100">ملاحظة:</strong> هذا نص
          مبدئي مرتبط بحالة الواجهة الحالية (skeleton) وليس نصاً قانونياً نهائياً
          لسياسة الخصوصية. سيُستبدل بنسخة كاملة عند اكتمال الخادم الخلفي ونظام
          المصادقة.
        </p>
      </div>
    </div>
  );
}
