"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Book, BookDetail, fetchBookDetail, fetchRecommendations } from "@/lib/api";

function sentimentTone(sentiment: string | null): "green" | "red" | "gray" {
  if (!sentiment) {
    return "gray";
  }
  if (sentiment.toLowerCase() === "positive") {
    return "green";
  }
  if (sentiment.toLowerCase() === "negative") {
    return "red";
  }
  return "gray";
}

export default function BookDetailPage({ params }: { params: { id: string } }) {
  const [book, setBook] = useState<BookDetail | null>(null);
  const [related, setRelated] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const run = async () => {
      setLoading(true);
      setError(null);
      try {
        const [bookData, recData] = await Promise.all([
          fetchBookDetail(params.id),
          fetchRecommendations(params.id),
        ]);
        setBook(bookData);
        setRelated(recData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load book details");
      } finally {
        setLoading(false);
      }
    };

    run();
  }, [params.id]);

  if (loading) {
    return <p className="text-sm text-ink/70">Loading book details...</p>;
  }

  if (error || !book) {
    return <p className="text-sm text-rose-300">{error || "Book not found"}</p>;
  }

  return (
    <section className="space-y-5">
      <div>
        <Link href="/">
          <Button variant="outline">Back</Button>
        </Link>
      </div>

      <div className="grid grid-cols-1 gap-5 md:grid-cols-[280px_1fr]">
        <div className="relative h-[420px] overflow-hidden rounded-xl border border-white/10 bg-panel/60">
          {book.cover_image_url ? (
            <Image
              src={book.cover_image_url}
              alt={book.title}
              fill
              className="object-cover"
              sizes="(max-width: 768px) 100vw, 280px"
            />
          ) : (
            <div className="flex h-full items-center justify-center text-sm text-ink/60">No cover</div>
          )}
        </div>

        <div className="space-y-4">
          <h1 className="font-[var(--font-heading)] text-3xl font-black text-gold">{book.title}</h1>
          <p className="text-lg text-ink/80">{book.author}</p>
          <p className="text-sm text-gold-soft">Rating: {book.rating ? `${book.rating}/5` : "N/A"}</p>

          <div className="flex flex-wrap gap-2">
            <Badge>{book.genre || "Unknown Genre"}</Badge>
            <Badge tone={sentimentTone(book.sentiment)}>{book.sentiment || "Neutral"}</Badge>
          </div>

          <Card className="border-gold/20 bg-gold/10">
            <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-gold-soft">AI Summary</h2>
            <p className="text-sm leading-relaxed">{book.summary || "Summary unavailable."}</p>
          </Card>

          <Card>
            <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-gold-soft">Description</h2>
            <p className="text-sm leading-relaxed text-ink/85">
              {book.description || "No description available."}
            </p>
          </Card>
        </div>
      </div>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold text-gold">Related Books</h2>
        {related.length === 0 ? (
          <p className="text-sm text-ink/70">No related books available yet.</p>
        ) : (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {related.map((item) => (
              <Link key={item.id} href={`/books/${item.id}`}>
                <Card className="transition hover:border-gold/40 hover:bg-white/5">
                  <p className="line-clamp-1 font-medium">{item.title}</p>
                  <p className="mt-1 text-sm text-ink/70">{item.author}</p>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </section>
    </section>
  );
}
