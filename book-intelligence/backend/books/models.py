from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    rating = models.FloatField(null=True, blank=True)
    reviews_count = models.IntegerField(null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    genre = models.CharField(max_length=120, null=True, blank=True)
    book_url = models.URLField(unique=True)
    cover_image_url = models.URLField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    sentiment = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.title} by {self.author}"


class BookChunk(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="chunks")
    chunk_text = models.TextField()
    chunk_index = models.IntegerField()
    chroma_id = models.CharField(max_length=255, unique=True)

    class Meta:
        unique_together = ("book", "chunk_index")

    def __str__(self) -> str:
        return f"Chunk {self.chunk_index} for {self.book.title}"


class ChatHistory(models.Model):
    question = models.TextField()
    answer = models.TextField()
    sources = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        preview = self.question[:50]
        return f"Q: {preview}..."
