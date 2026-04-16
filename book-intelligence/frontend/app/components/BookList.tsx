import { Book } from "@/lib/api";

import { BookCard } from "./BookCard";

export function BookList({ books }: { books: Book[] }) {
  if (books.length === 0) {
    return (
      <div className="rounded-xl border border-white/10 bg-panel/60 p-8 text-center text-ink/70">
        No books found. Try scraping more books.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {books.map((book) => (
        <BookCard key={book.id} book={book} />
      ))}
    </div>
  );
}
