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
from rest_framework import viewsets
from .models import Category
from .serializers import CategorySerializer



from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Word
from .serializers import WordSerializer
class CategoryByNameAPIView(APIView):
    def get(self, request):
        name = request.query_params.get("name")
        if not name:
            return Response({"error": "name parametri kerak"}, status=400)

        categories = Category.objects.filter(name=name)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
class WordsByCategoryAPIView(APIView):
    def get(self, request):
        category_name = request.query_params.get('category')
        if not category_name:
            return Response({"error": "category parametri kerak"}, status=400)

        words = Word.objects.filter(category__name=category_name)
        serializer = WordSerializer(words, many=True)
        return Response(serializer.data)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all().order_by('-created_at')
    serializer_class = CategorySerializer


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


class AddKnownWordAPIView(APIView):
    def post(self, request):
        user_id = request.data.get("user_id")
        word_id = request.data.get("word")

        # Agar mavjud bo‘lsa, 200 qaytaramiz
        if KnownWord.objects.filter(user_id=user_id, word_id=word_id).exists():
            return Response({"message": "Allaqachon mavjud"}, status=200)

        serializer = KnownWordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)



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



class AttemptsByUserAndCategoryAPIView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        category_name = request.query_params.get('category')

        if not user_id or not category_name:
            return Response({'error': 'user_id and category are required'}, status=400)

        try:
            user_id = int(user_id)
        except ValueError:
            return Response({'error': 'Invalid user_id'}, status=400)

        try:
            category = Category.objects.get(name=category_name)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=404)

        word_ids = Word.objects.filter(category=category).values_list('id', flat=True)

        attempts = Attempt.objects.filter(
            user_id=user_id,
            word_id__in=word_ids
        ).order_by('word_id', '-attempted_at')

        # Har bir word_id uchun faqat eng so‘nggi urinishni olish
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
        category_name = request.query_params.get('category')
        user_id = request.query_params.get('user_id')

        if not category_name:
            return Response({"error": "category is required"}, status=400)

        try:
            category = Category.objects.get(name=category_name)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=404)

        words = Word.objects.filter(category=category)

        # user_id bo‘lsa — tartiblash
        if user_id:
            try:
                user_id = int(user_id)
            except ValueError:
                return Response({"error": "Invalid user_id"}, status=400)

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