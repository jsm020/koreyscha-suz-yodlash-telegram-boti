import os
import httpx
import random
from datetime import date

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/")


async def get_pool():
    return None  # Legacy


async def close_pool():
    return None  # Legacy


# Foydalanuvchining known words dagi so‘z id'larini olish
async def get_known_word_ids(pool, user_id):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BACKEND_URL}knownwords/?user_id={user_id}")
        resp.raise_for_status()
        data = resp.json()
        return set([item['word'] for item in data])


# So‘z qo‘shish
async def add_word(pool, korean, uzbek, romanized, audio_url):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{BACKEND_URL}words/", json={
            "korean": korean,
            "uzbek": uzbek,
            "romanized": romanized,
            "audio_url": audio_url
        })
        resp.raise_for_status()
        return resp.json()


# Attempt qo‘shish
async def add_attempt(pool, word_id, user_id, attempt_count, is_correct):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{BACKEND_URL}add_attempt/", json={
            "word": word_id,
            "user_id": user_id,
            "attempt_count": attempt_count,
            "is_correct": is_correct
        })
        resp.raise_for_status()
        return resp.json()


# KnownWord qo‘shish
async def add_known_word(pool, user_id, word_id):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{BACKEND_URL}add_known_word/", json={
            "user_id": user_id,
            "word": word_id
        })
        resp.raise_for_status()
        return resp.json()


# Sanaga qarab so‘zlar olish (va random aralashtirish)
async def get_words_by_date(pool, date=None, user_id=None):
    params = {}
    if date:
        params["date"] = str(date)
    if user_id:
        params["user_id"] = user_id

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BACKEND_URL}words_by_date/", params=params)
        resp.raise_for_status()
        return resp.json()


# Sana + user_id bo‘yicha urinishlar (har bir so‘z uchun oxirgisi)
async def get_attempts_by_user_and_date(pool, user_id, date):
    params = {"user_id": user_id, "date": str(date)}
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BACKEND_URL}attempts_by_user_and_date/", params=params)
        resp.raise_for_status()
        return resp.json()


# RepeatSession ni olish yoki yaratish (moslashtirilgan!)
async def get_or_create_repeat_session(pool, repeat_key, session_date, n=10):
    async with httpx.AsyncClient() as client:
        # Avval bor-yo‘qligini tekshiramiz
        resp = await client.get(f"{BACKEND_URL}repeatsessions/?repeat_key={repeat_key}")
        if resp.status_code == 200 and resp.json():
            return resp.json()[0]  # return full session dict

        # So‘zlar ro‘yxatini olish va aralashtirish
        words = await get_words_by_date(pool, session_date)
        word_ids = [w['id'] for w in words]
        random.shuffle(word_ids)
        word_ids = word_ids[:n]

        # Yangi session yaratish
        new_session_data = {
            "repeat_key": repeat_key,
            "date": str(session_date),
            "words": word_ids  # ManyToManyField 'words'
        }
        resp2 = await client.post(f"{BACKEND_URL}add_repeat_session/", json=new_session_data)
        resp2.raise_for_status()
        return resp2.json()


# Repeat natijasini saqlash (moslashtirilgan)
async def save_repeat_result(pool, repeat_session_id, user_id, word_id, is_correct, attempt_count):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{BACKEND_URL}add_repeat_result/", json={
            "repeat_session": repeat_session_id,  # ForeignKey id
            "user_id": user_id,
            "word": word_id,
            "is_correct": is_correct,
            "attempt_count": attempt_count
        })
        resp.raise_for_status()
        return resp.json()


# Repeat natijalarni olish
async def get_repeat_results(pool, repeat_session_id, user_id):
    params = {"repeat_key": repeat_session_id, "user_id": user_id}  # Param nomi `/repeat_results_by_user_and_key/` endpoint bilan mos
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BACKEND_URL}repeat_results_by_user_and_key/", params=params)
        resp.raise_for_status()
        return resp.json()


async def create_repeat_session(data):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{BACKEND_URL}add_repeat_session/", json=data)
        resp.raise_for_status()
        return resp.json()