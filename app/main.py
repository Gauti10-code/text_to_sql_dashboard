from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from app.chain import generate_sql
from app.validator import validate_sql, UnsafeSQLError
from app.db import run_query, test_connection
from app.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_title)


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    question: str
    sql: str
    columns: list[str]
    rows: list[list]
    row_count: int


@app.on_event("startup")
def startup_check():
    if not test_connection():
        raise RuntimeError("Cannot connect to MySQL. Check your .env credentials.")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    # Step 1: Generate SQL from natural language
    try:
        raw_sql = generate_sql(request.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

    # Step 2: Validate SQL
    try:
        safe_sql = validate_sql(raw_sql)
    except UnsafeSQLError as e:
        raise HTTPException(status_code=400, detail=f"Unsafe SQL: {str(e)}")

    # Step 3: Execute query
    try:
        df: pd.DataFrame = run_query(safe_sql)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution error: {str(e)}")

    return QueryResponse(
        question=request.question,
        sql=safe_sql,
        columns=df.columns.tolist(),
        rows=df.values.tolist(),
        row_count=len(df),
    )