from django.contrib import admin
from .models import Word, Attempt, KnownWord, RepeatSession, RepeatResult

admin.site.register(Word)
admin.site.register(Attempt)
admin.site.register(KnownWord)
admin.site.register(RepeatSession)
admin.site.register(RepeatResult)
