from django.contrib import admin

from .models import Book, BookChunk, ChatHistory


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "genre", "rating", "created_at")
    search_fields = ("title", "author", "genre")


@admin.register(BookChunk)
class BookChunkAdmin(admin.ModelAdmin):
    list_display = ("id", "book", "chunk_index", "chroma_id")
    search_fields = ("book__title", "chroma_id")


@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "created_at")
    search_fields = ("question",)
