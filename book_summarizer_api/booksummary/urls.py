# book_summarizer_api/booksummary/urls.py

from rest_framework import routers
from .views import BookViewSet, ChapterViewSet, ChapterSummaryViewSet, auth_callback
from django.urls import path

router = routers.DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'chapters', ChapterViewSet)
router.register(r'summaries', ChapterSummaryViewSet, basename='summary')

urlpatterns = router.urls

urlpatterns += [
    path('auth/callback/', auth_callback, name='auth_callback'),
]