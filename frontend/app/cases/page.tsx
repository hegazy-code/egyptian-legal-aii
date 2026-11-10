import Link from "next/link";
import caseRecords from "../../data/appeal-cases.json";
import intakeCandidates from "../../data/appeal-case-intake-candidates.json";

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
  secondarySources?: string[];
};

type IntakeCandidate = {
  id: string;
  docket: string;
  hearingDate: string;
  reportedOutcome: string;
  sourceUrl: string;
  sourceType: string;
  missing: string[];
  publishable: boolean;
  sourceEvidence?: { reportedCharge?: string; reportedChallengedJudgment?: string; evidenceScope?: string };
};

const visibleResearchLeads = (intakeCandidates as IntakeCandidate[]).filter(c =>
  c.publishable === false && c.sourceUrl.startsWith("https://")
);

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

const pressCases = (caseRecords as CaseRecord[]).filter(c =>
  c.status === "research_only" && c.id !== "cassation-5032-93-2024" && (c.secondarySources?.length ?? 0) > 0
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
      {verifiedCases.length > 0 && (
        <section className="mt-9" aria-label="القضايا الموثقة">
          <h2 className="font-legal text-3xl font-bold">القضايا الموثقة</h2>
          <div className="mt-5 grid gap-5 md:grid-cols-2">
            {verifiedCases.map(c => <article key={c.id} className="border border-sand bg-white p-6">
              <p className="text-sm font-semibold text-seal">حكم موثق · {c.appealDate}</p>
              <h3 className="mt-3 font-legal text-2xl font-bold">{c.appealNumber}</h3><Link href={`/cases/${c.id}`} className="mt-3 inline-block font-bold text-seal underline">اقرأ القصة كاملة ←</Link>
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
      {pressCases.length > 0 && <section className="mt-10" aria-label="قضايا من مصادر منشورة قيد التحقق">
        <h2 className="font-legal text-3xl font-bold">قصص القضايا</h2>
        <div className="mt-5 grid gap-5 md:grid-cols-2">
          {pressCases.map(c => <article key={c.id} className="border border-sand bg-white p-6">
            <p className="text-sm font-semibold text-seal">{c.appealDate}</p>
            <h3 className="mt-3 font-legal text-2xl font-bold">{c.appealNumber}</h3>
            <Link href={`/cases/${c.id}`} className="mt-4 inline-block bg-seal px-5 py-3 font-bold text-white hover:opacity-90">اقرأ القصة كاملة ←</Link>
            <dl className="mt-4 space-y-3 leading-8">
              <div><dt className="font-bold text-seal">الحكم الأول بحسب المصادر</dt><dd>{c.firstJudgment}</dd></div>
              <div><dt className="font-bold text-seal">الحكم المطعون فيه</dt><dd>{c.challengedJudgment}</dd></div>
              <div><dt className="font-bold text-seal">النتيجة المنقولة</dt><dd>{c.appealOutcome}</dd></div>
            </dl>
            <div className="mt-4 flex flex-wrap gap-3">{c.secondarySources?.map((url, i) =>
              <a key={url} href={url} target="_blank" rel="noopener noreferrer" className="border border-seal px-4 py-2 font-semibold text-seal">المصدر {i + 1} ↗</a>
            )}</div>
          </article>)}
        </div>
      </section>}
      {visibleResearchLeads.length > 0 && false && <section className="mt-12" aria-label="مرشحات طعون لم تستكمل المراجعة">
        <h2 className="font-legal text-3xl font-bold">مرشحات طعون للبحث — ليست قضايا مكتملة</h2>
        <p className="mt-3 leading-8 text-muted">هذه سجلات أولية من فهارس قانونية غير رسمية. لم نتحقق من الحكم السابق أو نطابق منطوق الحكم النهائي كاملًا؛ لذلك لا نعدّها ضمن القضايا المنشورة أو الأحكام الموثقة.</p>
        <div className="mt-5 grid gap-5 md:grid-cols-2">
          {visibleResearchLeads.map(c => <article key={c.id} className="border border-sand bg-white p-6">
            <p className="text-sm font-semibold text-seal">مرشح غير معتمد · {c.hearingDate}</p>
            <h3 className="mt-3 font-legal text-2xl font-bold">الطعن {c.docket}</h3><Link href={`/cases/${c.id}`} className="mt-3 inline-block font-bold text-seal underline">افتح ملف القضية وقصتها ←</Link>
            {c.sourceEvidence?.reportedCharge && <p className="mt-3 leading-8"><strong>موضوع القضية بحسب المقتطف:</strong> {c.sourceEvidence.reportedCharge}</p>}
            <p className="mt-3 leading-8"><strong>النتيجة المذكورة في الفهرس:</strong> {c.reportedOutcome}</p>
            <p className="mt-3 leading-8"><strong>ما لم يثبت بعد:</strong> {c.missing.join("؛ ")}</p>
            <p className="mt-2 text-sm text-muted">المصدر: {c.sourceType}. هذه بيانات بحثية وليست توصيفًا قضائيًا نهائيًا.</p>
            <a href={c.sourceUrl} target="_blank" rel="noopener noreferrer" className="mt-4 inline-block border border-seal px-4 py-2 font-semibold text-seal">افتح الفهرس المصدر ↗</a>
          </article>)}
        </div>
      </section>}
      <nav className="mt-8 flex flex-wrap gap-4" aria-label="أقسام ذات صلة">
        <Link href="/real-world" className="border border-seal px-5 py-3 font-semibold text-seal hover:bg-paper-deep">القانون على أرض الواقع: قصص القضايا الحقيقية ←</Link>
        <Link href="/cases/archive" className="border border-sand px-5 py-3 font-semibold text-muted hover:bg-white">الأرشيف السابق: أحكام وقضايا عامة ←</Link>
      </nav>
    </div>
  </main>;
}
