"use client";

import { useMemo, useState } from "react";

const cases = [
  {
    "id": 1,
    "number": "44 لسنة 17 قضائية دستورية",
    "date": "1997-02-22",
    "category": "الإيجارات",
    "title": "مين يكمل إيجار المحل بعد وفاة المستأجر؟",
    "story": "الخلاف بدأ حول محل مؤجر لنشاط تجاري أو حرفي. بعد وفاة المستأجر ظهر السؤال: هل يستمر الورثة في الانتفاع بالمحل بحكم القانون، أم يستطيع المالك طلب الإخلاء؟ وصل النزاع للمحكمة الدستورية لفحص حدود الامتداد القانوني لعقد الإيجار.",
    "takeaway": "القضية بتوضح الفرق بين حق الورثة في الاستمرار في النشاط وبين حق المالك في استرداد ملكه. الحكم الدستوري لا يُطبَّق على أي عقد من غير مراجعة تاريخ العقد والقانون الساري.",
    "source": "https://www.mksegypt.org/ar/judgments-of-the-supreme-constitutional-court/15606"
  },
  {
    "id": 2,
    "number": "38 لسنة 17 قضائية دستورية",
    "date": "1996-05-18",
    "category": "المحاماة",
    "title": "هل السن يمنع شخصًا مؤهلًا من المحاماة؟",
    "story": "تقدم شخص للقيد في جدول المحامين تحت التمرين، لكن طلبه اصطدم بشرط يمنع من تجاوز الخمسين عامًا. بدل ما ينتهي الموضوع عند قرار الرفض، طعن على دستورية النص: هل العمر وحده يثبت عدم القدرة على أداء عمل قانوني؟",
    "takeaway": "قضت المحكمة بعدم دستورية شرط السن في المادة 21 من قانون المحاماة في النطاق المطروح. ناقشت ارتباط القيد بحرية العمل والمساواة وطبيعة مهام المحامي.",
    "source": "https://mksegypt.org/ar/judgments-of-the-supreme-constitutional-court/15255"
  },
  {
    "id": 3,
    "number": "1 لسنة 11 قضائية تنازع",
    "date": "1991-03-02",
    "category": "تنازع الأحكام",
    "title": "هل البراءة تحسم ملكية الأموال؟",
    "story": "تعددت الإجراءات والأحكام حول أموال وحقوق محل خلاف. هنا ظهرت مشكلة قانونية مختلفة عن مجرد إثبات الاتهام: هل يوجد تعارض حقيقي بين حكمين نهائيين بحيث يستحيل تنفيذهما معًا؟",
    "takeaway": "البراءة الجنائية لا تعني تلقائيًا إثبات الملكية. يلزم الرجوع إلى منطوق كل حكم وأطرافه وموضوعه. تفاصيل الوقائع والمنطوق قيد المطابقة مع النص الكامل.",
    "source": "https://mksegypt.org/ar/judgments-of-the-supreme-constitutional-court/3630"
  },
  {
    "id": 4,
    "number": "94 لسنة 18 قضائية دستورية",
    "date": "1998-05-09",
    "category": "الوظيفة العامة",
    "title": "سنة خدمة تغيّر ترتيب الموظفين",
    "story": "موظف وجد أن زملاءه تقدموا عليه في الأقدمية بعدما ضُمّت لهم سنة خدمة عامة. بالنسبة للموظفين، الأقدمية قد تؤثر في الترقية والمراكز الوظيفية، لذلك تحول القرار إلى نزاع قضائي ثم طعن دستوري.",
    "takeaway": "قضت المحكمة بعدم دستورية احتساب الخدمة العامة بما يتجاوز أقدمية زميل التخرج في النطاق المحدد بالحكم. القضية تشرح الموازنة بين تقدير الخدمة العامة والمساواة بين الموظفين.",
    "source": "https://www.mksegypt.org/ar/judgments-of-the-supreme-constitutional-court/15545"
  },
  {
    "id": 5,
    "number": "55 لسنة 12 قضائية دستورية",
    "date": "1992-04-18",
    "category": "قانون العقوبات",
    "title": "الطعن في قانون المخدرات لا يحسم الاتهام",
    "story": "أثناء محاكمة جنائية مرتبطة بقانون المخدرات، دفع الدفاع بعدم دستورية النص التشريعي الذي تستند إليه الاتهامات. انتقل النقاش من الواقعة الجنائية نفسها إلى صلاحية النص القانوني.",
    "takeaway": "من المهم عدم الخلط بين الحكم الدستوري وبين إدانة المتهم أو براءته. تفاصيل المنطوق تحتاج مراجعة النص الكامل قبل نشر نتيجة قاطعة.",
    "source": "https://mksegypt.org/ar/judgments-of-the-supreme-constitutional-court/4032"
  },
  {
    "id": 6,
    "number": "88 لسنة 4 قضائية دستورية",
    "date": "1991-05-04",
    "category": "الملكية والحراسة",
    "title": "نزاع عقاري مرتبط بإجراءات الحراسة",
    "story": "بدأ الخلاف حول تصرفات في عقارات ارتبطت بأوضاع الحراسة. انتقل النزاع من صحة التصرفات إلى قواعد قانونية تنظم آثار الحراسة والطعن فيها.",
    "takeaway": "هذه قراءة تمهيدية لموضوع القضية، وليست تقريرًا بأن أي طرف ثبتت ملكيته أو أن البيع بطل. منطوق الحكم وأسماء الخصوم قيد المراجعة.",
    "source": "https://mksegypt.org/ar/judgments-of-the-supreme-constitutional-court/15610"
  },
  {
    "id": 7,
    "number": "102 لسنة 12 قضائية دستورية",
    "date": "1993-06-19",
    "category": "الأوقاف والتقاضي",
    "title": "قسمة وقف انتهى… وهل الاستئناف كفاية؟",
    "story": "اختلف أطراف على تقسيم أعيان وقف انتهى، فصدرت قرارات من اللجان المختصة ثم استمر الطعن أمام القضاء. بعدها ظهر سؤال دستوري: هل منع طريق طعن معين يُعد حرمانًا من حق التقاضي؟",
    "takeaway": "قضت المحكمة برفض الطعن الدستوري. حق اللجوء إلى القضاء لا يقتضي إتاحة عدد غير محدود من درجات التقاضي.",
    "source": "https://mksegypt.org/ar/judgments-of-the-supreme-constitutional-court/6183"
  },
  {
    "id": 8,
    "number": "5 لسنة 12 قضائية دستورية",
    "date": "1993-09-25",
    "category": "قانون المخدرات",
    "title": "اتهامات ثقيلة… والطعن على نص القانون",
    "story": "واجه متهم اتهامات تتعلق بمواد مخدرة واستعمال القوة أو التهديد مع موظفين عموميين، وفق أوراق الإحالة. اختار الدفاع الطعن على دستورية بعض تعديلات قانون المخدرات بدل الاكتفاء بمناقشة أدلة الاتهام.",
    "takeaway": "المحكمة لم تقبل بعض أوجه الطعن ورفضت أخرى. هذا لا يعني أن المحكمة الدستورية أدانت المتهم أو برأته.",
    "source": "https://mksegypt.org/public/ar/judgments-of-the-supreme-constitutional-court/15407"
  },
  {
    "id": 9,
    "number": "10 لسنة 14 قضائية دستورية",
    "date": "1993-06-19",
    "category": "العمل",
    "title": "موظف بنك يعترض على نقله",
    "story": "اعترض موظف على نقله بين فرعين، وطلب حقوقًا وظيفية وتعويضًا. لكن البنك استند إلى نظام قانوني خاص، فتحول جزء من الخلاف إلى سؤال عن مدى تطبيق قوانين العمل العادية.",
    "takeaway": "الفصل في دستورية النص لا يساوي بالضرورة الفصل في مشروعية قرار النقل أو استحقاق التعويض. التفاصيل الدقيقة للمنطوق قيد المطابقة.",
    "source": "https://mksegypt.org/ar/judgments-of-the-supreme-constitutional-court/6163"
  },
  {
    "id": 10,
    "number": "59 لسنة 17 قضائية دستورية",
    "date": "1997-12-06",
    "category": "الملكية العقارية",
    "title": "عقد بيع قديم يقابله تسجيل ميراث",
    "story": "تمسكت مدعية بعقد شراء قديم وحكم بصحة ونفاذه، بينما واجهت تسجيلًا لاحقًا لحق إرث. أصبح السؤال الأهم: ما أثر التسجيل على الحقوق العقارية؟ وهل تختلف آثار العقد عن آثار الشهر؟",
    "takeaway": "رفضت المحكمة الطعن الدستوري في النطاق المطروح. لكن تحديد مالك العقار في النزاع المدني يحتاج الرجوع إلى مستنداته وإجراءاته.",
    "source": "https://mksegypt.org/ar/judgments-of-the-supreme-constitutional-court/15481"
  }
];

