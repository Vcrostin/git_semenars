from enum import Enum
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import random
import string
import psycopg2
import uuid

app = FastAPI()


class Task(BaseModel):
    title: str
    description: str|None
    completed: bool


db_cridentials = {
    "dbname":"app_db",
    "user":"user",
    "password":"password",
    "host":"postgre",
    "port":"5432"
}


with psycopg2.connect(
    **db_cridentials
) as conn:
    with conn.cursor() as cur:
        # Создание таблицы shorten_urls с двумя столбцами: shorten_url и original_url
        cur.execute('''
        	CREATE TABLE IF NOT EXISTS tasks_table (
                task_id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                completed boolean
            );
        ''')
        conn.commit()


def contruct_task_from_fetch_result(fetch_result):
    return Task(title=fetch_result[1], description=fetch_result[2], completed=fetch_result[3])


@app.post("/items")
def create_task(task: Task) -> str:
    id = str(uuid.uuid4())

    with psycopg2.connect(
        **db_cridentials
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(f'''
                INSERT INTO tasks_table VALUES ('{id}', '{task.title}', '{task.description}', '{task.completed}');
            ''')
            conn.commit()
        return id


@app.get("/items")
def get_tasks() -> list[Task]:
    try:
        with psycopg2.connect(
            **db_cridentials
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(f'''
                    select * from tasks_table;
                ''')
                return [contruct_task_from_fetch_result(pre_task) for pre_task in cur.fetchall()]

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="It is not your day. Try again later")


def lookup_original_task(id: str) -> Task:
    with psycopg2.connect(
            **db_cridentials
        ):
            with conn.cursor() as cur:
                cur.execute(f'''
                    SELECT * from tasks_table where task_id = '{id}';
                ''')
                return contruct_task_from_fetch_result(cur.fetchone())


@app.get("/items/{item_id}")
def get_task(item_id: str) -> Task:
    try:
        return lookup_original_task(item_id)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="It is not your day. Try again later")


def update_original_task(id:str, task: Task) -> None:
    with psycopg2.connect(
            **db_cridentials
        ):
            with conn.cursor() as cur:
                cur.execute(f'''
                    UPDATE tasks_table SET title = '{task.title}', description = '{task.description}', completed = '{task.completed}' where task_id = '{id}';
                ''')
                conn.commit()


@app.put("/items/{item_id}")
def update_task(item_id: str, task: Task) -> None:
    try:
        update_original_task(item_id, task)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="It is not your day. Try again later")


def remove_original_task(id: str) -> None:
    with psycopg2.connect(
            **db_cridentials
        ):
            with conn.cursor() as cur:
                cur.execute(f'''
                    DELETE from tasks_table where task_id = '{id}';
                ''')
                conn.commit()


@app.delete("/items")
def remove_task(id: str) -> None:
    try:
        remove_original_task(id)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="It is not your day. Try again later")
