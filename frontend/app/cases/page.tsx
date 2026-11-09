import Link from "next/link";

export default function CasesPage() {
  return <main dir="rtl" className="min-h-screen bg-paper text-ink">
    <div className="mx-auto max-w-5xl px-6 py-12 md:py-16">
      <header className="border-b-[1.5px] border-ink pb-8">
        <p className="text-sm font-bold text-seal">حجازي للتقنية القانونية · القضايا</p>
        <h1 className="mt-4 font-legal text-4xl font-bold leading-relaxed md:text-5xl">لما الطعن يغيّر الحكم</h1>
        <p className="mt-4 max-w-3xl text-lg leading-9 text-muted">هنا بنحكي قضايا مصرية صدر فيها حكم، ثم أدى الطعن إلى نقضه أو تعديله أو تغيّر نتيجته بعد إعادة المحاكمة. بنوضح الحكم الأول، دفع المحامي، سبب تدخل محكمة الطعن، والنتيجة القانونية الموثقة.</p>
      </header>
      <section className="mt-8 grid gap-4 md:grid-cols-3" aria-label="مراحل القضية">
        {[
          ["١. الحكم الأول", "المحكمة حكمت بإيه؟ وعلى أي أساس؟"],
          ["٢. الطعن والنقطة الفاصلة", "إيه الخطأ أو الدفع اللي غيّر مسار القضية؟"],
          ["٣. النتيجة بعد الطعن", "هل الحكم اتنقض، اتعدل، ولا أُعيدت المحاكمة؟"]
        ].map(([title,body])=><div key={title} className="border border-sand bg-white p-6"><h2 className="font-legal text-2xl font-bold text-seal">{title}</h2><p className="mt-3 leading-8 text-muted">{body}</p></div>)}
      </section>
      <section className="mt-9 border-r-4 border-seal bg-paper-deep p-6">
        <h2 className="font-legal text-2xl font-bold">ليه مفيش قضايا معروضة هنا دلوقتي؟</h2>
        <p className="mt-3 leading-9">بنراجع الأحكام الأصلية قبل إضافة أول قضية. مش هننشر قصة على إنها «حكم اتغير بالطعن» من غير دليل واضح على الحكم الأول، والطعن، والنتيجة اللي حصلت فعلًا. نقض الحكم مش معناه تلقائيًا البراءة أو تخفيف العقوبة.</p>
      </section>
      <nav className="mt-8 flex flex-wrap gap-4" aria-label="أقسام ذات صلة">
        <Link href="/real-world" className="border border-seal px-5 py-3 font-semibold text-seal hover:bg-paper-deep">القانون على أرض الواقع: قصص القضايا الحقيقية ←</Link>
        <Link href="/cases/archive" className="border border-sand px-5 py-3 font-semibold text-muted hover:bg-white">الأرشيف السابق: أحكام وقضايا عامة ←</Link>
      </nav>
      <p className="mt-8 text-sm leading-7 text-muted">للتثقيف القانوني فقط. عند إضافة قضية، سيُعرض مصدر الحكم وتاريخ المراجعة وحالة التوثيق.</p>
    </div>
  </main>;
}
