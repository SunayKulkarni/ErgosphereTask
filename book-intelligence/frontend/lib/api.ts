const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api";

export type Book = {
  id: number;
  title: string;
  author: string;
  rating: number | null;
  genre: string | null;
  cover_image_url: string | null;
  book_url: string;
};

export type BookDetail = Book & {
  reviews_count: number | null;
  price: number | null;
  description: string | null;
  summary: string | null;
  sentiment: string | null;
  created_at: string;
};

export type Source = {
  book_id: number;
  book_title: string;
};

export type QAResponse = {
  question: string;
  answer: string;
  sources: Source[];
};

export type ChatHistoryItem = {
  id: number;
  question: string;
  answer: string;
  sources: Source[];
  created_at: string;
};

async function parseResponse<T>(response: Response): Promise<T> {
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data?.error || "Request failed");
  }
  return data as T;
}

export async function fetchBooks(): Promise<Book[]> {
  const response = await fetch(`${API_BASE}/books/`, { cache: "no-store" });
  return parseResponse<Book[]>(response);
}

export async function fetchBookDetail(id: string): Promise<BookDetail> {
  const response = await fetch(`${API_BASE}/books/${id}/`, { cache: "no-store" });
  return parseResponse<BookDetail>(response);
}

export async function fetchRecommendations(id: string): Promise<Book[]> {
  const response = await fetch(`${API_BASE}/books/${id}/recommendations/`, { cache: "no-store" });
  return parseResponse<Book[]>(response);
}

export async function uploadBooks(scrapeCount = 1) {
  const response = await fetch(`${API_BASE}/books/upload/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scrape_count: scrapeCount }),
  });
  return parseResponse<{ total_processed: number; created: number; updated: number }>(response);
}

export async function askQuestion(question: string): Promise<QAResponse> {
  const response = await fetch(`${API_BASE}/qa/ask/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  return parseResponse<QAResponse>(response);
}

export async function fetchHistory(): Promise<ChatHistoryItem[]> {
  const response = await fetch(`${API_BASE}/qa/history/`, { cache: "no-store" });
  return parseResponse<ChatHistoryItem[]>(response);
}
