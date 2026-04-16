import logging
from typing import Dict, List

from .ai_engine import ask_groq
from .models import ChatHistory
from .vector_store import similarity_search

logger = logging.getLogger(__name__)


def answer_question(question: str) -> Dict:
    chunks = similarity_search(question, n_results=5)

    if not chunks:
        fallback_answer = "I could not find relevant context to answer that question yet."
        chat = ChatHistory.objects.create(question=question, answer=fallback_answer, sources=[])
        return {
            "question": chat.question,
            "answer": chat.answer,
            "sources": chat.sources,
        }

    context_parts: List[str] = []
    sources: List[Dict] = []
    seen_books = set()

    for chunk in chunks:
        title = chunk.get("book_title") or "Unknown Book"
        chunk_text = chunk.get("chunk_text") or ""
        context_parts.append(f"Source: {title}\n{chunk_text}\n")

        source_key = (chunk.get("book_id"), title)
        if source_key not in seen_books:
            seen_books.add(source_key)
            sources.append(
                {
                    "book_id": chunk.get("book_id"),
                    "book_title": title,
                }
            )

    context = "\n".join(context_parts)
    prompt = (
        "You are a knowledgeable book assistant. Answer the question using ONLY the context provided. "
        "Cite the book title for each fact you use.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Provide a helpful answer with citations like [Book Title]."
    )

    answer = ask_groq(prompt, max_tokens=500)
    if not answer:
        answer = "I could not generate an answer right now. Please try again."

    chat = ChatHistory.objects.create(question=question, answer=answer, sources=sources)
    return {
        "question": chat.question,
        "answer": chat.answer,
        "sources": chat.sources,
    }
