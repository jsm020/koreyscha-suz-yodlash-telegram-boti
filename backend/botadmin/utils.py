import os
from gtts import gTTS
from django.conf import settings


def romanize_korean(korean_word):
    # TODO: haqiqiy romanizatsiya kutubxonasini ulang
    return korean_word  # Hozircha faqat qaytaradi


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
