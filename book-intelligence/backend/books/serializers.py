from rest_framework import serializers

from .models import Book, ChatHistory


class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "rating",
            "genre",
            "cover_image_url",
            "book_url",
        ]


class BookDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "rating",
            "reviews_count",
            "price",
            "description",
            "genre",
            "book_url",
            "cover_image_url",
            "summary",
            "sentiment",
            "created_at",
        ]


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["id", "title", "author", "genre", "cover_image_url", "book_url"]


class UploadBooksSerializer(serializers.Serializer):
    url = serializers.URLField(required=False)
    scrape_count = serializers.IntegerField(required=False, min_value=1, max_value=50)

    def validate(self, attrs):
        if not attrs.get("url") and not attrs.get("scrape_count"):
            raise serializers.ValidationError("Provide either 'url' or 'scrape_count'.")
        return attrs


class AskQuestionSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=2000)


class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory
        fields = ["id", "question", "answer", "sources", "created_at"]
