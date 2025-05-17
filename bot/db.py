import os
import httpx

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/")

async def get_pool():
    return None  # Legacy, not used

async def close_pool():
    return None  # Legacy, not used

# Foydalanuvchining known_words dagi so'z id larini olish
async def get_known_word_ids(pool, user_id):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BACKEND_URL}knownwords/?user_id={user_id}")
        resp.raise_for_status()
        data = resp.json()
        return set([item['word'] for item in data])

# So'z qo'shish
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

# Attempts qo'shish
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

# Known words ga qo'shish
async def add_known_word(pool, user_id, word_id):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{BACKEND_URL}add_known_word/", json={
            "user_id": user_id,
            "word": word_id
        })
        resp.raise_for_status()
        return resp.json()

# Sanalar bo'yicha so'zlar ro'yxati
async def get_words_by_date(pool, date, user_id=None):
    params = {"date": str(date)}
    if user_id is not None:
        params["user_id"] = user_id
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BACKEND_URL}words_by_date/", params=params)
        resp.raise_for_status()
        return resp.json()

# Foydalanuvchi va sana bo'yicha attempts statistikasi
async def get_attempts_by_user_and_date(pool, user_id, date):
    params = {"user_id": user_id, "date": str(date)}
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BACKEND_URL}attempts_by_user_and_date/", params=params)
        resp.raise_for_status()
        return resp.json()

# Random repeat uchun session yaratish yoki olish
async def get_or_create_repeat_session(pool, repeat_key, date, n=10):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BACKEND_URL}repeatsessions/?repeat_key={repeat_key}")
        if resp.status_code == 200 and resp.json():
            return resp.json()[0]['word_ids']
        # So'zlarni random olish uchun API orqali olamiz
        words = await get_words_by_date(pool, date)
        import random
        word_ids = [w['id'] for w in words]
        random.shuffle(word_ids)
        word_ids = word_ids[:n]
        # Yangi session yaratamiz
        resp2 = await client.post(f"{BACKEND_URL}add_repeat_session/", json={
            "repeat_key": repeat_key,
            "date": str(date),
            "word_ids": word_ids
        })
        resp2.raise_for_status()
        return word_ids

# User natijasini saqlash
async def save_repeat_result(pool, repeat_key, user_id, word_id, is_correct, attempt_count):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{BACKEND_URL}add_repeat_result/", json={
            "repeat_key": repeat_key,
            "user_id": user_id,
            "word": word_id,
            "is_correct": is_correct,
            "attempt_count": attempt_count
        })
        resp.raise_for_status()
        return resp.json()

# User natijalarini olish
async def get_repeat_results(pool, repeat_key, user_id):
    params = {"repeat_key": repeat_key, "user_id": user_id}
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BACKEND_URL}repeat_results_by_user_and_key/", params=params)
        resp.raise_for_status()
        return resp.json()