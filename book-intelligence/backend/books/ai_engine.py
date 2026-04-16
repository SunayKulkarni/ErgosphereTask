import hashlib
import json
import logging
import os
from typing import List, Optional

from django.core.cache import cache
from groq import Groq

logger = logging.getLogger(__name__)

MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
CACHE_TIMEOUT = 60 * 60 * 24
ALLOWED_GENRES = {
    "Fiction",
    "Non-Fiction",
    "Mystery",
    "Romance",
    "Sci-Fi",
    "Fantasy",
    "Biography",
    "Self-Help",
    "History",
    "Children",
}


def _cache_key(function_name: str, payload: str, book_id: Optional[int] = None) -> str:
    payload_hash = hashlib.md5(payload.encode("utf-8")).hexdigest()[:16]
    scope = f"book-{book_id}" if book_id is not None else "book-none"
    return f"ai:{function_name}:{scope}:{payload_hash}"


def _get_client() -> Optional[Groq]:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.warning("GROQ_API_KEY is missing")
        return None
    return Groq(api_key=api_key)


def ask_groq(prompt: str, max_tokens: int = 350) -> str:
    client = _get_client()
    if client is None:
        return ""

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            max_tokens=max_tokens,
            temperature=0.2,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )
        if not completion.choices:
            return ""

        content = completion.choices[0].message.content
        if not content:
            return ""
        return str(content).strip()
    except Exception as exc:
        logger.exception("Groq API call failed: %s", exc)
        return ""


def generate_summary(
    title: str,
    author: str,
    description: str,
    book_id: Optional[int] = None,
) -> str:
    payload = f"{title}|{author}|{description}"
    key = _cache_key("summary", payload, book_id=book_id)
    cached = cache.get(key)
    if cached:
        return cached

    prompt = (
        f"Generate a concise 3-sentence summary of the book '{title}' by {author}. "
        f"Description: {description}. Focus on what makes it unique."
    )
    response = ask_groq(prompt, max_tokens=220) or "Summary unavailable."
    cache.set(key, response, timeout=CACHE_TIMEOUT)
    return response


def classify_genre(title: str, description: str, book_id: Optional[int] = None) -> str:
    payload = f"{title}|{description}"
    key = _cache_key("genre", payload, book_id=book_id)
    cached = cache.get(key)
    if cached:
        return cached

    prompt = (
        f"Based on the title '{title}' and description: {description}, classify this book into exactly ONE "
        "genre from: [Fiction, Non-Fiction, Mystery, Romance, Sci-Fi, Fantasy, Biography, "
        "Self-Help, History, Children]. Reply with just the genre name."
    )
    response = ask_groq(prompt, max_tokens=30).strip() or "Fiction"
    if response not in ALLOWED_GENRES:
        response = "Fiction"

    cache.set(key, response, timeout=CACHE_TIMEOUT)
    return response


def analyze_sentiment(description: str, book_id: Optional[int] = None) -> str:
    payload = description
    key = _cache_key("sentiment", payload, book_id=book_id)
    cached = cache.get(key)
    if cached:
        return cached

    prompt = (
        "Analyze the sentiment of this book description and reply with exactly one word "
        f"- Positive, Negative, or Neutral: {description}"
    )
    response = ask_groq(prompt, max_tokens=10).strip().capitalize()
    if response not in {"Positive", "Negative", "Neutral"}:
        response = "Neutral"

    cache.set(key, response, timeout=CACHE_TIMEOUT)
    return response


def generate_recommendations(
    book_title: str,
    genre: str,
    all_book_titles: List[str],
    book_id: Optional[int] = None,
) -> List[str]:
    payload = f"{book_title}|{genre}|{'|'.join(all_book_titles)}"
    key = _cache_key("recommendations", payload, book_id=book_id)
    cached = cache.get(key)
    if cached:
        return cached

    prompt = (
        f"Given that a user liked '{book_title}' (genre: {genre}), recommend 3 books from this list: "
        f"{all_book_titles}. Return as JSON array of title strings only."
    )
    response = ask_groq(prompt, max_tokens=140)

    recommendations: List[str] = []
    if response:
        try:
            parsed = json.loads(response)
            if isinstance(parsed, list):
                recommendations = [str(item) for item in parsed[:3]]
        except json.JSONDecodeError:
            stripped = [line.strip(" -\t") for line in response.splitlines() if line.strip()]
            recommendations = stripped[:3]

    if not recommendations:
        recommendations = all_book_titles[:3]

    cache.set(key, recommendations, timeout=CACHE_TIMEOUT)
    return recommendations
