
from hangul_romanize import Transliter
from hangul_romanize.rule import academic
from gtts import gTTS
import os

def romanize_korean(text):
    """
    Koreyscha so'zni lotin transkripsiyasiga o'tkazadi.
    Misol: 학교 -> hakgyo
    """
    transliter = Transliter(academic)
    return transliter.translit(text)

def generate_korean_audio(text, filename):
    """
    Koreyscha so'z uchun audio fayl yaratadi (gTTS).
    """
    tts = gTTS(text, lang='ko')
    tts.save(filename)
    return filename

