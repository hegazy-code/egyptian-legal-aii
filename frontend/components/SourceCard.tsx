import type { SourceCitation } from "@/types";

const STATUS_LABEL: Record<SourceCitation["status"], string> = {
  current: "سارٍ حالياً",
  historical: "تاريخي / ملغى",
};

const BASIS_LABEL: Record<NonNullable<SourceCitation["basis"]>, string> = {
  from_law: "من القانون مباشرة",
  ai_inference: "استنتاج الذكاء الاصطناعي",
};

/** One citation: law/judgment name, article number, status badge, source link. */
export default function SourceCard({ source }: { source: SourceCitation }) {
  const isCurrent = source.status === "current";

  return (
    <li className="rounded-lg border border-slate-200 bg-white p-3 text-sm dark:border-slate-700 dark:bg-slate-900">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="font-semibold text-slate-900 dark:text-slate-100">
          {source.lawName}
          {source.articleNumber ? (
            <span className="font-normal text-slate-600 dark:text-slate-400">
              {" "}
              — {source.articleNumber}
            </span>
          ) : null}
        </div>
        <span
          className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${
            isCurrent
              ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-300"
              : "bg-slate-200 text-slate-700 dark:bg-slate-700 dark:text-slate-300"
          }`}
        >
          {STATUS_LABEL[source.status]}
        </span>
      </div>

      {source.excerpt ? (
        <p className="mt-2 border-r-2 border-slate-300 pr-3 text-slate-700 dark:border-slate-600 dark:text-slate-300">
          {source.excerpt}
        </p>
      ) : null}

      <div className="mt-2 flex flex-wrap items-center gap-2">
        {source.basis ? (
          <span
            className={`rounded-full px-2 py-0.5 text-xs font-medium ${
              source.basis === "from_law"
                ? "bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300"
                : "bg-purple-100 text-purple-800 dark:bg-purple-900/50 dark:text-purple-300"
            }`}
          >
            {BASIS_LABEL[source.basis]}
          </span>
        ) : null}

        {source.sourceUrl ? (
          <a
            href={source.sourceUrl}
            target="_blank"
            rel="noreferrer noopener"
            className="text-xs font-medium text-teal-700 underline underline-offset-2 hover:text-teal-900 dark:text-teal-400 dark:hover:text-teal-300"
          >
            عرض المصدر ↗
          </a>
        ) : null}
      </div>
    </li>
  );
}
