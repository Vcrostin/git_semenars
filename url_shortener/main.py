from enum import Enum
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import random
import string
import psycopg2

app = FastAPI()


class Url(BaseModel):
    url: str


db_cridentials = {
    "dbname":"app_db",
    "user":"user",
    "password":"password",
    "host":"postgre",
    "port":"5432"
}


# для тестов удобно использовать 1. В целом думаю разумно использовать значения до 10 включительно
SHORTEN_URL_LEN=1


with psycopg2.connect(
    **db_cridentials
) as conn:
    with conn.cursor() as cur:
        # Создание таблицы shorten_urls с двумя столбцами: shorten_url и original_url
        cur.execute('''
        	CREATE TABLE IF NOT EXISTS shorten_urls (
                shorten_url TEXT PRIMARY KEY,
                original_url TEXT,
                ts timestamp default now()
            );
        ''')
        conn.commit()


@app.post("/shorten")
def shorten_url(original_url: Url) -> str:
    try:
        letters = string.ascii_lowercase
        shorten_url = ''.join(random.choice(letters) for i in range(SHORTEN_URL_LEN))
        with psycopg2.connect(
            **db_cridentials
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(f'''
                    INSERT INTO shorten_urls VALUES ('{shorten_url}', '{original_url.url}');
                ''')
                conn.commit()
            return shorten_url

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="It is not your day. Try again later")


def lookup_original_url(short_id: str):
    with psycopg2.connect(
            **db_cridentials
        ):
            with conn.cursor() as cur:
                cur.execute(f'''
                    SELECT original_url from shorten_urls where shorten_url = '{short_id}';
                ''')
                return cur.fetchone()[0]


# использую query params из-за частого обращения к / сторонними запросами (например favicon.ico и прочее)
@app.get("/")
def redir2original(short_id: str) -> RedirectResponse:
    try:
        return RedirectResponse(lookup_original_url(short_id), status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="There isn't such url in database")


@app.get("/stats/{short_id}")
def get_stats(short_id: str) -> Url:
    try:
        return Url(url=lookup_original_url(short_id))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="There isn't such url in database")
