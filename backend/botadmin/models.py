import os
from django.db import models
from django.utils.text import slugify


def audio_upload_path(instance, filename):
    base, ext = os.path.splitext(filename)
    filename = f"{slugify(instance.korean)}{ext}"
    return os.path.join("audios", filename)


class Word(models.Model):
    id = models.AutoField(primary_key=True)
    korean = models.TextField()
    uzbek = models.TextField()
    romanized = models.TextField(blank=True, null=True)
    audio_file = models.FileField(upload_to=audio_upload_path, blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'words'

    def __str__(self):
        return self.korean

    def save(self, *args, **kwargs):
        from .utils import romanize_korean, generate_audio_file
        if not self.romanized:
            self.romanized = romanize_korean(self.korean)
        if not self.audio_file:
            filename = f"{slugify(self.korean)}.mp3"
            audio_path = generate_audio_file(self.korean, filename)
            self.audio_file.name = audio_path
        super().save(*args, **kwargs)


class Attempt(models.Model):
    id = models.AutoField(primary_key=True)
    word = models.ForeignKey(Word, db_column='word_id', on_delete=models.CASCADE)
    user_id = models.BigIntegerField()
    attempt_count = models.IntegerField()
    is_correct = models.BooleanField()
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'attempts'

    def __str__(self):
        return f"User {self.user_id} - {self.word.korean} - {'✅' if self.is_correct else '❌'}"


class KnownWord(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.BigIntegerField()
    word = models.ForeignKey(Word, db_column='word_id', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'known_words'
        unique_together = ("user_id", "word")

    def __str__(self):
        return f"{self.user_id} knows {self.word.korean}"


class RepeatSession(models.Model):
    id = models.AutoField(primary_key=True)
    repeat_key = models.TextField(unique=True)
    date = models.DateField()
    words = models.ManyToManyField(Word, related_name='repeat_sessions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'repeat_sessions'

    def __str__(self):
        return f"Session {self.repeat_key} - {self.date}"


class RepeatResult(models.Model):
    id = models.AutoField(primary_key=True)
    repeat_session = models.ForeignKey(RepeatSession, db_column='repeat_key', on_delete=models.CASCADE)
    user_id = models.BigIntegerField()
    word = models.ForeignKey(Word, db_column='word_id', on_delete=models.CASCADE)
    is_correct = models.BooleanField(null=True, blank=True)
    attempt_count = models.IntegerField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'repeat_results'

    def __str__(self):
        return f"Result: {self.user_id} - {self.word.korean} - {'✅' if self.is_correct else '❌'}"
