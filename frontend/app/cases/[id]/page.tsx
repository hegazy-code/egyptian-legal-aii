import Link from "next/link";
import cases from "../../../data/appeal-cases.json";
import leads from "../../../data/appeal-case-intake-candidates.json";

export function generateStaticParams() {
  return [...cases, ...leads].map(c => ({ id: c.id }));
}

export default async function CaseDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const record = cases.find(c => c.id === id);
  const lead = leads.find(c => c.id === id);
  if (!record && !lead) return <main dir="rtl" className="p-10"><p>القضية غير موجودة.</p><Link href="/cases">العودة للمكتبة</Link></main>;
  const chapters = record ? [
    ["الحكاية والحكم الأول", record.firstJudgment],
    ["الحكم المطعون عليه", record.challengedJudgment],
    ["إيه اللي حصل في الطعن؟", "تفاصيل دفوع الدفاع وأسباب المحكمة لم تُستخرج كاملة بعد؛ لذلك لا ننسب للمحامي دفوعًا غير موثقة."],
    ["نتيجة الطعن بحسب المصدر", record.appealOutcome],
    ["إيه اللي نتعلمه؟", "نقض الحكم لا يعني بالضرورة البراءة. لا بد من قراءة منطوق الحكم السابق وحيثيات محكمة النقض لتحديد ما تغيّر فعلًا."]
  ] : [
    ["بداية الحكاية", lead!.sourceEvidence?.reportedCharge ?? "وقائع القضية لم تُستخرج من الحكم كاملًا بعد."],
    ["الحكم السابق", lead!.sourceEvidence?.reportedChallengedJudgment ?? "لم يتوفر منطوق الحكم السابق أو تاريخه بعد."],
    ["الطعن", `جلسة الطعن المذكورة بالفهرس: ${lead!.hearingDate}. أسباب الطعن ودفوع الدفاع غير متاحة بالنص الكامل.`],
    ["النتيجة المذكورة في الفهرس", lead!.reportedOutcome],
    ["ما الذي ينقص القصة؟", lead!.missing.join("؛ ")],
    ["الدرس القانوني", "هذا ملف بحثي أولي، ولا يمكن استنتاج دور المحامي أو تسلسل الأحكام من عنوان الفهرس وحده."]
  ];
  const sources = record ? record.secondarySources ?? [] : [lead!.sourceUrl];
  return <main dir="rtl" className="min-h-screen bg-paper text-ink"><article className="mx-auto max-w-3xl px-6 py-12">
    <Link href="/cases" className="font-bold text-seal">← الرجوع للقضايا</Link>
    <p className="mt-8 font-bold text-seal">حجازي للتقنية القانونية · {record ? "ملف بحثي غير متحقق رسميًا" : "مرشح أولي غير معتمد"}</p>
    <h1 className="mt-4 font-legal text-4xl font-bold">الطعن {record ? record.appealNumber : lead!.docket}</h1>
    <p className="mt-6 border-r-4 border-seal bg-paper-deep p-5 leading-9">هذه قصة بحثية مبنية على البيانات المتاحة، وليست سردًا مكتمل التوثيق. لا نختلق أحداثًا أو مرافعات أو حيثيات غير موجودة بالمصادر.</p>
    <div className="mt-10 space-y-8">{chapters.map(([heading, body], index) => <section key={heading} className="border-b border-sand pb-8">
      <p className="text-sm font-bold text-seal">الفصل {index + 1}</p><h2 className="mt-2 font-legal text-2xl font-bold">{heading}</h2><p className="mt-4 text-lg leading-10">{body}</p>
    </section>)}</div>
    <section className="mt-10"><h2 className="font-legal text-2xl font-bold">المصادر</h2><div className="mt-4 flex flex-wrap gap-3">{sources.map((url, i) => <a key={url} href={url} target="_blank" rel="noopener noreferrer" className="border border-seal px-4 py-2 text-seal">المصدر {i + 1} ↗</a>)}</div></section>
  </article></main>;
}
