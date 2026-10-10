import type { Metadata } from "next";

export const metadata: Metadata = { title: "من نحن -- المساعد القانوني المصري" };

export default function AboutPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6">
      <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">من نحن</h1>
      <div className="mt-6 space-y-4 text-sm leading-relaxed text-slate-700 dark:text-slate-300">
        <p>
          المساعد القانوني المصري مشروع يهدف إلى تسهيل الوصول إلى المعلومة القانونية
          لكل مواطن مصري، من خلال أداة تعتمد على الذكاء الاصطناعي للبحث في النصوص
          القانونية والأحكام القضائية المصرية وتقديم إجابات واضحة ومنظمة بالعربية.
        </p>
        <p>
          نؤمن أن فهم القانون لا يجب أن يكون حكراً على المتخصصين، لكننا في الوقت نفسه
          ندرك أن أداة آلية لا يمكنها أن تحل محل الخبرة والحكم القانوني الذي يقدمه
          محامٍ مرخّص. لذلك صُممت هذه الأداة لتكون نقطة بداية للفهم، وليست نهاية
          المطاف في أي قرار قانوني.
        </p>
        <p>
          كل إجابة تصدر عن النظام مبنية على البحث في مصادر موثوقة، مع الإشارة
          الواضحة إلى مصدر كل معلومة، والتمييز -- حيثما أمكن -- بين ما هو مقتبس من
          القانون مباشرة وما هو استنتاج مبني عليه.
        </p>
      </div>

      <section className="mt-10 rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">صاحب المشروع</h2>
        <p className="mt-3 text-base font-semibold text-teal-800 dark:text-teal-400">يوسف حجازي</p>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
          مؤسس ومطوّر &quot;المساعد القانوني المصري&quot; – طالب حقوق
        </p>
        <p className="mt-3 text-sm leading-relaxed text-slate-700 dark:text-slate-300">
          طالب في الفرقة الثانية بكلية الحقوق، بنيت هذه المنصة لتبسيط القانون المصري للناس. المحتوى
          هنا إرشادي وتعليمي، وليس استشارة قانونية من محامٍ مرخّص.
        </p>
        <ul className="mt-4 space-y-2 text-sm text-slate-700 dark:text-slate-300">
          <li>
            البريد الإلكتروني:{" "}
            <a className="text-teal-700 underline dark:text-teal-400" href="mailto:youssefhegazy336@gmail.com" dir="ltr">
              youssefhegazy336@gmail.com
            </a>
          </li>
          <li>
            الهاتف:{" "}
            <a className="text-teal-700 underline dark:text-teal-400" href="tel:+201555516710" dir="ltr">
              01555516710
            </a>
          </li>
          <li>
            واتساب:{" "}
            <a
              className="text-teal-700 underline dark:text-teal-400"
              href="https://wa.me/201555516710"
              target="_blank"
              rel="noopener noreferrer"
            >
              تواصل معي على واتساب
            </a>
          </li>
        </ul>
      </section>
    </div>
  );
}
