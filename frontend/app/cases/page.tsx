import Link from "next/link";
import caseRecords from "../../data/appeal-cases.json";

type CaseRecord = {
  id: string;
  status: "research_only" | "verified";
  appealNumber: string;
  appealDate: string;
  firstJudgment: string;
  challengedJudgment: string;
  appealOutcome: string;
  officialJudgmentUrl: string | null;
  primarySourceChecked: boolean;
  reviewedAt: string | null;
  reviewedBy: string | null;
};

const isOfficialCourtSource = (value: string | null) => {
  if (!value) return false;
  try {
    const url = new URL(value);
    return url.protocol === "https:" &&
      (url.hostname === "cc.gov.eg" || url.hostname.endsWith(".cc.gov.eg")) &&
      !url.username && !url.password;
  } catch {
    return false;
  }
};

const verifiedCases = (caseRecords as CaseRecord[]).filter(
  (c) => c.status === "verified" && c.primarySourceChecked === true &&
    isOfficialCourtSource(c.officialJudgmentUrl) &&
    Boolean(c.reviewedAt && c.reviewedBy)
);

export default function CasesPage() {
  return <main dir="rtl" className="min-h-screen bg-paper text-ink">
    <div className="mx-auto max-w-5xl px-6 py-12 md:py-16">
      <header className="border-b-[1.5px] border-ink pb-8">
        <p className="text-sm font-bold text-seal">حجازي للتقنية القانونية · القضايا</p>
        <h1 className="mt-4 font-legal text-4xl font-bold leading-relaxed md:text-5xl">لما الطعن يغيّر الحكم</h1>
        <p className="mt-4 max-w-3xl text-lg leading-9 text-muted">قضايا مصرية صدر فيها حكم، ثم أدى الطعن إلى نقضه أو تعديله أو تغيّر نتيجته بعد إعادة المحاكمة. بنوضح الحكم الأول، وسبب الطعن، والنقطة القانونية الفاصلة، والنتيجة الموثقة.</p>
      </header>
      <section className="mt-8 grid gap-4 md:grid-cols-3" aria-label="مراحل القضية">
        {[
          ["١. الحكم الأول", "المحكمة حكمت بإيه؟ وعلى أي أساس؟"],
          ["٢. الطعن والنقطة الفاصلة", "إيه الخطأ أو الدفع اللي غيّر مسار القضية؟"],
          ["٣. النتيجة بعد الطعن", "هل الحكم اتنقض، اتعدل، ولا أُعيدت المحاكمة؟"]
        ].map(([title,body])=><div key={title} className="border border-sand bg-white p-6"><h2 className="font-legal text-2xl font-bold text-seal">{title}</h2><p className="mt-3 leading-8 text-muted">{body}</p></div>)}
      </section>
      {verifiedCases.length === 0 ? (
        <section className="mt-9 border-r-4 border-seal bg-paper-deep p-6" role="status">
          <h2 className="font-legal text-2xl font-bold">القضايا قيد المراجعة القانونية</h2>
          <p className="mt-3 leading-9">بنراجع الأحكام الأصلية قبل نشر أول قضية. مش هننشر قصة على إنها «حكم اتغير بالطعن» من غير دليل واضح على الحكم الأول، والطعن، والنتيجة. نقض الحكم مش معناه تلقائيًا البراءة أو تخفيف العقوبة.</p>
        </section>
      ) : (
        <section className="mt-9" aria-label="القضايا الموثقة">
          <h2 className="font-legal text-3xl font-bold">القضايا الموثقة</h2>
          <div className="mt-5 grid gap-5 md:grid-cols-2">
            {verifiedCases.map(c => <article key={c.id} className="border border-sand bg-white p-6">
              <p className="text-sm font-semibold text-seal">حكم موثق · {c.appealDate}</p>
              <h3 className="mt-3 font-legal text-2xl font-bold">{c.appealNumber}</h3>
              <dl className="mt-4 space-y-3 leading-8">
                <div><dt className="font-bold text-seal">الحكم الأول</dt><dd>{c.firstJudgment}</dd></div>
                <div><dt className="font-bold text-seal">الحكم المطعون فيه</dt><dd>{c.challengedJudgment}</dd></div>
                <div><dt className="font-bold text-seal">نتيجة الطعن</dt><dd>{c.appealOutcome}</dd></div>
              </dl>
              <p className="mt-4 text-sm text-muted">آخر مراجعة: {c.reviewedAt}</p>
              <a href={c.officialJudgmentUrl!} target="_blank" rel="noopener noreferrer" className="mt-4 inline-block border border-seal px-4 py-2 font-semibold text-seal">اقرأ الحكم الأصلي ↗</a>
            </article>)}
          </div>
        </section>
      )}
      <nav className="mt-8 flex flex-wrap gap-4" aria-label="أقسام ذات صلة">
        <Link href="/real-world" className="border border-seal px-5 py-3 font-semibold text-seal hover:bg-paper-deep">القانون على أرض الواقع: قصص القضايا الحقيقية ←</Link>
        <Link href="/cases/archive" className="border border-sand px-5 py-3 font-semibold text-muted hover:bg-white">الأرشيف السابق: أحكام وقضايا عامة ←</Link>
      </nav>
      <p className="mt-8 text-sm leading-7 text-muted">للتثقيف القانوني فقط. لا تُعرض هنا إلا القضايا التي اجتازت متطلبات توثيق المصدر.</p>
    </div>
  </main>;
}
