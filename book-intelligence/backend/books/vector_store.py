import logging
import uuid
from typing import Dict, List

import chromadb
from chromadb.config import Settings
from django.conf import settings

from .models import BookChunk

logger = logging.getLogger(__name__)

_COLLECTION_NAME = "books"


def init_chroma_client():
    client = chromadb.PersistentClient(
        path=settings.CHROMA_PERSIST_DIRECTORY,
        settings=Settings(
            anonymized_telemetry=False,
            chroma_product_telemetry_impl="books.chroma_noop_telemetry.NoOpProductTelemetryClient",
            chroma_telemetry_impl="books.chroma_noop_telemetry.NoOpProductTelemetryClient",
        ),
    )
    return client.get_or_create_collection(name=_COLLECTION_NAME)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    if not text:
        return []

    normalized = " ".join(text.split())
    if len(normalized) <= chunk_size:
        return [normalized]

    chunks: List[str] = []
    step = max(chunk_size - overlap, 1)
    for start in range(0, len(normalized), step):
        end = start + chunk_size
        chunk = normalized[start:end]
        if chunk:
            chunks.append(chunk)
        if end >= len(normalized):
            break
    return chunks


def embed_and_store(book_id: int, book_title: str, description: str, summary: str):
    collection = init_chroma_client()

    combined_text = "\n\n".join(part for part in [description or "", summary or ""] if part.strip())
    chunks = chunk_text(combined_text)
    if not chunks:
        return []

    existing_chunks = list(BookChunk.objects.filter(book_id=book_id))
    if existing_chunks:
        chroma_ids = [chunk.chroma_id for chunk in existing_chunks]
        try:
            collection.delete(ids=chroma_ids)
        except Exception as exc:
            logger.warning("Failed deleting old chunks from ChromaDB: %s", exc)
        BookChunk.objects.filter(book_id=book_id).delete()

    saved_records = []
    for index, chunk in enumerate(chunks):
        chroma_id = f"book-{book_id}-chunk-{index}-{uuid.uuid4().hex[:8]}"
        metadata = {
            "book_id": int(book_id),
            "book_title": book_title,
            "chunk_index": index,
        }

        try:
            collection.add(documents=[chunk], metadatas=[metadata], ids=[chroma_id])
        except Exception as exc:
            logger.exception("Failed adding chunk %s to ChromaDB: %s", index, exc)
            continue

        saved_records.append(
            BookChunk(
                book_id=book_id,
                chunk_text=chunk,
                chunk_index=index,
                chroma_id=chroma_id,
            )
        )

    if saved_records:
        BookChunk.objects.bulk_create(saved_records)

    return saved_records


def similarity_search(query: str, n_results: int = 5) -> List[Dict]:
    collection = init_chroma_client()

    try:
        result = collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
    except Exception as exc:
        logger.exception("Similarity search failed: %s", exc)
        return []

    documents = (result.get("documents") or [[]])[0]
    metadatas = (result.get("metadatas") or [[]])[0]
    distances = (result.get("distances") or [[]])[0]

    hits: List[Dict] = []
    for idx, chunk_text in enumerate(documents):
        metadata = metadatas[idx] if idx < len(metadatas) else {}
        distance = distances[idx] if idx < len(distances) else None
        hits.append(
            {
                "chunk_text": chunk_text,
                "book_id": metadata.get("book_id"),
                "book_title": metadata.get("book_title"),
                "distance": distance,
            }
        )
    return hits
