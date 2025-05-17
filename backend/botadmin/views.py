from .models import RepeatSession, RepeatResult
from .serializers import RepeatSessionSerializer, RepeatResultSerializer

# POST /api/add_repeat_session/
class AddRepeatSessionAPIView(APIView):
    def post(self, request):
        serializer = RepeatSessionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

# POST /api/add_repeat_result/
class AddRepeatResultAPIView(APIView):
    def post(self, request):
        serializer = RepeatResultSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

# GET /api/repeat_results_by_user_and_key/?user_id=123&repeat_key=abc
class RepeatResultsByUserAndKeyAPIView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        repeat_key = request.query_params.get('repeat_key')
        if not user_id or not repeat_key:
            return Response({'error': 'user_id and repeat_key are required'}, status=400)
        results = RepeatResult.objects.filter(user_id=user_id, repeat_key=repeat_key)
        serializer = RepeatResultSerializer(results, many=True)
        return Response(serializer.data)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Word, Attempt, KnownWord
from .serializers import AttemptSerializer, KnownWordSerializer
from django.utils.dateparse import parse_date

# POST /api/add_attempt/
class AddAttemptAPIView(APIView):
    def post(self, request):
        serializer = AttemptSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

# POST /api/add_known_word/
class AddKnownWordAPIView(APIView):
    def post(self, request):
        serializer = KnownWordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

# GET /api/attempts_by_user_and_date/?user_id=123&date=YYYY-MM-DD
class AttemptsByUserAndDateAPIView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        date_str = request.query_params.get('date')
        if not user_id or not date_str:
            return Response({'error': 'user_id and date are required'}, status=400)
        date = parse_date(date_str)
        if not date:
            return Response({'error': 'Invalid date'}, status=400)
        attempts = Attempt.objects.filter(user_id=user_id, word__created_at=date).order_by('word_id', '-attempted_at')
        # Har bir word_id uchun faqat eng so'nggi urinishni olish
        last_attempts = {}
        for a in attempts:
            if a.word_id not in last_attempts:
                last_attempts[a.word_id] = a
        serializer = AttemptSerializer(last_attempts.values(), many=True)
        return Response(serializer.data)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Word, Attempt
from .serializers import WordSerializer, AttemptSerializer
from django.utils.dateparse import parse_date

# GET /api/words_by_date/?date=YYYY-MM-DD&user_id=123
class WordsByDateAPIView(APIView):
    def get(self, request):
        date_str = request.query_params.get('date')
        user_id = request.query_params.get('user_id')
        if not date_str:
            return Response({'error': 'date is required'}, status=400)
        date = parse_date(date_str)
        if not date:
            return Response({'error': 'Invalid date'}, status=400)
        words = Word.objects.filter(created_at=date)
        # Agar user_id berilgan bo'lsa, attempts soni bo'yicha tartiblash
        if user_id:
            user_id = int(user_id)
            # Har bir so'z uchun attempts sonini topamiz
            word_ids = list(words.values_list('id', flat=True))
            attempts = Attempt.objects.filter(user_id=user_id, word_id__in=word_ids)
            attempts_map = {}
            for a in attempts:
                attempts_map[a.word_id] = attempts_map.get(a.word_id, 0) + 1
            # So'zlarni attempts soni bo'yicha kamayish tartibida, so'ng random aralashtiramiz
            import random
            words = sorted(words, key=lambda w: (-attempts_map.get(w.id, 0), random.random()))
        else:
            import random
            words = list(words)
            random.shuffle(words)
        serializer = WordSerializer(words, many=True)
        return Response(serializer.data)
