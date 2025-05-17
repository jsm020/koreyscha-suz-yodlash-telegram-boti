from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404

from .models import (
    Word, Attempt, KnownWord,
    RepeatSession, RepeatResult
)
from .serializers import (
    WordSerializer, AttemptSerializer, KnownWordSerializer,
    RepeatSessionSerializer, RepeatResultSerializer
)

import random


# --- CREATE APIs (POST) ---
class AddRepeatSessionAPIView(generics.CreateAPIView):
    queryset = RepeatSession.objects.all()
    serializer_class = RepeatSessionSerializer


class AddRepeatResultAPIView(generics.CreateAPIView):
    queryset = RepeatResult.objects.all()
    serializer_class = RepeatResultSerializer


class AddAttemptAPIView(generics.CreateAPIView):
    queryset = Attempt.objects.all()
    serializer_class = AttemptSerializer


class AddKnownWordAPIView(generics.CreateAPIView):
    queryset = KnownWord.objects.all()
    serializer_class = KnownWordSerializer


# --- GET APIs ---
class RepeatResultsByUserAndKeyAPIView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        repeat_key = request.query_params.get('repeat_key')

        if not user_id or not repeat_key:
            return Response({'error': 'user_id and repeat_key are required'}, status=400)

        results = RepeatResult.objects.filter(
            user_id=user_id,
            repeat_session__repeat_key=repeat_key  # ForeignKey orqali
        )
        serializer = RepeatResultSerializer(results, many=True)
        return Response(serializer.data)


class AttemptsByUserAndDateAPIView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        date_str = request.query_params.get('date')

        if not user_id or not date_str:
            return Response({'error': 'user_id and date are required'}, status=400)

        date = parse_date(date_str)
        if not date:
            return Response({'error': 'Invalid date'}, status=400)

        attempts = Attempt.objects.filter(
            user_id=user_id,
            word__created_at=date
        ).order_by('word_id', '-attempted_at')

        # Har bir word_id uchun eng so‘nggi urinishni tanlash
        last_attempts = {}
        for attempt in attempts:
            if attempt.word_id not in last_attempts:
                last_attempts[attempt.word_id] = attempt

        serializer = AttemptSerializer(last_attempts.values(), many=True)
        return Response(serializer.data)


from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.dateparse import parse_date
from .models import Word, Attempt
from .serializers import WordSerializer
import random

class WordsByDateAPIView(APIView):
    def get(self, request):
        date_str = request.query_params.get('date')
        user_id = request.query_params.get('user_id')

        # date bo‘lsa — filtrlash
        if date_str:
            date = parse_date(date_str)
            if not date:
                return Response({'error': 'Invalid date'}, status=400)
            words = Word.objects.filter(created_at=date)
        else:
            words = Word.objects.all()

        # user_id bo‘lsa — urinishlar asosida tartiblash
        if user_id:
            try:
                user_id = int(user_id)
            except ValueError:
                return Response({'error': 'Invalid user_id'}, status=400)

            word_ids = list(words.values_list('id', flat=True))
            attempts = Attempt.objects.filter(user_id=user_id, word_id__in=word_ids)

            attempts_map = {}
            for a in attempts:
                attempts_map[a.word_id] = attempts_map.get(a.word_id, 0) + 1

            words = sorted(words, key=lambda w: (-attempts_map.get(w.id, 0), random.random()))
        else:
            words = list(words)
            random.shuffle(words)

        serializer = WordSerializer(words, many=True)
        return Response(serializer.data)