export default function CasesPage() {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("الكل");
  const [selected, setSelected] = useState<number | null>(null);
  const categories = ["الكل", ...Array.from(new Set(cases.map(c => c.category)))];
  const filtered = useMemo(() => cases.filter(c =>
    (category === "الكل" || c.category === category) &&
    [c.title, c.story, c.number, c.category].join(" ").includes(query.trim())
  ), [query, category]);
  const active = cases.find(c => c.id === selected);
  const back = () => { setSelected(null); window.scrollTo({top: 0, behavior: "smooth"}); };
  const open = (id: number) => { setSelected(id); window.scrollTo({top: 0, behavior: "smooth"}); };
  return <main dir="rtl" className="min-h-screen bg-[#F8F6F1] text-[#192337]">
    <div className="mx-auto max-w-6xl px-5 pb-24 pt-10">
      <header className="rounded-3xl bg-[#172338] px-7 py-10 text-white shadow-xl md:px-12 md:py-14">
        <p className="mb-4 text-sm font-bold tracking-wide text-[#D8B47B]">حجازي للتقنية القانونية · مكتبة الأحكام</p>
        <h1 className="max-w-3xl text-3xl font-black leading-relaxed md:text-5xl">{active ? active.title : "وراء كل حكم… حكاية تستحق أن تُروى"}</h1>
        <p className="mt-5 max-w-3xl text-base leading-9 text-[#D9E0EA]">{active ? "اقرأ خلفية النزاع، والسؤال القانوني، وما يمكن استخلاصه من الحكم." : "اكتشف القضايا المصرية من خلال حكايات قانونية مبسطة، ومراجع يمكنك الرجوع إليها."}</p>
        <div className="mt-7 flex flex-wrap gap-3 text-xs"><span className="rounded-full border border-white/25 px-4 py-2">10 حكايات قانونية</span><span className="rounded-full border border-[#D8B47B]/50 px-4 py-2 text-[#F1D8B1]">ملخصات تحريرية · التحقق جارٍ</span></div>
      </header>
      <div role="note" className="mt-6 rounded-2xl border border-amber-200 bg-amber-50 p-5 text-sm leading-8 text-amber-950">تنبيه مهني: هذه حكايات وملخصات تحريرية وليست نسخًا رسمية أو أحكامًا موثقة نهائيًا. لا يُعتمد عليها منفردة في اتخاذ إجراء قانوني. راجع المصدر الأصلي وحالة القانون الحالية.</div>
      {active ? <div className="mt-8">
        <button onClick={back} className="mb-6 rounded-xl border border-[#D7D5D0] bg-white px-5 py-3 font-bold text-[#8A2434] hover:bg-[#F2E9E8]">→ العودة إلى مكتبة القضايا</button>
        <article className="overflow-hidden rounded-3xl border border-[#E6E0D7] bg-white shadow-sm">
          <div className="border-b border-[#EEE8E0] bg-[#FCFAF7] p-7 md:p-10">
            <div className="mb-5 flex flex-wrap gap-2 text-sm"><span className="rounded-full bg-[#8A2434] px-4 py-2 font-bold text-white">{active.category}</span><span className="rounded-full bg-[#EDE7DE] px-4 py-2">المحكمة الدستورية العليا</span><span className="rounded-full bg-amber-100 px-4 py-2 text-amber-900">قيد التحقق</span></div>
            <h2 className="text-2xl font-black leading-relaxed md:text-4xl">{active.title}</h2>
            <dl className="mt-7 grid gap-4 rounded-2xl border border-[#E9E1D7] bg-white p-5 text-sm md:grid-cols-2"><div><dt className="text-slate-500">رقم الدعوى</dt><dd className="mt-1 font-bold">{active.number}</dd></div><div><dt className="text-slate-500">تاريخ الحكم</dt><dd className="mt-1 font-bold">{active.date}</dd></div></dl>
          </div>
          <div className="space-y-10 p-7 md:p-12">
            <section className="relative border-r-4 border-[#D8B47B] pr-6"><p className="mb-2 text-sm font-bold text-[#8A2434]">الفصل الأول · بداية الحكاية</p><h3 className="text-2xl font-black">إيه اللي حصل؟</h3><p className="mt-4 text-lg leading-[2.2]">{active.story}</p></section>
            <section className="rounded-2xl bg-[#F5F2ED] p-6 md:p-8"><p className="mb-2 text-sm font-bold text-[#8A2434]">الفصل الثاني · السؤال القانوني</p><h3 className="text-2xl font-black">فين كانت المشكلة؟</h3><p className="mt-4 text-lg leading-9">القضية بتطرح سؤالًا قانونيًا يحتاج فهم الوقائع والنصوص الحاكمة وقت صدور الحكم. اقرأ خلفية النزاع ثم ارجع إلى الحكم المنشور قبل استخلاص نتيجة قانونية.</p></section>
            <section className="relative border-r-4 border-[#8A2434] pr-6"><p className="mb-2 text-sm font-bold text-[#8A2434]">الفصل الثالث · القراءة القانونية</p><h3 className="text-2xl font-black">إيه اللي نقدر نتعلمه؟</h3><p className="mt-4 text-lg leading-[2.2]">{active.takeaway}</p><p className="mt-4 text-sm leading-7 text-slate-600">هذه قراءة تحريرية؛ لا يُعرض النص أعلاه باعتباره اقتباسًا حرفيًا من منطوق المحكمة.</p></section>
            <section className="rounded-2xl border border-[#E6E0D7] p-6 md:p-8"><p className="mb-2 text-sm font-bold text-[#8A2434]">ملف القضية · المصادر والتوثيق</p><h3 className="text-2xl font-black">ارجع للمصدر بنفسك</h3><p className="my-4 leading-8 text-slate-600">المصدر التالي أرشيف منشور للاستدلال، ولم تُستكمل بعد مطابقة الحكم مع نسخة رسمية مستقلة أو مراجعة التطورات التشريعية.</p><a className="inline-flex rounded-xl bg-[#8A2434] px-6 py-3 font-bold text-white hover:bg-[#6D1B29]" href={active.source} target="_blank" rel="noopener noreferrer">قراءة الحكم المنشور ↗</a></section>
          </div>
        </article>
      </div> : <>
        <div className="mt-10 flex flex-col gap-4 md:flex-row"><input aria-label="ابحث عن قضية" placeholder="ابحث عن قضية أو رقم طعن أو موضوع..." value={query} onChange={e => setQuery(e.target.value)} className="w-full flex-1 rounded-xl border border-[#DDD7CF] bg-white px-5 py-4 outline-[#8A2434]" /><select aria-label="تصنيف القضية" value={category} onChange={e => setCategory(e.target.value)} className="rounded-xl border border-[#DDD7CF] bg-white px-5 py-4">{categories.map(c => <option key={c}>{c}</option>)}</select></div>
        <div className="my-7 flex items-center justify-between"><h2 className="text-2xl font-black">تصفح الحكايات</h2><span className="text-sm text-slate-500">{filtered.length} قضية</span></div>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">{filtered.map(c => <button key={c.id} onClick={() => open(c.id)} className="group flex min-h-72 flex-col rounded-2xl border border-[#E5DED5] bg-white p-7 text-right shadow-sm transition hover:-translate-y-1 hover:border-[#8A2434] hover:shadow-lg"><div className="mb-5 flex flex-wrap gap-2"><span className="rounded-full bg-[#F4E8E8] px-3 py-1 text-xs font-bold text-[#8A2434]">{c.category}</span><span className="rounded-full bg-amber-50 px-3 py-1 text-xs text-amber-900">قيد التحقق</span></div><h3 className="text-xl font-black leading-relaxed group-hover:text-[#8A2434]">{c.title}</h3><p className="mt-3 line-clamp-3 text-sm leading-8 text-slate-600">{c.story}</p><div className="mt-auto flex items-center justify-between border-t border-[#F0EBE5] pt-5 text-xs text-slate-500"><span>{c.number}</span><span className="font-bold text-[#8A2434]">اقرأ الحكاية ←</span></div></button>)}</div>
        {filtered.length === 0 && <p className="rounded-2xl bg-white p-10 text-center text-slate-600">لا توجد قضايا مطابقة للبحث.</p>}
      </>}
    </div>
  </main>;
}
