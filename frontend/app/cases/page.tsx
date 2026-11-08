import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "مكتبة القضايا | حجازي للتقنية القانونية",
  description: "عشر قضايا مصرية مع قصص مبسطة ومراجع للأحكام المنشورة. محتوى معلوماتي قيد المراجعة التحريرية.",
};

/**
 * Temporary production integration of the approved case-library design.
 * The case-library preview remains isolated until its data is migrated to
 * the site's own database and independently validated.
 */
export default function CasesPage() {
  return (
    <div className="bg-[#FCFBF9]">
      <div className="mx-auto max-w-6xl px-4 pt-4 text-right text-sm text-[#4A5461]">
        <p role="note" className="border-r-4 border-[#8A2434] bg-[#F4F1EC] px-4 py-3 leading-7">
          مكتبة الأحكام القضائية — القصص مبسطة للقراءة، والمعلومات المعروضة لا تُعد بديلًا عن النص الأصلي للحكم أو المشورة القانونية. بعض الملفات ما زالت قيد المراجعة والتوثيق.
        </p>
      </div>
      <iframe
        title="مكتبة القضايا المصرية — حجازي"
        src="https://hegazy-cases-preview.onrender.com/"
        loading="eager"
        referrerPolicy="strict-origin-when-cross-origin"
        className="mt-3 block h-[1400px] min-h-[85vh] w-full border-0 bg-[#FCFBF9] md:h-[1700px]"
      />
      <p className="mx-auto max-w-6xl px-4 pb-6 text-sm text-[#4A5461]">
        إذا تعذر عرض المكتبة داخل الصفحة، افتح النسخة المستقلة من الرابط التالي:{" "}
        <a className="font-semibold text-[#8A2434] underline" href="https://hegazy-cases-preview.onrender.com/" target="_blank" rel="noopener noreferrer">مكتبة القضايا</a>.
      </p>
    </div>
  );
}
