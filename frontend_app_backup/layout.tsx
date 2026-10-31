import type { Metadata } from "next";
import Nav from "@/components/Nav";
import Link from "next/link";
// Self-hosted Cairo (Arabic + Latin) -- bundled locally via @fontsource
// instead of next/font/google, so the app never depends on reaching
// fonts.googleapis.com/fonts.gstatic.com at build or runtime.
import "@fontsource/cairo/arabic-400.css";
import "@fontsource/cairo/arabic-600.css";
import "@fontsource/cairo/arabic-700.css";
import "@fontsource/cairo/latin-400.css";
import "@fontsource/cairo/latin-600.css";
import "@fontsource/cairo/latin-700.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "المساعد القانوني المصري",
  description:
    "أداة تساعدك على فهم القانون المصري من خلال إجابات مستندة إلى النصوص القانونية والأحكام القضائية -- ليست بديلاً عن استشارة محامٍ مرخّص.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="ar" dir="rtl" className="h-full">
      <body className="flex min-h-full flex-col bg-slate-50 font-sans text-slate-900 antialiased dark:bg-slate-950 dark:text-slate-100">
        <Nav />
        <main className="flex-1">{children}</main>
        <footer className="border-t border-slate-200 bg-white py-6 text-sm text-slate-500 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-400">
          <div className="mx-auto flex max-w-5xl flex-col items-center gap-3 px-4 text-center sm:flex-row sm:justify-between sm:text-right">
            <p>© {new Date().getFullYear()} المساعد القانوني المصري -- أداة معلوماتية، وليست جهة قانونية رسمية.</p>
            <nav className="flex flex-wrap items-center justify-center gap-x-4 gap-y-1">
              <Link href="/legal-disclaimer" className="hover:text-teal-700 dark:hover:text-teal-400">
                إخلاء المسؤولية القانونية
              </Link>
              <Link href="/privacy" className="hover:text-teal-700 dark:hover:text-teal-400">
                سياسة الخصوصية
              </Link>
              <Link href="/terms" className="hover:text-teal-700 dark:hover:text-teal-400">
                الشروط والأحكام
              </Link>
            </nav>
          </div>
        </footer>
      </body>
    </html>
  );
}
