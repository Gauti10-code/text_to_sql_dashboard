# Text-to-SQL

An AI-powered natural language interface for databases. Ask questions in plain English and get instant SQL queries, results, and visualizations — no SQL knowledge required.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green) ![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red) ![LangChain](https://img.shields.io/badge/LangChain-0.3%2B-yellow) ![MySQL](https://img.shields.io/badge/MySQL-8.0-orange)

---

## Overview

Text-to-SQL bridges the gap between business users and databases. Type a question like _"Show me top 10 distributors by revenue"_ and the app:

1. Converts it to a valid MySQL SELECT query using GPT-4o
2. Validates the SQL for safety (blocks injections and destructive operations)
3. Executes the query against your MySQL database
4. Renders an interactive chart and a downloadable data table

The project ships with sample FMCG (Fast-Moving Consumer Goods) data — 20,000 sales records across distributors, products, and regions — so you can try it immediately after setup.

---

## Features

- **Natural language to SQL** — GPT-4o with few-shot prompting for accurate, domain-aware query generation
- **Schema introspection** — automatically reads your database schema and injects it into the LLM prompt; no manual schema maintenance needed
- **SQL safety validation** — blocks `DROP`, `DELETE`, `UPDATE`, `INSERT`, `TRUNCATE`, comments, and multi-statement queries before execution
- **Query guardrails** — configurable row limit (default 5,000) and query timeout (default 30 s)
- **Interactive dashboard** — built with Streamlit; shows the generated SQL, lets you pick X/Y axes and chart type, and renders charts via Plotly
- **CSV export** — download any result set with one click
- **REST API** — FastAPI backend with a `/query` endpoint you can call programmatically

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | OpenAI GPT-4o via LangChain |
| Backend | FastAPI + Uvicorn |
| Database | MySQL + SQLAlchemy 2.0 |
| SQL parsing | sqlparse |
| Frontend | Streamlit + Plotly Express |
| Data | Pandas |
| Config | Pydantic Settings + python-dotenv |
| Tests | pytest + pytest-asyncio |

---

## Project Structure

```
text_to_sql/
├── app/
│   ├── main.py            # FastAPI app and /query endpoint
│   ├── chain.py           # LangChain SQL generation chain
│   ├── schema_loader.py   # Auto schema introspection via SQLAlchemy
│   ├── db.py              # DB connection and query execution
│   ├── validator.py       # SQL safety validation
│   └── config.py          # Pydantic settings (reads .env)
├── frontend/
│   └── streamlit_app.py   # Streamlit dashboard
├── data/
│   ├── seed_data.py       # Seeds sample FMCG database
│   └── schema.sql         # Reference schema
├── tests/
│   ├── test_validator.py  # Unit tests for SQL validator
│   └── test_chain.py      # Chain tests
├── .env                   # Your secrets (not committed)
├── requirements.txt
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- MySQL 8.0 running locally (or remotely)
- An [OpenAI API key](https://platform.openai.com/api-keys)

### 1. Clone and install

```bash
git clone https://github.com/your-username/text-to-sql.git
cd text-to-sql

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure environment

Create a `.env` file at the project root:

```env
# OpenAI
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.0

# MySQL
DB_HOST=localhost
DB_PORT=3306
DB_NAME=fmcg_db
DB_USER=root
DB_PASSWORD=your_password

# Guardrails
MAX_ROWS=5000
QUERY_TIMEOUT_SECONDS=30

# Optional: print generated SQL to console
DEBUG=false
```

### 3. Seed the database

This creates the `fmcg_db` database with distributors, products, and 20,000 sales records:

```bash
python data/seed_data.py
```

### 4. Start the backend

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API is now available at `http://localhost:8000`. Visit `/docs` for the interactive Swagger UI.

### 5. Start the frontend

In a separate terminal:

```bash
streamlit run frontend/streamlit_app.py
```

Open `http://localhost:8501` in your browser.

---

## Usage

### Streamlit Dashboard

1. Type your question in the text box, or click one of the example questions
2. Click **Run Query**
3. Expand **Generated SQL** to see what the model produced
4. Use the chart controls to pick axes and chart type (Bar / Line / Scatter)
5. Click **Download CSV** to export the data

### REST API

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the top 5 products by total revenue?"}'
```

Response:

```json
{
  "sql": "SELECT product_name, SUM(revenue) AS total_revenue FROM sales ...",
  "columns": ["product_name", "total_revenue"],
  "rows": [["Amul Ghee", 1250000.0], ...],
  "row_count": 5
}
```

### Example Questions

- _Show me total sales by region for 2024_
- _Which distributor has the highest average order value?_
- _What is the month-over-month revenue growth?_
- _List the top 10 distributors by revenue_
- _Show me products with declining sales in Q4 2024_

---

## How It Works

```
User Question
     │
     ▼
┌─────────────────────────────────────────┐
│  LangChain Chain (chain.py)             │
│  - Load schema via introspection        │
│  - Build prompt with schema + examples  │
│  - Call GPT-4o                          │
└─────────────────────────────────────────┘
     │ raw SQL
     ▼
┌─────────────────────────────────────────┐
│  SQL Validator (validator.py)           │
│  - Strip markdown fences                │
│  - Block dangerous keywords             │
│  - Block multi-statement queries        │
│  - Block SQL comments                   │
└─────────────────────────────────────────┘
     │ safe SQL
     ▼
┌─────────────────────────────────────────┐
│  Query Executor (db.py)                 │
│  - Execute with timeout                 │
│  - Cap at MAX_ROWS rows                 │
│  - Return as Pandas DataFrame           │
└─────────────────────────────────────────┘
     │ results
     ▼
  Streamlit UI — chart + table + CSV
```

---

## Running Tests

```bash
pytest tests/ -v
```

The test suite covers SQL validation edge cases: valid SELECT queries, markdown stripping, dangerous keyword blocking, injection attempts, multi-statement blocking, and aggregation queries.

---

## Configuration Reference

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | OpenAI secret key (required) |
| `OPENAI_MODEL` | `gpt-4o` | Model to use for SQL generation |
| `OPENAI_TEMPERATURE` | `0.0` | Deterministic output; increase for variety |
| `DB_HOST` | `localhost` | MySQL host |
| `DB_PORT` | `3306` | MySQL port |
| `DB_NAME` | `fmcg_db` | Database name |
| `DB_USER` | `root` | MySQL user |
| `DB_PASSWORD` | — | MySQL password (required) |
| `MAX_ROWS` | `5000` | Maximum rows returned per query |
| `QUERY_TIMEOUT_SECONDS` | `30` | Query execution timeout |
| `DEBUG` | `false` | Log generated SQL to console |

---

## Security

The validator enforces **SELECT-only** access:

- Blocks `DROP`, `DELETE`, `UPDATE`, `INSERT`, `TRUNCATE`, `ALTER`, `CREATE`, `EXEC`
- Blocks SQL comments (`--`, `/* */`)
- Blocks stacked/multi-statement queries (`;` separators)
- Strips LLM markdown code fences before parsing

The application connects with the credentials you supply in `.env`. For production use, create a read-only MySQL user scoped to your target database.

---

## License

MIT
