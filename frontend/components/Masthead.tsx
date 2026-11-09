import Link from "next/link";

const LINKS = [
  { href: "/ask", label: "اسأل" },
  { href: "/how-it-works", label: "كيف نعمل" },
  { href: "/laws", label: "ثقف نفسك" },
  { href: "/cases", label: "القضايا" },
  { href: "/real-world", label: "القانون على أرض الواقع" },
  { href: "/documents", label: "المستندات" },
  { href: "/about", label: "من نحن" },
  { href: "/profile", label: "حسابي" },
];

export default function Masthead() {
  return (
    <header className="border-b border-sand bg-paper">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-6 py-4">
        <Link href="/" className="flex items-baseline gap-3">
          <span className="font-legal text-4xl font-bold leading-none text-seal">حجازي</span>
          <span className="border-r border-[#C9C1B2] pr-3 text-sm text-muted">للتقنية القانونية</span>
        </Link>
        <nav className="flex flex-wrap gap-x-6 gap-y-1 text-[15px] font-medium">
          {LINKS.map((l) => (
            <Link key={l.href} href={l.href} className="hover:text-seal">
              {l.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}