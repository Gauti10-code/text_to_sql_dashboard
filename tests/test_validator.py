import pytest
from app.validator import validate_sql, UnsafeSQLError, extract_sql


def test_valid_select():
    sql = "SELECT * FROM sales LIMIT 10"
    assert validate_sql(sql) == sql


def test_strips_markdown_fences():
    raw = "```sql\nSELECT * FROM sales\n```"
    result = extract_sql(raw)
    assert result == "SELECT * FROM sales"


def test_blocks_drop():
    with pytest.raises(UnsafeSQLError):
        validate_sql("DROP TABLE sales")


def test_blocks_delete():
    with pytest.raises(UnsafeSQLError):
        validate_sql("DELETE FROM sales WHERE id = 1")


def test_blocks_multiple_statements():
    with pytest.raises(UnsafeSQLError):
        validate_sql("SELECT * FROM sales; DROP TABLE sales")


def test_blocks_comments():
    with pytest.raises(UnsafeSQLError):
        validate_sql("SELECT * FROM sales -- comment")


def test_valid_aggregation():
    sql = "SELECT region, SUM(revenue) FROM sales GROUP BY region ORDER BY SUM(revenue) DESC LIMIT 10"
    assert validate_sql(sql) == sql