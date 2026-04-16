from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .ai_engine import generate_recommendations
from .models import Book, ChatHistory
from .pipeline import process_scraped_books
from .rag_pipeline import answer_question
from .scraper import scrape_book_detail, scrape_book_list
from .serializers import (
    AskQuestionSerializer,
    BookDetailSerializer,
    BookListSerializer,
    ChatHistorySerializer,
    RecommendationSerializer,
    UploadBooksSerializer,
)


class BookViewSet(viewsets.ViewSet):
    def list(self, request):
        books = Book.objects.all().order_by("-created_at")
        serializer = BookListSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BookDetailSerializer(book)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="recommendations")
    def recommendations(self, request, pk=None):
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

        all_titles = list(Book.objects.exclude(pk=book.pk).values_list("title", flat=True))
        if not all_titles:
            return Response([], status=status.HTTP_200_OK)

        recommended_titles = generate_recommendations(
            book_title=book.title,
            genre=book.genre or "Fiction",
            all_book_titles=all_titles,
            book_id=book.id,
        )

        title_rank = {title: idx for idx, title in enumerate(recommended_titles)}
        candidates = list(Book.objects.filter(title__in=recommended_titles).exclude(pk=book.pk))
        candidates.sort(key=lambda item: title_rank.get(item.title, 999))

        if len(candidates) < 3:
            fallback = Book.objects.exclude(pk=book.pk).exclude(pk__in=[b.pk for b in candidates])[: 3 - len(candidates)]
            candidates.extend(list(fallback))

        serializer = RecommendationSerializer(candidates[:3], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="upload")
    def upload(self, request):
        serializer = UploadBooksSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        payload = serializer.validated_data
        scraped_books = []

        try:
            if payload.get("url"):
                detail = scrape_book_detail(payload["url"])
                if detail:
                    scraped_books.append(detail)
            else:
                pages = payload.get("scrape_count", 1)
                scraped_books = scrape_book_list(max_pages=pages)
        except Exception as exc:
            return Response(
                {"error": f"Scraping failed: {str(exc)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if not scraped_books:
            return Response(
                {"error": "No books were scraped from the provided input."},
                status=status.HTTP_404_NOT_FOUND,
            )

        result = process_scraped_books(scraped_books)
        response_status = status.HTTP_201_CREATED if result["total_processed"] else status.HTTP_207_MULTI_STATUS
        return Response(result, status=response_status)


class QAViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["post"], url_path="ask")
    def ask(self, request):
        serializer = AskQuestionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        question = serializer.validated_data["question"]
        try:
            result = answer_question(question)
        except Exception as exc:
            return Response(
                {"error": f"Failed to answer question: {str(exc)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="history")
    def history(self, request):
        history = ChatHistory.objects.all().order_by("-created_at")
        serializer = ChatHistorySerializer(history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
