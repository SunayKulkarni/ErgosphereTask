# Document Intelligence Platform

A complete full-stack web application that scrapes book metadata, stores structured records, enriches them with AI insights, and answers user questions through a Retrieval-Augmented Generation (RAG) pipeline.

## Stack

- Backend: Django + Django REST Framework
- Database: MySQL (metadata) + ChromaDB (vector embeddings)
- Frontend: Next.js (App Router) + Tailwind CSS
- AI: Groq API (`llama-3.1-8b-instant` by default)
- Scraping: Selenium + BeautifulSoup
- Background tasks (bonus): Celery + Redis

## Project Structure

```text
book-intelligence/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/
│   │   ├── settings.py
│   │   └── urls.py
│   └── books/
│       ├── models.py
│       ├── views.py
│       ├── serializers.py
│       ├── urls.py
│       ├── scraper.py
│       ├── ai_engine.py
│       ├── rag_pipeline.py
│       └── vector_store.py
├── frontend/
│   └── app/
│       ├── page.tsx
│       ├── books/[id]/page.tsx
│       ├── qa/page.tsx
│       └── components/
│           ├── BookCard.tsx
│           ├── BookList.tsx
│           ├── QAInterface.tsx
│           └── Navbar.tsx
├── .env
└── README.md
```

## Features

- Multi-page scraper for books.toscrape.com with polite delays
- MySQL storage for books, chunks, and Q&A history
- AI-generated summary, sentiment, and genre classification
- ChromaDB persistent vector store with chunk-level indexing
- RAG-based Q&A over stored book descriptions/summaries
- Recommendation endpoint using AI selection
- Responsive frontend dashboard, detail page, and chat UI

## Setup Instructions

## 1. Clone and enter project

```bash
git clone <your-repo-url>
cd book-intelligence
```

## 2. Configure environment variables

Edit `.env` values:

```env
GROQ_API_KEY=your_key
GROQ_MODEL=llama-3.1-8b-instant
DJANGO_SECRET_KEY=your_secret
DB_NAME=bookdb
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DJANGO_CACHE_BACKEND=django.core.cache.backends.locmem.LocMemCache
```

## 3. Start MySQL and Redis

Ensure MySQL and Redis are running locally.

## 4. Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## 5. Optional background worker (Celery)

From `backend` with venv active:

```bash
celery -A config worker -l info
```

## 6. Frontend setup

```bash
cd ../frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`, backend on `http://localhost:8000`.

## API Endpoints

Base URL: `http://localhost:8000/api`

## 1. GET `/books/`
List all books.

Response:

```json
[
  {
    "id": 1,
    "title": "A Light in the Attic",
    "author": "Unknown Author",
    "rating": 3.0,
    "genre": "Fiction",
    "cover_image_url": "https://books.toscrape.com/media/cache/...jpg",
    "book_url": "https://books.toscrape.com/catalogue/..."
  }
]
```

## 2. GET `/books/{id}/`
Get full book detail.

Response:

```json
{
  "id": 1,
  "title": "A Light in the Attic",
  "author": "Unknown Author",
  "rating": 3,
  "reviews_count": 12,
  "price": 51.77,
  "description": "...",
  "genre": "Fiction",
  "summary": "...",
  "sentiment": "Positive",
  "book_url": "...",
  "cover_image_url": "...",
  "created_at": "2026-04-15T12:00:00Z"
}
```

## 3. GET `/books/{id}/recommendations/`
Get 3 related books.

Response:

```json
[
  { "id": 8, "title": "Book A", "author": "Unknown Author", "genre": "Fiction", "cover_image_url": "...", "book_url": "..." },
  { "id": 9, "title": "Book B", "author": "Unknown Author", "genre": "Fantasy", "cover_image_url": "...", "book_url": "..." },
  { "id": 10, "title": "Book C", "author": "Unknown Author", "genre": "Mystery", "cover_image_url": "...", "book_url": "..." }
]
```

## 4. POST `/books/upload/`
Scrape books and run AI + vector pipeline.

Request (scrape pages):

```json
{
  "scrape_count": 5
}
```

Request (single URL):

```json
{
  "url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
}
```

Response:

```json
{
  "created": 20,
  "updated": 5,
  "errors": [],
  "total_processed": 25
}
```

## 5. POST `/qa/ask/`
Ask a question using the RAG pipeline.

Request:

```json
{
  "question": "Which books mention perseverance?"
}
```

Response:

```json
{
  "question": "Which books mention perseverance?",
  "answer": "... [Book Title] ...",
  "sources": [
    { "book_id": 1, "book_title": "A Light in the Attic" },
    { "book_id": 7, "book_title": "Tipping the Velvet" }
  ]
}
```

## 6. GET `/qa/history/`
Get past Q&A entries.

Response:

```json
[
  {
    "id": 1,
    "question": "Which books mention perseverance?",
    "answer": "...",
    "sources": [{ "book_id": 1, "book_title": "A Light in the Attic" }],
    "created_at": "2026-04-15T12:15:00Z"
  }
]
```

## Management Command

Scrape and process books from the CLI:

```bash
python manage.py scrape_books --pages 5
```

## Caching

AI outputs (summary, genre, sentiment, recommendations) are cached for 24 hours using Django cache with keys namespaced by function and book scope.

## Screenshot Placeholders

- `screenshots/dashboard.png` - Dashboard with searchable grid
- `screenshots/book-detail.png` - Book detail with AI summary and recommendations
- `screenshots/qa-interface.png` - Chat-style Q&A with source chips
- `screenshots/mobile-view.png` - Mobile responsive views

## Sample Q&A Pairs

1. Q: `Recommend books related to mystery themes.`
   A: `Based on context, these books lean into mystery tropes ... [Book X] [Book Y]`

2. Q: `Which books have a positive tone and focus on growth?`
   A: `These titles show positive framing and growth themes ... [Book A] [Book B]`

3. Q: `Summarize recurring themes in fantasy books from this dataset.`
   A: `Common themes include world-building and quest arcs ... [Book C] [Book D]`

## Notes

- Books.toscrape does not provide explicit author names; `Unknown Author` is used.
- Never expose backend API keys in frontend code.
- ChromaDB is persistent on disk at `backend/chroma_db`.
- All timestamps are stored in UTC (`USE_TZ=True`, `TIME_ZONE="UTC"`).
