from django.db import models

class Word(models.Model):
    id = models.AutoField(primary_key=True)
    korean = models.TextField()
    uzbek = models.TextField()
    romanized = models.TextField()
    audio_url = models.TextField(blank=True, null=True)
    created_at = models.DateField()

    class Meta:
        db_table = 'words'

    def __str__(self):
        return self.korean

class Attempt(models.Model):
    id = models.AutoField(primary_key=True)
    word = models.ForeignKey(Word, db_column='word_id', on_delete=models.CASCADE)
    user_id = models.BigIntegerField()
    attempt_count = models.IntegerField()
    is_correct = models.BooleanField()
    attempted_at = models.DateTimeField()

    class Meta:
        db_table = 'attempts'

class KnownWord(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.BigIntegerField()
    word = models.ForeignKey(Word, db_column='word_id', on_delete=models.CASCADE)
    added_at = models.DateTimeField()

    class Meta:
        db_table = 'known_words'
        unique_together = ("user_id", "word")

class RepeatSession(models.Model):
    id = models.AutoField(primary_key=True)
    repeat_key = models.TextField()
    date = models.DateField()
    word_ids = models.JSONField()
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'repeat_sessions'

class RepeatResult(models.Model):
    id = models.AutoField(primary_key=True)
    repeat_key = models.TextField()
    user_id = models.BigIntegerField()
    word = models.ForeignKey(Word, db_column='word_id', on_delete=models.CASCADE)
    is_correct = models.BooleanField(null=True)
    attempt_count = models.IntegerField(null=True)
    finished_at = models.DateTimeField()

    class Meta:
        db_table = 'repeat_results'
