from django import forms
from botadmin.models import Category, Word, Attempt, KnownWord, RepeatSession, RepeatResult

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class WordForm(forms.ModelForm):
    class Meta:
        model = Word
        fields = ['korean', 'uzbek', 'romanized', 'audio_file', 'category']
        widgets = {
            'korean': forms.TextInput(attrs={'class': 'form-control'}),
            'uzbek': forms.TextInput(attrs={'class': 'form-control'}),
            'romanized': forms.TextInput(attrs={'class': 'form-control'}),
            'audio_file': forms.FileInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

class AttemptForm(forms.ModelForm):
    class Meta:
        model = Attempt
        fields = ['word', 'user_id', 'attempt_count', 'is_correct']
        widgets = {
            'word': forms.Select(attrs={'class': 'form-control'}),
            'user_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'attempt_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class KnownWordForm(forms.ModelForm):
    class Meta:
        model = KnownWord
        fields = ['user_id', 'word']
        widgets = {
            'user_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'word': forms.Select(attrs={'class': 'form-control'}),
        }

class RepeatSessionForm(forms.ModelForm):
    class Meta:
        model = RepeatSession
        fields = ['repeat_key', 'date', 'category']
        widgets = {
            'repeat_key': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

class RepeatResultForm(forms.ModelForm):
    class Meta:
        model = RepeatResult
        fields = ['repeat_session', 'user_id', 'word', 'is_correct', 'attempt_count', 'finished_at']
        widgets = {
            'repeat_session': forms.Select(attrs={'class': 'form-control'}),
            'user_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'word': forms.Select(attrs={'class': 'form-control'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'attempt_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'finished_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }