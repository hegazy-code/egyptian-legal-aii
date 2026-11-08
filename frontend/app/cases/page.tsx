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
 const [query,setQuery]=useState("");
 const [category,setCategory]=useState("الكل");
 const [selected,setSelected]=useState<number|null>(null);
 const categories=["الكل",...Array.from(new Set(cases.map(c=>c.category)))];
 const filtered=useMemo(()=>cases.filter(c=>(category==="الكل"||c.category===category)&&[c.title,c.story,c.number,c.category].join(" ").includes(query.trim())),[query,category]);
 const active=cases.find(c=>c.id===selected);
 return <div dir="rtl" className="min-h-screen bg-[#FCFBF9] text-[#141C26]"><div className="mx-auto max-w-6xl px-5 py-12">
 <div className="border-b border-[#E2DCD0] pb-8"><p className="font-bold text-[#8A2434]">حجازي للتقنية القانونية</p><h1 className="mt-3 font-serif text-4xl font-bold">{active?"تفاصيل القضية":"مكتبة القضايا والأحكام"}</h1><p className="mt-4 max-w-3xl leading-8 text-[#4A5461]">عشر قضايا مصرية، حكاياتها بلغة بسيطة، مع شرح قانوني وروابط للأحكام المنشورة.</p><p role="note" className="mt-4 rounded-md border-r-4 border-[#8A2434] bg-[#F4F1EC] p-4 text-sm leading-7">هذه ملخصات تحريرية وليست النصوص الرسمية للأحكام. بعض تفاصيل الوقائع والمنطوق لم تكتمل مراجعتها بعد، فلا تعتمد عليها وحدها لاتخاذ إجراء قانوني.</p></div>
 {active?<article className="mt-8 max-w-4xl"><button onClick={()=>setSelected(null)} className="mb-6 font-bold text-[#8A2434]">← العودة إلى كل القضايا</button><div className="rounded-xl border border-[#E2DCD0] bg-white p-6 md:p-10"><span className="text-sm text-[#8A2434]">{active.category} · {active.date}</span><h2 className="mt-3 text-3xl font-bold leading-relaxed">{active.title}</h2><p className="mt-2 text-sm text-[#4A5461]">رقم القضية: {active.number}</p><section className="mt-10"><h3 className="text-2xl font-bold">القصة الكاملة — ببساطة</h3><p className="mt-4 text-lg leading-[2.2]">{active.story}</p></section><section className="mt-10"><h3 className="text-2xl font-bold">المحكمة قالت إيه؟ وإيه اللي نتعلمه؟</h3><p className="mt-4 text-lg leading-[2.2]">{active.takeaway}</p></section><section className="mt-10 border-t border-[#E2DCD0] pt-6"><h3 className="text-xl font-bold">المصدر المنشور</h3><p className="my-3 text-sm text-[#4A5461]">راجع نص الحكم كاملًا قبل الاعتماد على الملخص.</p><a href={active.source} target="_blank" rel="noopener noreferrer" className="font-bold text-[#8A2434] underline">قراءة الحكم المنشور ↗</a></section></div></article>:<><div className="mt-8 flex flex-wrap gap-3"><input aria-label="ابحث عن قضية" placeholder="ابحث بالعنوان أو رقم القضية..." value={query} onChange={e=>setQuery(e.target.value)} className="min-w-0 flex-1 rounded-lg border border-[#E2DCD0] bg-white p-3 outline-[#8A2434]"/><select aria-label="تصنيف القضية" value={category} onChange={e=>setCategory(e.target.value)} className="rounded-lg border border-[#E2DCD0] bg-white p-3">{categories.map(c=><option key={c}>{c}</option>)}</select></div><p className="my-5 text-sm text-[#4A5461]">{filtered.length} قضايا</p><div className="grid gap-5 md:grid-cols-2">{filtered.map(c=><button key={c.id} onClick={()=>{setSelected(c.id);window.scrollTo({top:0,behavior:"smooth"});}} className="rounded-xl border border-[#E2DCD0] bg-white p-6 text-right transition hover:border-[#8A2434] hover:shadow-md"><p className="text-sm font-semibold text-[#8A2434]">{c.category} · {c.date}</p><h2 className="mt-3 text-xl font-bold leading-relaxed">{c.title}</h2><p className="mt-3 line-clamp-3 leading-8 text-[#4A5461]">{c.story}</p><p className="mt-5 text-sm font-bold text-[#8A2434]">اقرأ القصة ←</p></button>)}</div>{filtered.length===0&&<p className="py-12 text-center">مفيش قضايا مطابقة للبحث.</p>}</>}
 </div></div>;
}
