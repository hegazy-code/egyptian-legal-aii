"use client";

import { useMemo, useState } from "react";

const newlySourcedCases = [
  {"id":27,"number":"24 لسنة 20 قضائية دستورية","date":"غير مثبت في الملخص","category":"الإيجارات","title":"هل يجوز تثبيت أجرة السكن بلا مراجعة؟","story":"طعن مالك على ثبات القيمة الإيجارية للوحدات السكنية في قانون 136 لسنة 1981، بعد نزاع حول إعادة تقدير أجرتها.","takeaway":"قضت المحكمة بعدم دستورية ثبات الأجرة السنوية في نطاق الفقرة الأولى من المادتين 1 و2، وحددت تاريخًا لاحقًا لإعمال أثر الحكم.","source":"https://www.sccourt.gov.eg/SCC/faces/Rules_Html/15196_20_24_1_2.html"},
  {"id":28,"number":"149 لسنة 18 قضائية دستورية","date":"غير مثبت في الملخص","category":"الإيجارات","title":"التأجير المفروش: هل يجوز فرضه على المالك؟","story":"تناول النزاع المادة 40 من القانون 49 لسنة 1977 وما تتيحه من أحكام خاصة بتأجير الأماكن مفروشة.","takeaway":"قضت المحكمة بعدم دستورية المادة 40 وسقوط المادة 45 في نطاق تطبيقها على الأماكن المؤجرة مفروشة وفق المادة 40.","source":"https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/1044_18_149_1_2.html"},
  {"id":29,"number":"99 لسنة 34 قضائية دستورية","date":"غير مثبت في الملخص","category":"تجاري","title":"تقادم الشيك: هل يسقط حق الرجوع بعد سنة؟","story":"طُعن على النص الذي يحدد مدة سنة لتقادم دعوى رجوع حامل الشيك على الساحب والمظهرين وغيرهم من الملتزمين.","takeaway":"قضت المحكمة برفض الدعوى الدستورية، معتبرة أن تحديد ميعاد التقادم تنظيم تشريعي لحق التقاضي.","source":"https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/12699_34_99_1_2.html"},
  {"id":30,"number":"34 لسنة 29 قضائية دستورية","date":"غير مثبت في الملخص","category":"تجاري","title":"قانون الشيك الجديد: هل يُطبّق إذا كان أصلح للمتهم؟","story":"تناول النزاع بدء تطبيق أحكام الشيك في قانون التجارة الجديد ومدى أثرها على اتهام جنائي قائم.","takeaway":"قضت المحكمة بعدم قبول الدعوى لزوال المصلحة بعد نفاذ التنظيم الجديد وإمكان تطبيق القانون الأصلح للمتهم.","source":"https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/2879_29_34_1_2.html"},
  {"id":12,"number":"108 لسنة 25 قضائية دستورية","date":"غير مثبت في الملخص","category":"عمل","title":"رصيد الإجازات: هل يضيع حق العامل بعد أربعة أشهر؟","story":"حُرم عامل بهيئة النقل العام من المقابل النقدي لرصيد إجازاته الاعتيادية الزائد على أربعة أشهر، رغم أن متطلبات العمل حالت دون حصوله على الإجازة.","takeaway":"قضت المحكمة بعدم دستورية الحرمان من المقابل النقدي فيما جاوز أربعة أشهر عندما يكون عدم الحصول على الإجازة راجعًا إلى مصلحة العمل.","source":"https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/1455_25_108_1_2.html"},
  {"id":13,"number":"98 لسنة 43 قضائية دستورية","date":"غير مثبت في الملخص","category":"عمل","title":"الموظف البريء: هل يسترد نصف أجر الحبس الاحتياطي؟","story":"ثار نزاع حول حرمان موظف من نصف أجره خلال حبسه احتياطيًا رغم انتهاء الإجراءات بانتفاء مسؤوليته الجنائية بصورة نهائية.","takeaway":"قضت المحكمة بعدم دستورية الحرمان من نصف الأجر في حالات انتفاء المسؤولية الجنائية بحكم نهائي أو قرار قضائي غير قابل للطعن.","source":"https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/17937_43_98_1_2.html"},
  {"id":14,"number":"47 لسنة 31 قضائية دستورية","date":"غير مثبت في الملخص","category":"عمل","title":"الفصل بعد إجازة رعاية الأب: لماذا لم يُقبل الطعن؟","story":"انقطع عامل عن العمل بعد إجازة لرعاية والده المريض، وواجه طلبًا بفصله، ثم طعن دستوريًا على المادة 69 من قانون العمل.","takeaway":"قضت المحكمة بعدم قبول الدعوى؛ لانتفاء المصلحة بالنسبة للنص المحدد، ولعدم تحديد النصوص والأوجه في باقي الطعن.","source":"https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/7906_31_47_1_2.html"},
  {"id":15,"number":"248 لسنة 30 قضائية دستورية","date":"غير مثبت في الملخص","category":"جنائي","title":"دليل الزنا: هل يجوز حصره في مكان واحد؟","story":"انصب الطعن على قصر الدليل المقبول ضد المتهم في جريمة الزنا على وجوده في منزل مسلم وفق المادة 276 من قانون العقوبات.","takeaway":"قضت المحكمة بعدم دستورية هذا القصر الوارد في عجز المادة 276 من قانون العقوبات.","source":"https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/11301_30_248_1_2.html"},
  {"id":16,"number":"114 لسنة 21 قضائية دستورية","date":"غير مثبت في الملخص","category":"جنائي","title":"متى تسقط المادة 48 من قانون العقوبات؟","story":"نظرت المحكمة طعنًا دستوريًا على المادة 48 من قانون العقوبات.","takeaway":"قضت المحكمة بعدم دستورية نص المادة 48 من قانون العقوبات؛ يلزم الرجوع للنص الأصلي لفهم نطاق الأثر التشريعي.","source":"https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/1167_21_114_1_2.html"},
  {"id":17,"number":"17 لسنة 15 قضائية دستورية","date":"غير مثبت في الملخص","category":"جنائي","title":"القبض والتفتيش في الطوارئ: هل تُستبعد ضمانات الإجراءات؟","story":"تعلّق النزاع بسلطات القبض والاعتقال وتفتيش الأشخاص والأماكن في قانون الطوارئ دون التقيد بقانون الإجراءات الجنائية.","takeaway":"قضت المحكمة بعدم دستورية ما أجازته المادة 3/1 من قانون الطوارئ من الترخيص بهذه الإجراءات دون التقيد بقانون الإجراءات الجنائية.","source":"https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/3839_15_17_1_2.html"},
  {"id":18,"number":"74 لسنة 17 قضائية دستورية","date":"غير مثبت في الملخص","category":"أحوال شخصية","title":"سن الحضانة: هل تختلف ضمانات الطفل باختلاف ديانته؟","story":"طُعن على قاعدة بلائحة الأحوال الشخصية للأقباط الأرثوذكس تُنهي الحضانة عند سن معينة وتحد من عرض مصلحة الطفل على القضاء.","takeaway":"قضت المحكمة بعدم دستورية المادة 139 من لائحة الأحوال الشخصية للأقباط الأرثوذكس.","source":"https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/1254_17_74_1_2.html"},
  {"id":19,"number":"151 لسنة 20 قضائية دستورية","date":"غير مثبت في الملخص","category":"أحوال شخصية","title":"هل تنتقل حضانة الطفل تلقائيًا للأب بعد الطلاق؟","story":"نظرت المحكمة قاعدة تنقل حضانة الصغير من أمه إلى أبيه إذا صدر حكم الطلاق لمصلحة الأب.","takeaway":"قضت المحكمة بعدم دستورية الفقرة الأولى من المادة 72 من لائحة الأحوال الشخصية للأقباط الأرثوذكس في هذا النطاق وسقوط عجزها.","source":"https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/1070_20_151_1_2.html"},
  {"id":20,"number":"95 لسنة 20 قضائية دستورية","date":"غير مثبت في الملخص","category":"تجاري","title":"هل يمكن منع الطعن في أحكام التحكيم؟","story":"انصب النزاع على نص يمنع الطعن بأي وجه في أحكام التحكيم المتعلقة بهيئات القطاع العام وشركاته.","takeaway":"قضت المحكمة بعدم دستورية الفقرة الأولى من المادة 66 من قانون هيئات القطاع العام وشركاته في حدود تحصين أحكام التحكيم من الطعن.","source":"https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/163_20_95_1_2.html"},
  {"id":21,"number":"67 لسنة 6 قضائية دستورية","date":"غير مثبت في الملخص","category":"تجاري","title":"هل تُحصّن قرارات تقييم الشركات من رقابة القضاء؟","story":"طُعن على نص يعتبر قرارات لجان تقويم بعض الشركات نهائية ولا تقبل الطعن القضائي.","takeaway":"قضت المحكمة بعدم دستورية المادة الثانية من القرار بقانون 119 لسنة 1961 في حدود تحصين تلك القرارات.","source":"https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/349_6_67_1_2.html"},
  {"id":22,"number":"45 لسنة 22 قضائية دستورية","date":"غير مثبت في الملخص","category":"مدني","title":"التركات بلا وارث: هل يصمد نص قانوني أمام الدستور؟","story":"نظرت المحكمة طعنًا على تنظيم التركات الشاغرة التي يخلفها متوفون دون وارث.","takeaway":"قضت المحكمة بعدم دستورية الفقرة الأولى من المادة الثانية من القانون رقم 71 لسنة 1962 بشأن التركات الشاغرة، وفق النطاق المبين بالحكم.","source":"https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/149_22_45_1_2.html"},
  {"id":23,"number":"2 لسنة 21 قضائية دستورية","date":"غير مثبت في الملخص","category":"عمل","title":"الإجازات غير المستخدمة بسبب العمل: حق أم منحة؟","story":"تعلّق النزاع بالمقابل النقدي عن إجازات لم يحصل عليها العامل بسبب مقتضيات العمل.","takeaway":"قضت المحكمة بعدم دستورية الحرمان من المقابل النقدي عن الرصيد الزائد على أربعة أشهر حين حالت مقتضيات العمل دون الإجازة.","source":"https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/1159_21_2_1_2.html"},
  {"id":24,"number":"200 لسنة 25 قضائية دستورية","date":"غير مثبت في الملخص","category":"أحوال شخصية","title":"مؤخر الصداق: لماذا لم تُقبل الدعوى الدستورية؟","story":"دار النزاع الموضوعي حول مؤخر صداق حل موعد أدائه بالطلاق، بينما طُعن على قاعدة لم يكن الفصل فيها مؤثرًا في هذا الدين.","takeaway":"قضت المحكمة بعدم قبول الدعوى لانتفاء المصلحة الشخصية المباشرة.","source":"https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/3205_25_200_1_2.html"},
  {"id":25,"number":"15 لسنة 17 قضائية دستورية","date":"غير مثبت في الملخص","category":"تجاري","title":"محامي الشركة: هل يُمنع من مقاضاة جهة عمله؟","story":"تناول النزاع حظر مباشرة محامي الإدارات القانونية بشركات القطاع العام أعمال المحاماة في قضاياهم ضد جهة عملهم.","takeaway":"قضت المحكمة بعدم دستورية الحظر الوارد في الفقرة الثالثة من المادة 8 من قانون المحاماة رقم 17 لسنة 1983.","source":"https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/1258_17_15_1_2.html"},
  {"id":26,"number":"54 لسنة 23 قضائية دستورية","date":"غير مثبت في الملخص","category":"مدني","title":"تعويض أصحاب الصحف: هل يجوز منع الطعن في تقديره؟","story":"تعلق الطعن بتحصين قرارات لجان تقدير تعويض أصحاب الصحف من المراجعة القضائية.","takeaway":"قضت المحكمة بعدم دستورية المادة الرابعة من القرار بقانون 156 لسنة 1960 في حدود عدم جواز الطعن على قرارات اللجنة.","source":"https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/95_23_54_1_2.html"},
  {
    id: 11, number: "108 لسنة 19 قضائية دستورية", date: "غير مؤكد",
    category: "الإيجارات", title: "هل يجوز إعادة الطعن في مسألة دستورية حُسمت سابقًا؟",
    story: "طلبت مؤجرة إنهاء عقد إيجار عين غير سكنية بعد وفاة المستأجر الأصلي، وطعنت على أحكام امتداد العقد إلى الورثة الذين يستغلون العين في النشاط نفسه.",
    takeaway: "قضت المحكمة بعدم قبول الدعوى، لسبق حسم المسألة الدستورية في القضية رقم 203 لسنة 20 قضائية بتاريخ 14 أبريل 2002. تاريخ جلسة الحكم الحالي قيد المطابقة.",
    source: "https://www.sccourt.gov.eg/DjangoPortalResources/Rules_Html/1617_19_108_1_2.html"
  }
];
const cases = [
  ...newlySourcedCases,
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

const plannedCases = [
  ["جنائي","الدفاع الشرعي"],["جنائي","بطلان الاعتراف بالإكراه"],["جنائي","القتل الخطأ"],["جنائي","التزوير"],["جنائي","النصب والاحتيال"],
  ["مدني","التعويض عن الضرر"],["مدني","فسخ العقود"],["مدني","صحة ونفاذ البيع"],["مدني","المسؤولية التقصيرية"],
  ["تجاري","منازعات الشركات"],["تجاري","الشيكات التجارية"],["تجاري","الإفلاس"],
  ["عمل","الفصل التعسفي"],["عمل","مستحقات العامل"],["عمل","إصابات العمل"],
  ["أحوال شخصية","النفقة"],["أحوال شخصية","الحضانة"],["أحوال شخصية","الرؤية والاستضافة"],
  ["إيجارات","الإخلاء"],["إيجارات","الامتداد القانوني لعقد الإيجار"]
] as const;

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
      <section className="mt-12 border-t border-sand pt-8" aria-labelledby="research-heading">
        <h2 id="research-heading" className="font-legal text-3xl font-bold">القضايا الجاري البحث عن أحكامها</h2>
        <p className="mt-3 text-base leading-8 text-muted">٢٠ موضوعًا ضمن خطة الوصول إلى ٣٠ قضية. هذه موضوعات بحث فقط، وليست أحكامًا قضائية موثقة أو قضايا منشورة. لن تُعرض تفاصيل حكم قبل مراجعة مصدره الأصلي.</p>
        <div className="mt-6 grid gap-3 sm:grid-cols-2">
          {plannedCases.map(([area, topic], index) => <div key={topic} className="border border-sand bg-paper-deep p-4">
            <p className="text-xs font-semibold text-muted">بحث رقم {index + 11} · {area} · قيد التوثيق</p>
            <p className="mt-2 font-legal text-xl font-bold">{topic}</p>
          </div>)}
        </div>
      </section>

    </>}
  </div></div>;
}
