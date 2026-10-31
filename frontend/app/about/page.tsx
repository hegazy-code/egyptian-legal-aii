import type { Metadata } from "next";

export const metadata: Metadata = { title: "من نحن — حجازي للتقنية القانونية" };

export default function AboutPage() {
  return (
    <div className="mx-auto max-w-4xl px-6 py-16">
      <p className="mb-3 text-sm font-semibold tracking-wide text-seal">من نحن</p>
      <h1 className="font-legal text-6xl font-bold leading-[1.25]">يوسف محمد حجازي</h1>
      <p className="mt-4 text-xl font-semibold leading-[1.7] text-seal">
        باحث قانوني
        <br />
        مؤسس المنصة · رئيس البحث التشريعي
      </p>
      <div className="mt-10 space-y-5 border-t-[1.5px] border-ink pt-8 text-xl">
        <p>
          بنيتُ هذه المنصة بنفسي لأن القانون المصري مكتوب، لكن من يحتاجه أكثر لا يستطيع قراءته. أقود البحث التشريعي في المنصة: اختيار المصادر الرسمية، وتحقيق أرقام المواد، وتصميم الطريقة التي تُبنى بها كل إجابة.
        </p>
        <p className="text-[#3A4450]">
          دراستي: الحقوق بجامعة عين شمس وتقنية المعلومات بالجامعة الألمانية بالقاهرة.
        </p>
        <p className="text-[#3A4450]">
          لا أدّعي لقب محامٍ. أدّعي شيئاً أقوى لأنه قابل للإثبات: كل إجابة هنا مبنية على نص رسمي تستطيع أن تفتحه وتقرأه بنفسك. ومن احتاج محامياً، يصل إليه وهو يعرف حقه وماذا يسأل.
        </p>
      </div>
    </div>
  );
}