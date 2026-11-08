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
  const filtered = useMemo(() => cases.filter(c => (category === "الكل" || c.category === category) && [c.title, c.story, c.number, c.category].join(" ").includes(query.trim())), [query, category]);
  const active = cases.find(c => c.id === selected);
  const docket = active?.number.match(/^([0-9]+) لسنة ([0-9]+) قضائية (.+)$/);
  return <div dir="rtl" className="min-h-screen bg-paper text-ink"><div className="mx-auto max-w-5xl px-6 py-12">
    <header className="border-b-[1.5px] border-ink pb-7">
      <p className="text-sm font-bold text-seal">حجازي للتقنية القانونية · مكتبة القضايا</p>
      <h1 className="mt-3 font-legal text-4xl font-bold leading-[1.4] md:text-5xl">{active ? active.title : "وراء كل حكم حكاية… والقانون له الكلمة الأخيرة"}</h1>
      <p className="mt-3 max-w-3xl text-lg leading-9 text-muted">حكايات قانونية مصرية بلغة واضحة، مع بيانات الحكم ومصدره المنشور.</p>
    </header>
    <p role="note" className="my-6 border-r-4 border-seal bg-paper-deep px-5 py-4 text-sm leading-8 text-muted">ملخصات تحريرية للتثقيف القانوني، وليست نصوص أحكام رسمية. لم تكتمل مطابقة بعض الوقائع والمنطوق مع المصدر الأصلي؛ راجع الحكم قبل الاعتماد عليه.</p>
    {active ? <article className="max-w-4xl">
      <button onClick={() => {setSelected(null);window.scrollTo({top:0,behavior:"smooth"});}} className="my-5 font-semibold text-seal hover:underline">→ العودة لكل القضايا</button>
      <div className="border-[1.5px] border-sand bg-white p-6 md:p-10">
        <p className="text-sm font-semibold text-seal">{active.category} · المحكمة الدستورية العليا</p>
        <h2 className="mt-3 font-legal text-3xl font-bold leading-relaxed">{active.title}</h2>
        <dl className="mt-5 grid gap-4 border-y border-sand py-4 text-sm sm:grid-cols-2">
<div><dt className="text-muted">المحكمة</dt><dd className="font-semibold">المحكمة الدستورية العليا</dd></div>
<div><dt className="text-muted">رقم الدعوى / الطعن</dt><dd className="font-semibold">{docket?.[1] ?? active.number}</dd></div>
<div><dt className="text-muted">السنة القضائية</dt><dd className="font-semibold">{docket?.[2] ?? "غير متاحة"}</dd></div>
<div><dt className="text-muted">نوع الدعوى</dt><dd className="font-semibold">{docket?.[3] ?? "غير متاح"}</dd></div>
<div><dt className="text-muted">تاريخ الحكم</dt><dd className="font-semibold">{active.date}</dd></div>
<div><dt className="text-muted">رقم القضية كاملًا</dt><dd className="font-semibold">{active.number}</dd></div>
<div><dt className="text-muted">أسماء الخصوم</dt><dd>قيد التحقق من الحكم الأصلي</dd></div>
<div><dt className="text-muted">توثيق المصدر</dt><dd className="text-seal">مصدر ثانوي — مراجعة الأصل الرسمي لم تكتمل</dd></div>
</dl>
        <section className="mt-9"><h3 className="font-legal text-2xl font-bold text-seal">١. بداية الحكاية — إيه اللي حصل؟</h3><p className="mt-3 whitespace-pre-line text-lg leading-[2.1]">{active.story}</p></section>
        <section className="mt-9 border-r-[3px] border-seal bg-paper-deep p-5"><h3 className="font-legal text-2xl font-bold">٢. النزاع وصل للمحكمة ليه؟</h3><p className="mt-3 leading-9">المسألة القانونية المطروحة ترتبط بالوقائع المذكورة أعلاه. لا تتوافر في السجل الحالي تفاصيل موثقة كافية لعرض دفوع الخصوم أو تسلسل الإجراءات كاملة، ولذلك لن ننسب للمحكمة أو للأطراف أقوالًا غير متحقق منها.</p></section>
        <section className="mt-9"><h3 className="font-legal text-2xl font-bold text-seal">٣. الحكم والدرس القانوني</h3><p className="mt-3 whitespace-pre-line text-lg leading-[2.1]">{active.takeaway}</p><p className="mt-3 text-sm leading-7 text-muted">الشرح أعلاه ملخص تحريري وليس اقتباسًا حرفيًا من منطوق الحكم. تفاصيل المنطوق غير المؤكدة لا تُعرض كحقيقة قضائية.</p></section>
        <section className="mt-9 border-t border-sand pt-6"><h3 className="font-legal text-2xl font-bold">٤. ملف القضية والمصدر</h3><p className="mt-3 text-sm leading-8 text-muted">حالة التحقق: مراجعة المصدر الأصلي مستقلة لم تكتمل بعد. المصدر أدناه أرشيف منشور للاستدلال.</p><a href={active.source} target="_blank" rel="noopener noreferrer" className="mt-3 inline-block border border-seal px-5 py-3 font-semibold text-seal hover:bg-paper-deep">قراءة الحكم المنشور ↗</a></section>
      </div>
    </article> : <>
      <div className="mt-8 flex flex-col gap-3 sm:flex-row"><input aria-label="ابحث عن قضية" placeholder="ابحث بالعنوان أو رقم القضية..." value={query} onChange={e=>setQuery(e.target.value)} className="min-w-0 flex-1 border-[1.5px] border-[#C9C1B2] bg-white px-4 py-3 outline-seal"/><select aria-label="تصنيف القضية" value={category} onChange={e=>setCategory(e.target.value)} className="border-[1.5px] border-[#C9C1B2] bg-white px-4 py-3">{categories.map(c=><option key={c}>{c}</option>)}</select></div>
      <p className="my-5 text-sm text-muted">{filtered.length} قضايا</p>
      <div className="grid gap-4 sm:grid-cols-2">{filtered.map(c=><button key={c.id} onClick={()=>{setSelected(c.id);window.scrollTo({top:0,behavior:"smooth"});}} className="border-[1.5px] border-sand bg-white p-6 text-right transition hover:border-seal hover:bg-paper-deep"><p className="text-sm font-semibold text-seal">{c.category} · {c.date}</p><h2 className="mt-3 font-legal text-2xl font-bold leading-relaxed">{c.title}</h2><p className="mt-3 line-clamp-3 leading-8 text-muted">{c.story}</p><p className="mt-5 border-t border-sand pt-4 text-sm font-semibold text-seal">اقرأ الحكاية ←</p></button>)}</div>
      {filtered.length===0 && <p className="p-8 text-muted">لا توجد قضايا مطابقة للبحث.</p>}
    </>}
  </div></div>;
}
