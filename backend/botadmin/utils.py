import os
from gtts import gTTS
from django.conf import settings

def romanize_korean(korean_word):
    # Bu yerda haqiqiy romanizatsiya kutubxonasi yoki API chaqirishingiz mumkin
    # Hozircha oddiy stub (o'zgartiring yoki tashqi kutubxona ulang)
    return korean_word  # TODO: haqiqiy romanizatsiya

def generate_audio(korean_word, filename):
    tts = gTTS(text=korean_word, lang='ko')
    audio_dir = os.path.join(settings.BASE_DIR, 'audio')
    os.makedirs(audio_dir, exist_ok=True)
    file_path = os.path.join(audio_dir, filename)
    tts.save(file_path)
    return f'audio/{filename}'
