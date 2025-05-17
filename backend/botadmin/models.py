from django.db import models

class Word(models.Model):
    korean = models.CharField(max_length=255)
    uzbek = models.CharField(max_length=255)
    romanized = models.CharField(max_length=255, blank=True, null=True)
    audio_url = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.korean

class Attempt(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    user_id = models.BigIntegerField()
    attempt_count = models.IntegerField()
    is_correct = models.BooleanField()
    attempted_at = models.DateTimeField(auto_now_add=True)

class KnownWord(models.Model):
    user_id = models.BigIntegerField()
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user_id", "word")

class RepeatSession(models.Model):
    repeat_key = models.CharField(max_length=255)
    date = models.DateField()
    word_ids = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

class RepeatResult(models.Model):
    repeat_key = models.CharField(max_length=255)
    user_id = models.BigIntegerField()
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    is_correct = models.BooleanField(blank=True, null=True)
    attempt_count = models.IntegerField(blank=True, null=True)
    finished_at = models.DateTimeField(auto_now_add=True)
