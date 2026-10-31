interface ComingSoonProps {
  title: string;
  note?: string;
}

/**
 * Shared placeholder for every page that depends on functionality the
 * backend doesn't implement yet (auth, cases, documents, admin/RBAC).
 * See each page's TODO comment for exactly what it's waiting on.
 */
export default function ComingSoon({ title, note }: ComingSoonProps) {
  return (
    <div className="mx-auto flex max-w-xl flex-col items-center gap-4 px-4 py-24 text-center">
      <span aria-hidden className="text-4xl">🚧</span>
      <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">{title}</h1>
      <p className="text-lg font-semibold text-teal-800 dark:text-teal-400">قريباً</p>
      <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-400">
        {note ?? "هذه الصفحة قيد الإنشاء وتحتاج إلى نظام تسجيل الدخول والخادم الخلفي أولاً."}
      </p>
    </div>
  );
}
