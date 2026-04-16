"use client";

import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Book, fetchBooks, uploadBooks } from "@/lib/api";

import { BookList } from "./components/BookList";

export default function DashboardPage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadBooks = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchBooks();
      setBooks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch books");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBooks();
  }, []);

  const filteredBooks = useMemo(() => {
    const query = search.trim().toLowerCase();
    if (!query) {
      return books;
    }
    return books.filter((book) => {
      return (
        book.title.toLowerCase().includes(query) ||
        (book.author || "").toLowerCase().includes(query)
      );
    });
  }, [books, search]);

  const handleScrape = async () => {
    setScraping(true);
    setError(null);
    try {
      await uploadBooks(1);
      await loadBooks();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Scrape request failed");
    } finally {
      setScraping(false);
    }
  };

  return (
    <section className="space-y-5">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="font-[var(--font-heading)] text-3xl font-black text-gold">Dashboard</h1>
          <p className="mt-1 text-sm text-ink/70">
            Scraped books, AI summaries, and intelligent retrieval in one place.
          </p>
        </div>
        <Button onClick={handleScrape} disabled={scraping || loading}>
          {scraping ? "Scraping..." : "Scrape More Books"}
        </Button>
      </div>

      <Input
        placeholder="Search by title or author"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      {error ? <p className="text-sm text-rose-300">{error}</p> : null}

      {loading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {Array.from({ length: 8 }).map((_, idx) => (
            <div key={idx} className="space-y-3 rounded-xl border border-white/10 bg-panel/70 p-4">
              <Skeleton className="h-56 w-full" />
              <Skeleton className="h-6 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
              <Skeleton className="h-4 w-2/3" />
            </div>
          ))}
        </div>
      ) : (
        <BookList books={filteredBooks} />
      )}
    </section>
  );
}
