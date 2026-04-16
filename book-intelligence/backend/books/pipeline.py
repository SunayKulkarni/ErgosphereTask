import logging
from typing import Dict, List, Tuple

from django.db import IntegrityError, transaction

from .ai_engine import analyze_sentiment, classify_genre, generate_summary
from .models import Book
from .vector_store import embed_and_store

logger = logging.getLogger(__name__)


def upsert_and_enrich_book(scraped_data: Dict) -> Tuple[Book, bool]:
    book_url = scraped_data.get("book_url")
    if not book_url:
        raise ValueError("book_url is required for insert/update")

    defaults = {
        "title": scraped_data.get("title", "Untitled"),
        "author": scraped_data.get("author", "Unknown Author"),
        "rating": scraped_data.get("rating"),
        "reviews_count": scraped_data.get("reviews_count"),
        "price": scraped_data.get("price"),
        "description": scraped_data.get("description") or "",
        "cover_image_url": scraped_data.get("cover_image_url") or "",
    }

    try:
        with transaction.atomic():
            book, created = Book.objects.update_or_create(book_url=book_url, defaults=defaults)
    except IntegrityError as exc:
        logger.exception("Failed inserting/updating book %s: %s", book_url, exc)
        raise

    description = book.description or ""
    if description:
        book.summary = generate_summary(book.title, book.author, description, book_id=book.id)
        book.genre = classify_genre(book.title, description, book_id=book.id)
        book.sentiment = analyze_sentiment(description, book_id=book.id)
        book.save(update_fields=["summary", "genre", "sentiment"])

    try:
        embed_and_store(
            book_id=book.id,
            book_title=book.title,
            description=book.description or "",
            summary=book.summary or "",
        )
    except Exception as exc:
        logger.exception("Embedding storage failed for book %s: %s", book.id, exc)

    return book, created


def process_scraped_books(scraped_books: List[Dict]) -> Dict:
    created_count = 0
    updated_count = 0
    errors: List[Dict] = []

    for item in scraped_books:
        try:
            _, created = upsert_and_enrich_book(item)
            if created:
                created_count += 1
            else:
                updated_count += 1
        except Exception as exc:
            errors.append({"book_url": item.get("book_url"), "error": str(exc)})
            continue

    return {
        "created": created_count,
        "updated": updated_count,
        "errors": errors,
        "total_processed": created_count + updated_count,
    }
