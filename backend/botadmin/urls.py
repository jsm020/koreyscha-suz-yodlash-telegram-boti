from rest_framework import viewsets, routers
from .models import Word, Attempt, KnownWord, RepeatSession, RepeatResult
from .serializers import WordSerializer, AttemptSerializer, KnownWordSerializer, RepeatSessionSerializer, RepeatResultSerializer

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

router = routers.DefaultRouter()
router.register(r'words', WordViewSet)
router.register(r'attempts', AttemptViewSet)
router.register(r'knownwords', KnownWordViewSet)
router.register(r'repeatsessions', RepeatSessionViewSet)
router.register(r'repeatresults', RepeatResultViewSet)
