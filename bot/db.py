import os
import httpx
import random
from datetime import date

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/")


async def get_pool():
    return None  # Legacy


async def close_pool():
    return None  # Legacy

async def get_words_by_category(pool, category_name):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BACKEND_URL}words_by_category/", params={"category": category_name})
        resp.raise_for_status()
        return resp.json()

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
        print(user_id, word_id)
        return resp.json()

async def get_all_categories():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BACKEND_URL}categories/")
        resp.raise_for_status()
        return resp.json()
# Sanaga qarab so‘zlar olish (va random aralashtirish)
async def get_words_by_date(pool, category=None, user_id=None):
    params = {}
    if date:
        params["category"] = str(category)
    if user_id:
        params["user_id"] = user_id

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BACKEND_URL}words_by_date/", params=params)
        resp.raise_for_status()
        return resp.json()


# Sana + user_id bo‘yicha urinishlar (har bir so‘z uchun oxirgisi)
async def get_attempts_by_user_and_category(pool, user_id, category):
    params = {"user_id": user_id, "category": category}
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BACKEND_URL}attempts_by_user_and_category/", params=params)
        resp.raise_for_status()
        return resp.json()


# RepeatSession ni olish yoki yaratish (moslashtirilgan!)


async def get_or_create_repeat_session_by_category(pool, repeat_key, category_name, n=10):
    async with httpx.AsyncClient() as client:
        # 1. Mavjud session bormi?
        resp = await client.get(f"{BACKEND_URL}repeatsessions/?repeat_key={repeat_key}")
        if resp.status_code == 200 and resp.json():
            return resp.json()[0]

        # 2. Category ID ni olish
        cat_resp = await client.get(f"{BACKEND_URL}categories/?name={category_name}")
        if cat_resp.status_code != 200 or not cat_resp.json():
            return None
        category_id = cat_resp.json()[0]['id']

        # 3. So‘zlar olish
        words = await get_words_by_category(pool, category_name)
        if not words:
            return None

        word_ids = [w['id'] for w in words]
        random.shuffle(word_ids)
        word_ids = word_ids[:n]

        # 4. Sessionni yaratish
        session_data = {
            "repeat_key": repeat_key,
            "date": str(date.today()),
            "category": category_id,
            "words": word_ids  # JSONField yoki POST so‘rov ichida ishlashi kerak
        }

        resp2 = await client.post(f"{BACKEND_URL}add_repeat_session/", json=session_data)
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

