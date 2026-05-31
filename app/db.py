# app/db.py
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from app.config import get_settings

settings = get_settings()


engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,        # drops stale connections automatically
    echo=settings.debug,       # logs SQL to console when DEBUG=true
)


def run_query(sql: str) -> pd.DataFrame:
    """
    Execute a SELECT query and return results as a DataFrame.
    Raises on timeout or any DB error — caller handles the exception.
    """
    with engine.connect() as conn:
        conn.execute(text(f"SET SESSION max_execution_time={settings.query_timeout_seconds * 1000}"))
        result = conn.execute(text(sql))
        rows = result.fetchmany(settings.max_rows)
        columns = list(result.keys())
    return pd.DataFrame(rows, columns=columns)


def test_connection() -> bool:
    """
    Ping the DB. Used at startup to fail fast if credentials are wrong.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"DB connection failed: {e}")
        return False