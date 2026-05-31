import streamlit as st
import pandas as pd
import plotly.express as px
import requests

API_URL = "http://localhost:8000/query"

st.set_page_config(page_title="Text-to-SQL Dashboard", layout="wide")
st.title("Text-to-SQL Dashboard")
st.caption("Ask questions in plain English. Get SQL + charts instantly.")

# Sidebar: example questions
with st.sidebar:
    st.header("Example questions")
    examples = [
        "Show me top 10 distributors by total revenue",
        "Total revenue by region this year",
        "Which SKUs had the highest sales last month?",
        "Month-wise revenue trend for 2024",
        "Top 5 products by quantity sold",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state["question"] = ex

# Main input
question = st.text_input(
    "Your question",
    value=st.session_state.get("question", ""),
    placeholder="e.g. Show me top 10 distributors by revenue",
)

if st.button("Run", type="primary") and question.strip():
    with st.spinner("Generating SQL and fetching results..."):
        try:
            response = requests.post(API_URL, json={"question": question}, timeout=60)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API error: {e}")
            st.stop()

    # Show generated SQL
    with st.expander("Generated SQL", expanded=True):
        st.code(data["sql"], language="sql")

    st.caption(f"{data['row_count']} rows returned")

    df = pd.DataFrame(data["rows"], columns=data["columns"])

    # Auto chart
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    text_cols = df.select_dtypes(exclude="number").columns.tolist()

    if numeric_cols and text_cols:
        st.subheader("Chart")
        x_col = st.selectbox("X axis", text_cols)
        y_col = st.selectbox("Y axis", numeric_cols)
        chart_type = st.radio("Chart type", ["Bar", "Line", "Scatter"], horizontal=True)

        if chart_type == "Bar":
            fig = px.bar(df, x=x_col, y=y_col, title=question)
        elif chart_type == "Line":
            fig = px.line(df, x=x_col, y=y_col, title=question)
        else:
            fig = px.scatter(df, x=x_col, y=y_col, title=question)

        st.plotly_chart(fig, use_container_width=True)

    # Data table
    st.subheader("Data")
    st.dataframe(df, use_container_width=True)

    # Export
    csv = df.to_csv(index=False)
    st.download_button("Download CSV", csv, "results.csv", "text/csv")