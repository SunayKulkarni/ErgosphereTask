"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

const links = [
  { href: "/", label: "Dashboard" },
  { href: "/qa", label: "Q&A" },
];

export function Navbar() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-20 mb-6 border-b border-white/10 bg-bg/80 py-4 backdrop-blur-lg">
      <div className="flex items-center justify-between">
        <Link href="/" className="font-[var(--font-heading)] text-xl font-black tracking-wide text-gold">
          Document Intelligence
        </Link>
        <nav className="flex items-center gap-2">
          {links.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "rounded-md px-3 py-2 text-sm transition",
                  isActive
                    ? "bg-gold/15 text-gold"
                    : "text-ink/70 hover:bg-white/5 hover:text-ink",
                )}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
