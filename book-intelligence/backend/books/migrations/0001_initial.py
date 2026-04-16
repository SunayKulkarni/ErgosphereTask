from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Book",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("author", models.CharField(max_length=255)),
                ("rating", models.FloatField(blank=True, null=True)),
                ("reviews_count", models.IntegerField(blank=True, null=True)),
                ("price", models.FloatField(blank=True, null=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("genre", models.CharField(blank=True, max_length=120, null=True)),
                ("book_url", models.URLField(unique=True)),
                ("cover_image_url", models.URLField(blank=True, null=True)),
                ("summary", models.TextField(blank=True, null=True)),
                ("sentiment", models.CharField(blank=True, max_length=20, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="ChatHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("question", models.TextField()),
                ("answer", models.TextField()),
                ("sources", models.JSONField(default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="BookChunk",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("chunk_text", models.TextField()),
                ("chunk_index", models.IntegerField()),
                ("chroma_id", models.CharField(max_length=255, unique=True)),
                (
                    "book",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="chunks", to="books.book"),
                ),
            ],
            options={"unique_together": {("book", "chunk_index")}},
        ),
    ]
