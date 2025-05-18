import os
from gtts import gTTS
from django.conf import settings

from hangul_romanize import Transliter
from hangul_romanize.rule import academic

# Transliter obyektini yaratamiz (1 marta)
transliter = Transliter(academic)

def romanize_korean(korean_word):
    return transliter.translit(korean_word)


def generate_audio_file(korean_word, filename):
    """
    So‘z uchun mp3 fayl yaratadi va media/audio/ga saqlaydi.
    FileField uchun nisbiy yo‘lni qaytaradi.
    """
    audio_dir = os.path.join(settings.MEDIA_ROOT, 'audios')
    os.makedirs(audio_dir, exist_ok=True)

    file_path = os.path.join(audio_dir, filename)
    tts = gTTS(text=korean_word, lang='ko')
    tts.save(file_path)

    # FileField uchun nisbiy yo‘l (MEDIA_ROOT'dan nisbatan)
    return f'audios/{filename}'
