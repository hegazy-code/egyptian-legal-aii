"use client";

import { useEffect, useMemo, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const CATEGORY_LABELS: Record<string, string> = {
  civil: "القانون المدني",
  criminal: "قانون العقوبات",
  criminal_procedure: "قانون الإجراءات الجنائية",
  civil_procedure: "قانون المرافعات المدنية والتجارية",
  commercial: "القانون التجاري",
  labor: "قانون العمل",
  consumer: "حماية المستهلك",
  family: "الأحوال الشخصية",
  intellectual_property: "الملكية الفكرية",
  cybercrime: "الجرائم الإلكترونية",
  rental: "الإيجار (القديم)",
  rental_new: "الإيجار (الجديد)",
};
const catLabel = (c: string) => CATEGORY_LABELS[c] || c;

type Law = { id: string; law_number: string; title: string; category: string; year?: number };
type Article = { id: string; article_number: string; text: string };
type Expl = { loading?: boolean; explanation?: string; example?: string; error?: string };

export default function LawsPage() {
  const [laws, setLaws] = useState<Law[] | null>(null);
  const [lawsError, setLawsError] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);
  const [law, setLaw] = useState<Law | null>(null);
  const [arts, setArts] = useState<Article[] | null>(null);
  const [loadingArts, setLoadingArts] = useState(false);
  const [open, setOpen] = useState<string | null>(null);
  const [expl, setExpl] = useState<Record<string, Expl>>({});
  const [q, setQ] = useState("");

  useEffect(() => {
    let cancelled = false;
    const timer = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));
    async function loadLaws() {
      setLaws(null); setLawsError(false);
      for (let attempt = 0; attempt < 3; attempt++) {
        try {
          const response = await fetch(`${API}/laws`, { cache: "no-store" });
          if (!response.ok) throw new Error(`HTTP ${response.status}`);
          const data = await response.json();
          if (!Array.isArray(data)) throw new Error("Invalid laws response");
          if (!cancelled) setLaws(data);
          return;
        } catch {
          if (attempt < 2) await timer((attempt + 1) * 1500);
        }
      }
      if (!cancelled) { setLaws([]); setLawsError(true); }
    }
    void loadLaws();
    return () => { cancelled = true; };
  }, [reloadKey]);

  // group laws by category
  const grouped = useMemo(() => {
    const g: Record<string, Law[]> = {};
    (laws || []).forEach((l) => (g[l.category] = g[l.category] || []).push(l));
    return g;
  }, [laws]);
  const cats = useMemo(() => Object.keys(grouped).sort(), [grouped]);

  async function openLaw(l: Law) {
    setLaw(l); setArts(null); setLoadingArts(true); setOpen(null); setQ("");
    window.scrollTo({ top: 0 });
    try {
      const response = await fetch(`${API}/laws/${l.id}`, { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const d = await response.json();
      const a: Article[] = (d.articles || []).slice().sort(
        (x: Article, y: Article) => (parseInt(x.article_number) || 0) - (parseInt(y.article_number) || 0)
      );
      setArts(a);
    } catch {
      setArts(null);
    } finally {
      setLoadingArts(false);
    }
  }

  async function explain(a: Article) {
    if (expl[a.id]?.explanation) { setOpen(open === a.id ? null : a.id); return; }
    setOpen(a.id);
    setExpl((e) => ({ ...e, [a.id]: { loading: true } }));
    try {
      const r = await fetch(`${API}/articles/${a.id}/explain`, { method: "POST" });
      if (!r.ok) throw new Error(String(r.status));
      const d = await r.json();
      setExpl((e) => ({ ...e, [a.id]: { explanation: d.explanation, example: d.example } }));
    } catch {
      setExpl((e) => ({ ...e, [a.id]: { error: "تعذّر توليد الشرح الآن — الخدمة قد تكون مزدحمة. جرّب تاني بعد لحظات." } }));
    }
  }

  const shownArts = useMemo(() => {
    if (!arts) return null;
    const term = q.trim();
    if (!term) return arts;
    return arts.filter((a) => a.article_number.includes(term) || a.text.includes(term));
  }, [arts, q]);

  // ---------- law view ----------
  if (law) {
    return (
      <div className="mx-auto flex max-w-4xl flex-col gap-6 px-6 py-10" dir="rtl">
        <button onClick={() => { setLaw(null); setArts(null); }}
          className="self-start text-[15px] text-seal hover:underline">→ رجوع لكل القوانين</button>
        <div className="border-b-[1.5px] border-ink pb-5">
          <p className="text-[13px] font-semibold text-muted">{catLabel(law.category)}</p>
          <h1 className="font-legal text-4xl font-bold leading-[1.3]">{law.title}</h1>
          {arts && <p className="mt-2 text-[15px] text-[#3A4450]">{arts.length} مادة</p>}
        </div>

        {arts && arts.length > 0 && (
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="ابحث برقم المادة أو كلمة..."
            className="border-[1.5px] border-[#C9C1B2] bg-white px-4 py-2.5 text-[16px] outline-none focus:border-seal" />
        )}

        {loadingArts && <p className="text-muted">جاري تحميل المواد...</p>}
        {arts && arts.length === 0 && <p className="text-muted">لا توجد مواد لهذا القانون.</p>}
        {!loadingArts && arts === null && <div role="alert" className="border border-sand bg-paper-deep p-4 text-seal">تعذّر تحميل المواد مؤقتًا. <button onClick={() => openLaw(law)} className="font-bold underline">إعادة المحاولة</button></div>}

        <div className="flex flex-col gap-4">
          {(shownArts || []).map((a) => {
            const ex = expl[a.id];
            const isOpen = open === a.id;
            return (
              <div key={a.id} className="border border-[#C9C1B2]">
                <div className="flex items-start gap-3 p-4">
                  <span className="shrink-0 bg-ink px-2.5 py-1 text-[13px] font-semibold text-white">مادة {a.article_number}</span>
                  <p className="flex-1 text-[16px] leading-[1.9] text-ink whitespace-pre-line">{a.text}</p>
                </div>
                <div className="border-t border-sand bg-[#FBF7F0] px-4 py-2.5">
                  <button onClick={() => explain(a)}
                    className="text-[14px] font-semibold text-seal hover:underline disabled:opacity-60"
                    disabled={ex?.loading}>
                    {ex?.loading ? "جاري توليد الشرح..." : ex?.explanation ? (isOpen ? "إخفاء الشرح" : "عرض الشرح والمثال") : "اشرح المادة بالتفصيل مع مثال"}
                  </button>
                  {isOpen && ex?.error && <p className="mt-2 text-[14px] text-seal">{ex.error}</p>}
                  {isOpen && ex?.explanation && (
                    <div className="mt-3 flex flex-col gap-3 pb-1">
                      <div>
                        <p className="mb-1 text-[13px] font-bold text-muted">الشرح</p>
                        <p className="text-[15.5px] leading-[1.9] text-ink whitespace-pre-line">{ex.explanation}</p>
                      </div>
                      {ex.example && (
                        <div className="border-r-[3px] border-seal bg-white px-4 py-3">
                          <p className="mb-1 text-[13px] font-bold text-seal">مثال عملي</p>
                          <p className="text-[15.5px] leading-[1.9] text-ink whitespace-pre-line">{ex.example}</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  // ---------- catalog view ----------
  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-8 px-6 py-12" dir="rtl">
      <div className="border-b-[1.5px] border-ink pb-6">
        <h1 className="font-legal text-5xl font-bold leading-[1.25]">القوانين المصرية</h1>
        <p className="mt-3 text-lg text-[#3A4450]">اختر القانون لتصفّح مواده كاملة، مع شرح مبسّط ومثال عملي لكل مادة.</p>
      </div>

      {!laws && <p className="text-muted">جاري التحميل...</p>}
      {lawsError && <div role="alert" className="border border-sand bg-paper-deep p-4 text-seal">تعذّر الاتصال بقاعدة القوانين مؤقتًا. <button onClick={() => setReloadKey(k => k + 1)} className="font-bold underline">إعادة المحاولة</button></div>}
      {laws && laws.length === 0 && !lawsError && <p className="text-muted">لا توجد قوانين متاحة حاليًا.</p>}

      <div className="flex flex-col gap-8">
        {cats.map((c) => (
          <div key={c}>
            <h2 className="mb-3 font-legal text-2xl font-bold text-seal">{catLabel(c)}</h2>
            <div className="grid gap-3 sm:grid-cols-2">
              {grouped[c].map((l) => (
                <button key={l.id} onClick={() => openLaw(l)}
                  className="border-[1.5px] border-[#C9C1B2] p-4 text-right hover:border-seal hover:bg-[#FBF7F0]">
                  <p className="text-[16px] font-semibold leading-[1.6] text-ink">{l.title}</p>
                  <p className="mt-1 text-[13px] text-muted">قانون رقم {l.law_number}{l.year ? ` لسنة ${l.year}` : ""}</p>
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
