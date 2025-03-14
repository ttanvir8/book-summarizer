# book_summarizer_api/booksummary/urls.py

from rest_framework import routers
from .views import BookViewSet, ChapterViewSet, ChapterSummaryViewSet

router = routers.DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'chapters', ChapterViewSet)
router.register(r'summaries', ChapterSummaryViewSet)

urlpatterns = router.urls