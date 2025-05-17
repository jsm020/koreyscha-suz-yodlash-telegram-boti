from rest_framework import serializers
from .models import Word, Attempt, KnownWord, RepeatSession, RepeatResult

class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = '__all__'

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
