from rest_framework import viewsets, routers
from django.urls import path, include

from .models import Word, Attempt, KnownWord, RepeatSession, RepeatResult
from .serializers import (
    WordSerializer, AttemptSerializer, KnownWordSerializer,
    RepeatSessionSerializer, RepeatResultSerializer
)

from .views import (
    CategoryViewSet,
    WordsByCategoryAPIView,
    WordsByDateAPIView,
    AddAttemptAPIView,
    AddKnownWordAPIView,
    AttemptsByUserAndCategoryAPIView,
    AddRepeatSessionAPIView,
    AddRepeatResultAPIView,
    RepeatResultsByUserAndKeyAPIView
)

# --- ViewSets ---
class WordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Word.objects.all()
    serializer_class = WordSerializer


class AttemptViewSet(viewsets.ModelViewSet):
    queryset = Attempt.objects.all()
    serializer_class = AttemptSerializer


class KnownWordViewSet(viewsets.ModelViewSet):
    queryset = KnownWord.objects.all()
    serializer_class = KnownWordSerializer


class RepeatSessionViewSet(viewsets.ModelViewSet):
    queryset = RepeatSession.objects.all()
    serializer_class = RepeatSessionSerializer


class RepeatResultViewSet(viewsets.ModelViewSet):
    queryset = RepeatResult.objects.all()
    serializer_class = RepeatResultSerializer


# --- Router ---
router = routers.DefaultRouter()
router.register(r'words', WordViewSet)
router.register(r'attempts', AttemptViewSet)
router.register(r'knownwords', KnownWordViewSet)
router.register(r'repeatsessions', RepeatSessionViewSet)
router.register(r'repeatresults', RepeatResultViewSet)
router.register(r'categories', CategoryViewSet)


# --- Custom API endpoints ---
custom_urlpatterns = [
    path("words_by_category/", WordsByCategoryAPIView.as_view(), name="words-by-category"),

    path('words_by_date/', WordsByDateAPIView.as_view(), name='words-by-date'),
    path('add_attempt/', AddAttemptAPIView.as_view(), name='add-attempt'),
    path('add_known_word/', AddKnownWordAPIView.as_view(), name='add-known-word'),
    path('attempts_by_user_and_category/', AttemptsByUserAndCategoryAPIView.as_view(), name='attempts-by-user-and-date'),
    path('add_repeat_session/', AddRepeatSessionAPIView.as_view(), name='add-repeat-session'),
    path('add_repeat_result/', AddRepeatResultAPIView.as_view(), name='add-repeat-result'),
    path('repeat_results_by_user_and_key/', RepeatResultsByUserAndKeyAPIView.as_view(), name='repeat-results-by-user-and-key'),
]

# Combine router + custom
urlpatterns = [
    path('', include(router.urls)),
    *custom_urlpatterns,
]
