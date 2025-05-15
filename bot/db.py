
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

async def get_pool():
    return await asyncpg.create_pool(DATABASE_URL)

async def init_db():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(CREATE_WORDS_TABLE)
        await conn.execute(CREATE_ATTEMPTS_TABLE)
    await pool.close()

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
async def get_words_by_date(pool, date):
    query = "SELECT * FROM words WHERE created_at = $1;"
    async with pool.acquire() as conn:
        return await conn.fetch(query, date)

# Foydalanuvchi va sana bo'yicha attempts statistikasi
async def get_attempts_by_user_and_date(pool, user_id, date):
    query = """
    SELECT w.korean, w.uzbek, a.attempt_count, a.is_correct
    FROM attempts a
    JOIN words w ON a.word_id = w.id
    WHERE a.user_id = $1 AND w.created_at = $2;
    """
    async with pool.acquire() as conn:
        return await conn.fetch(query, user_id, date)

