import Link from "next/link";
import Disclaimer from "@/components/Disclaimer";

const FEATURES = [
  {
    title: "إجابات مستندة إلى مصادر",
    body: "كل إجابة مبنية على نصوص قانونية وأحكام قضائية حقيقية، مع ذكر المصدر ورقم المادة.",
  },
  {
    title: "تمييز واضح بين النص والاستنتاج",
    body: "نوضّح دائماً ما هو مقتبس من القانون مباشرة، وما هو استنتاج من الذكاء الاصطناعي.",
  },
  {
    title: "بالعربية، ولمصر تحديداً",
    body: "مبني حول القانون المصري وإجراءاته، بلغة عربية واضحة ومباشرة.",
  },
];

export default function HomePage() {
  return (
    <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 sm:py-16">
      <section className="text-center">
        <h1 className="text-3xl font-extrabold leading-tight text-slate-900 sm:text-4xl dark:text-slate-100">
          اسأل سؤالك القانوني، واحصل على إجابة مبنية على القانون المصري
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-base leading-relaxed text-slate-600 dark:text-slate-400">
          المساعد القانوني المصري أداة تساعدك على فهم حقوقك والتزاماتك القانونية من خلال
          تحليل سؤالك، والبحث في النصوص القانونية ذات الصلة، وتقديم إجابة منظمة
          بمصادرها -- كل ذلك باللغة العربية.
        </p>

        <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Link
            href="/ask"
            className="rounded-lg bg-teal-700 px-6 py-3 text-base font-semibold text-white shadow-sm transition hover:bg-teal-800"
          >
            اطرح سؤالك الآن
          </Link>
          <Link
            href="/how-it-works"
            className="rounded-lg border border-slate-300 px-6 py-3 text-base font-semibold text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            كيف يعمل؟
          </Link>
        </div>
      </section>

      <section className="mt-12 grid gap-4 sm:grid-cols-3">
        {FEATURES.map((f) => (
          <div
            key={f.title}
            className="rounded-xl border border-slate-200 bg-white p-5 text-right shadow-sm dark:border-slate-800 dark:bg-slate-900"
          >
            <h2 className="font-bold text-slate-900 dark:text-slate-100">{f.title}</h2>
            <p className="mt-2 text-sm leading-relaxed text-slate-600 dark:text-slate-400">{f.body}</p>
          </div>
        ))}
      </section>

      <section className="mt-12">
        <Disclaimer />
      </section>
    </div>
  );
}
