import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Fairness Opinion Generator",
  description: "DCF, comparable company, and precedent transaction analysis combined into a fairness opinion report.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="bg-navy-950 text-white">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
            <Link href="/" className="flex items-baseline gap-2">
              <span className="font-serif text-lg font-bold tracking-wide text-gold-400">
                Fairness Opinion Generator
              </span>
            </Link>
            <nav className="flex gap-6 text-sm text-slate-300">
              <Link href="/" className="hover:text-white">
                New Analysis
              </Link>
              <Link href="/reports" className="hover:text-white">
                Past Reports
              </Link>
            </nav>
          </div>
        </header>
        <main className="mx-auto min-h-[calc(100vh-64px)] max-w-6xl px-6 py-8">{children}</main>
        <footer className="border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-400">
          AI-generated drafts only — not a substitute for a licensed fairness opinion provider.
        </footer>
      </body>
    </html>
  );
}
