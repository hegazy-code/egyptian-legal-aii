import Link from "next/link";

const LINKS: { href: string; label: string }[] = [
  { href: "/", label: "الرئيسية" },
  { href: "/ask", label: "اسأل سؤالاً" },
  { href: "/how-it-works", label: "كيف يعمل" },
  { href: "/about", label: "من نحن" },
];

/** Top navigation bar, Arabic labels, RTL-friendly. */
export default function Nav() {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/90 backdrop-blur dark:border-slate-800 dark:bg-slate-950/90">
      <nav className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
        <Link href="/" className="flex items-center gap-2 font-bold text-teal-800 dark:text-teal-400">
          <span aria-hidden className="text-xl">⚖️</span>
          <span>المساعد القانوني المصري</span>
        </Link>

        <ul className="flex flex-wrap items-center gap-1 text-sm">
          {LINKS.map((link) => (
            <li key={link.href}>
              <Link
                href={link.href}
                className="rounded-md px-3 py-2 font-medium text-slate-700 transition hover:bg-slate-100 hover:text-teal-800 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-teal-400"
              >
                {link.label}
              </Link>
            </li>
          ))}
          <li>
            <Link
              href="/dashboard"
              className="rounded-md border border-slate-300 px-3 py-2 font-medium text-slate-600 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-400 dark:hover:bg-slate-800"
            >
              لوحة التحكم
            </Link>
          </li>
        </ul>
      </nav>
    </header>
  );
}
