from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.config import get_settings
from app.schema_loader import get_schema_string

settings = get_settings()

SYSTEM_PROMPT = """
You are an expert SQL assistant. Your job is to convert natural language questions into valid MySQL SELECT queries.

Rules:
- Only generate SELECT statements. Never use DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE.
- Always use table and column names exactly as they appear in the schema.
- If a question is ambiguous, make a reasonable assumption and write the query.
- Return ONLY the raw SQL query with no explanation, no markdown, no code fences.
- Always add a LIMIT clause if the user does not specify one (default LIMIT 100).

Schema:
{schema}

Few-shot examples:
Q: Show me top 5 distributors by total revenue
A: SELECT distributor_name, SUM(revenue) AS total_revenue FROM sales GROUP BY distributor_name ORDER BY total_revenue DESC LIMIT 5;

Q: Which SKUs had declining sales last month compared to the month before?
A: SELECT sku_name, SUM(CASE WHEN MONTH(sale_date) = MONTH(CURDATE()) - 1 THEN quantity ELSE 0 END) AS last_month, SUM(CASE WHEN MONTH(sale_date) = MONTH(CURDATE()) - 2 THEN quantity ELSE 0 END) AS prev_month FROM sales JOIN products ON sales.product_id = products.id GROUP BY sku_name HAVING last_month < prev_month;

Q: Total revenue by region for this year
A: SELECT region, SUM(revenue) AS total_revenue FROM sales WHERE YEAR(sale_date) = YEAR(CURDATE()) GROUP BY region ORDER BY total_revenue DESC;

Q: Month wise top 3 distributors by sales
A: SELECT sale_month, distributor_name, total_sales FROM (SELECT DATE_FORMAT(s.sale_date, '%Y-%m') AS sale_month, d.distributor_name, SUM(s.quantity) AS total_sales, RANK() OVER (PARTITION BY DATE_FORMAT(s.sale_date, '%Y-%m') ORDER BY SUM(s.quantity) DESC) AS rnk FROM sales s JOIN distributors d ON s.distributor_id = d.id GROUP BY sale_month, d.distributor_name) ranked WHERE rnk <= 3 ORDER BY sale_month, rnk;
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{question}"),
])

llm = ChatOpenAI(
    model=settings.openai_model,
    temperature=settings.openai_temperature,
    api_key=settings.openai_api_key,
)

chain = prompt | llm | StrOutputParser()


def generate_sql(question: str) -> str:
    schema = get_schema_string()
    return chain.invoke({"question": question, "schema": schema})