from sqlalchemy import inspect, text
from app.db import engine


def get_schema_string() -> str:
    """
    Introspects the MySQL DB and returns a DDL-style string
    injected into the LLM prompt so it knows the table structure.
    """
    inspector = inspect(engine)#connects to mysql and reads the info schema
    tables = inspector.get_table_names()
    schema_parts = []

    for table in tables:
        #metadata
        columns = inspector.get_columns(table)
        pk = inspector.get_pk_constraint(table)
        fks = inspector.get_foreign_keys(table)

        col_defs = []
        for col in columns:
            col_type = str(col["type"])
            nullable = "" if col["nullable"] else " NOT NULL"
            col_defs.append(f"  {col['name']} {col_type}{nullable}")

        if pk and pk.get("constrained_columns"):
            col_defs.append(f"  PRIMARY KEY ({', '.join(pk['constrained_columns'])})")

        for fk in fks:
            col_defs.append(
                f"  FOREIGN KEY ({', '.join(fk['constrained_columns'])}) "
                f"REFERENCES {fk['referred_table']}({', '.join(fk['referred_columns'])})"
            )

        schema_parts.append(f"CREATE TABLE {table} (\n" + ",\n".join(col_defs) + "\n);")

    return "\n\n".join(schema_parts)


def get_sample_rows(table: str, n: int = 3) -> str:
    """
    Returns n sample rows from a table as a string.
    Helps the LLM understand actual data values and formats.
    """
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT * FROM {table} LIMIT {n}"))
        rows = result.fetchall()
        columns = list(result.keys())

    if not rows:
        return f"-- {table}: no data"

    header = " | ".join(columns)
    lines = [header, "-" * len(header)]
    for row in rows:
        lines.append(" | ".join(str(v) for v in row))

    return f"-- Sample rows from {table}:\n" + "\n".join(lines)