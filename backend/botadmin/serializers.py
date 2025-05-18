from rest_framework import serializers
from .models import Word, Attempt, KnownWord, RepeatSession, RepeatResult
from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'created_at']

class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = ['id', 'korean', 'uzbek', 'romanized', 'audio_file', 'created_at']

class AttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attempt
        fields = '__all__'

class KnownWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnownWord
        fields = '__all__'

class RepeatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepeatSession
        fields = '__all__'

class RepeatResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepeatResult
        fields = '__all__'
