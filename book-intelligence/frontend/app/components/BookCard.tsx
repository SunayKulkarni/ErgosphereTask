import Image from "next/image";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { Book } from "@/lib/api";

export function BookCard({ book }: { book: Book }) {
  return (
    <Link href={`/books/${book.id}`}>
      <Card className="group h-full overflow-hidden transition duration-300 hover:-translate-y-1 hover:border-gold/30 hover:shadow-glow">
        <div className="relative mb-3 h-64 w-full overflow-hidden rounded-lg bg-black/20">
          {book.cover_image_url ? (
            <Image
              src={book.cover_image_url}
              alt={book.title}
              fill
              className="object-cover transition duration-300 group-hover:scale-105"
              sizes="(max-width: 768px) 100vw, 25vw"
            />
          ) : (
            <div className="flex h-full items-center justify-center text-sm text-ink/50">No cover</div>
          )}
        </div>

        <CardTitle className="line-clamp-2 text-base font-bold">{book.title}</CardTitle>
        <CardDescription className="mt-1 line-clamp-1">{book.author || "Unknown"}</CardDescription>

        <div className="mt-3 flex items-center justify-between">
          <span className="text-sm text-gold-soft">
            Rating: {book.rating ? `${book.rating.toFixed(1)}/5` : "N/A"}
          </span>
          {book.genre ? <Badge>{book.genre}</Badge> : <Badge tone="gray">Unclassified</Badge>}
        </div>
      </Card>
    </Link>
  );
}
