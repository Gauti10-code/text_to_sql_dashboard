# app/history.py
from sqlalchemy import text
from app.db import engine
from datetime import datetime


CREATE_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS query_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question TEXT NOT NULL,
    generated_sql TEXT NOT NULL,
    row_count INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'success',
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


def init_history_table():
    with engine.begin() as conn:
        conn.execute(text(CREATE_HISTORY_TABLE))


def save_query(question: str, sql: str, row_count: int, status: str = "success", error: str = None):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO query_history (question, generated_sql, row_count, status, error_message)
            VALUES (:question, :sql, :row_count, :status, :error)
        """), {
            "question": question,
            "sql": sql,
            "row_count": row_count,
            "status": status,
            "error": error,
        })


def get_history(limit: int = 50):
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, question, generated_sql, row_count, status, error_message, created_at
            FROM query_history
            ORDER BY created_at DESC
            LIMIT :limit
        """), {"limit": limit})
        columns = list(result.keys())
        rows = result.fetchall()
    return columns, rows


def delete_history():
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM query_history"))