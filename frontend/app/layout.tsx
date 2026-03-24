import "./globals.css";

import Link from "next/link";
import { ReactNode } from "react";

import Providers from "./providers";

export const metadata = {
  title: "World Geo Repository",
  description: "Global geo hierarchy explorer with Nigeria LGA support"
};

const navItems = [
  { href: "/", label: "Overview" },
  { href: "/countries", label: "Countries" },
  { href: "/explorer", label: "Division Explorer" },
  { href: "/cities", label: "Cities" },
  { href: "/search", label: "Search" },
  { href: "/map", label: "Map" }
];

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>
          <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col px-4 py-6 md:px-8">
            <header className="mb-6 rounded-2xl bg-brand-700 px-5 py-4 text-white shadow-lg">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <h1 className="font-display text-2xl md:text-3xl">World Geo Repository</h1>
                <nav className="flex flex-wrap gap-2 text-sm">
                  {navItems.map((item) => (
                    <Link
                      className="rounded-lg bg-white/10 px-3 py-1.5 transition hover:bg-white/20"
                      key={item.href}
                      href={item.href}
                    >
                      {item.label}
                    </Link>
                  ))}
                </nav>
              </div>
            </header>
            <main className="flex-1">{children}</main>
          </div>
        </Providers>
      </body>
    </html>
  );
}
