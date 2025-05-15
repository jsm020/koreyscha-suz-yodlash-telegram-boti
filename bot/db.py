

import os
import asyncpg
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# So'zlar jadvali va attempts jadvali uchun SQL
CREATE_WORDS_TABLE = """
CREATE TABLE IF NOT EXISTS words (
    id SERIAL PRIMARY KEY,
    korean TEXT NOT NULL,
    uzbek TEXT NOT NULL,
    romanized TEXT NOT NULL,
    audio_url TEXT,
    created_at DATE DEFAULT CURRENT_DATE
);
"""

CREATE_ATTEMPTS_TABLE = """
CREATE TABLE IF NOT EXISTS attempts (
    id SERIAL PRIMARY KEY,
    word_id INTEGER REFERENCES words(id),
    user_id BIGINT,
    attempt_count INTEGER,
    is_correct BOOLEAN,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Global pool
pool = None

async def get_pool():
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(DATABASE_URL)
    return pool

async def close_pool():
    global pool
    if pool is not None:
        await pool.close()
        pool = None

async def init_db():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(CREATE_WORDS_TABLE)
        await conn.execute(CREATE_ATTEMPTS_TABLE)

# So'z qo'shish
async def add_word(pool, korean, uzbek, romanized, audio_url):
    query = """
    INSERT INTO words (korean, uzbek, romanized, audio_url)
    VALUES ($1, $2, $3, $4)
    RETURNING id, created_at;
    """
    async with pool.acquire() as conn:
        return await conn.fetchrow(query, korean, uzbek, romanized, audio_url)

# Attempts qo'shish
async def add_attempt(pool, word_id, user_id, attempt_count, is_correct):
    query = """
    INSERT INTO attempts (word_id, user_id, attempt_count, is_correct)
    VALUES ($1, $2, $3, $4)
    RETURNING id;
    """
    async with pool.acquire() as conn:
        return await conn.fetchrow(query, word_id, user_id, attempt_count, is_correct)

# Sanalar bo'yicha so'zlar ro'yxati
from datetime import datetime, date as dt_date
import random
async def get_words_by_date(pool, date, user_id=None):
    # date string bo'lsa, uni date tipiga aylantiramiz
    if isinstance(date, str):
        date = datetime.strptime(date, "%Y-%m-%d").date()
    query = "SELECT * FROM words WHERE created_at = $1;"
    async with pool.acquire() as conn:
        words = await conn.fetch(query, date)
        # Agar user_id berilgan bo'lsa, attempts soni bo'yicha tartiblash
        if user_id is not None:
            # Har bir so'z uchun attempts sonini topamiz
            word_ids = [w['id'] for w in words]
            if word_ids:
                attempts_query = f"""
                    SELECT word_id, COUNT(*) as cnt
                    FROM attempts
                    WHERE user_id = $1 AND word_id = ANY($2::int[])
                    GROUP BY word_id
                """
                attempts = await conn.fetch(attempts_query, user_id, word_ids)
                attempts_map = {a['word_id']: a['cnt'] for a in attempts}
                # So'zlarni attempts soni bo'yicha kamayish tartibida, so'ng random aralashtiramiz
                words = sorted(words, key=lambda w: (-attempts_map.get(w['id'], 0), random.random()))
            else:
                random.shuffle(words)
        else:
            random.shuffle(words)
        return words

# Foydalanuvchi va sana bo'yicha attempts statistikasi
async def get_attempts_by_user_and_date(pool, user_id, date):
    # Har bir so'z uchun eng so'nggi urinishni olish
    query = """
    SELECT w.korean, w.uzbek, a.attempt_count, a.is_correct, a.word_id, a.attempted_at
    FROM attempts a
    JOIN words w ON a.word_id = w.id
    WHERE a.user_id = $1 AND w.created_at = $2
    ORDER BY a.word_id, a.attempted_at DESC
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, user_id, date)
        # Har bir word_id uchun faqat eng so'nggi urinishni olish
        last_attempts = {}
        for row in rows:
            wid = row['word_id']
            if wid not in last_attempts:
                last_attempts[wid] = row
        return list(last_attempts.values())

