from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BookViewSet, QAViewSet

router = DefaultRouter()
router.register("books", BookViewSet, basename="books")

urlpatterns = [
    path("", include(router.urls)),
    path("qa/ask/", QAViewSet.as_view({"post": "ask"}), name="qa-ask"),
    path("qa/history/", QAViewSet.as_view({"get": "history"}), name="qa-history"),
]
