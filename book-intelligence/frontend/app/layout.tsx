import type { Metadata } from "next";
import { Merriweather, Space_Grotesk } from "next/font/google";
import type { ReactNode } from "react";

import "./globals.css";
import { Navbar } from "./components/Navbar";

const headingFont = Merriweather({
  subsets: ["latin"],
  variable: "--font-heading",
  weight: ["700", "900"],
});

const bodyFont = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-body",
  weight: ["400", "500", "700"],
});

export const metadata: Metadata = {
  title: "Document Intelligence Platform",
  description: "Book scraping, AI insights, and RAG-based Q&A",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className={`${headingFont.variable} ${bodyFont.variable} font-[var(--font-body)]`}>
        <div className="mx-auto min-h-screen max-w-7xl px-4 pb-8 sm:px-6 lg:px-8">
          <Navbar />
          <main className="animate-rise">{children}</main>
        </div>
      </body>
    </html>
  );
}
