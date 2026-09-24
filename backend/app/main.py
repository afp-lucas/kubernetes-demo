import os

import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(title="Essay Manager API")


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "essays")
DB_USER = os.getenv("DB_USER", "essay_user")
DB_PASSWORD_FILE = os.getenv("DB_PASSWORD_FILE")


def get_db_password():
    if DB_PASSWORD_FILE:
        with open(DB_PASSWORD_FILE, "r") as file:
            return file.read().strip()

    return os.getenv("DB_PASSWORD", "essay_password")


class EssayCreate(BaseModel):
    title: str
    text: str
    score: int | None = None


def get_connection():
    return psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=get_db_password(),
    )


def create_table():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS essays (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    text TEXT NOT NULL,
                    score INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)


@app.on_event("startup")
def startup():
    create_table()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/essays")
def list_essays():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, title, text, score
                FROM essays
                ORDER BY id;
            """)

            rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "title": row[1],
            "text": row[2],
            "score": row[3],
        }
        for row in rows
    ]


@app.post("/essays", status_code=201)
def create_essay(essay: EssayCreate):
    if essay.score is not None and not 0 <= essay.score <= 1000:
        raise HTTPException(
            status_code=400,
            detail="A nota deve estar entre 0 e 1000",
        )

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO essays (title, text, score)
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (essay.title, essay.text, essay.score),
            )

            essay_id = cursor.fetchone()[0]

    return {
        "id": essay_id,
        "title": essay.title,
        "text": essay.text,
        "score": essay.score,
    }