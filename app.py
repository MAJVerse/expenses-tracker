import sqlite3
from datetime import date

import pandas as pd
import streamlit as st

DB_FILE = "expenses.db"

st.set_page_config(page_title="Expense Tracker", page_icon="💸", layout="centered")


# ---------- Database ----------
def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def add_expense(amount, category, description, when):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)",
            (amount, category.strip().title(), description.strip(), when.isoformat()),
        )


def delete_expense(expense_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))


def load_expenses():
    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT id, date, amount, category, description FROM expenses ORDER BY date DESC, id DESC",
        conn,
    )
    conn.close()
    return df


# ---------- UI ----------
st.title("💸 Personal Expense Tracker")
st.caption("Add, search, and manage your spending.")

df = load_expenses()

# Summary
col1, col2 = st.columns(2)
col1.metric("Total spending", f"₦{df['amount'].sum():,.2f}")
col2.metric("Expenses recorded", len(df))

tab_add, tab_view, tab_summary, tab_delete = st.tabs(
    ["➕ Add", "📋 View & Search", "📊 By Category", "🗑️ Delete"]
)

with tab_add:
    with st.form("add_form", clear_on_submit=True):
        amount = st.number_input("Amount (₦)", min_value=0.0, step=100.0, format="%.2f")
        category = st.text_input("Category", placeholder="e.g. Food, Transport")
        description = st.text_input("Description")
        when = st.date_input("Date", value=date.today())
        submitted = st.form_submit_button("Add expense")
    if submitted:
        if amount <= 0:
            st.error("Amount must be greater than zero.")
        elif not category.strip():
            st.error("Please enter a category.")
        else:
            add_expense(amount, category, description, when)
            st.success("Expense added!")
            st.rerun()

with tab_view:
    if df.empty:
        st.info("No expenses recorded yet.")
    else:
        keyword = st.text_input("Search (category or description)")
        categories = ["All"] + sorted(df["category"].unique().tolist())
        chosen = st.selectbox("Filter by category", categories)

        view = df
        if keyword:
            k = keyword.lower()
            view = view[
                view["category"].str.lower().str.contains(k, na=False)
                | view["description"].fillna("").str.lower().str.contains(k)
            ]
        if chosen != "All":
            view = view[view["category"] == chosen]

        st.dataframe(
            view,
            use_container_width=True,
            hide_index=True,
            column_config={"amount": st.column_config.NumberColumn("amount", format="₦%.2f")},
        )
        st.write(f"**Total of shown expenses:** ₦{view['amount'].sum():,.2f}")

with tab_summary:
    if df.empty:
        st.info("No expenses recorded yet.")
    else:
        by_cat = (
            df.groupby("category")["amount"].sum().sort_values(ascending=False).reset_index()
        )
        st.bar_chart(by_cat, x="category", y="amount")
        by_cat["amount"] = by_cat["amount"].map(lambda v: f"₦{v:,.2f}")
        st.dataframe(by_cat, use_container_width=True, hide_index=True)

with tab_delete:
    if df.empty:
        st.info("Nothing to delete.")
    else:
        options = {
            int(r.id): f"{r.date} · ₦{r.amount:,.2f} · {r.category} · {r.description}"
            for r in df.itertuples()
        }
        picked = st.selectbox(
            "Choose an expense", list(options.keys()), format_func=lambda i: options[i]
        )
        if st.button("Delete selected expense", type="primary"):
            delete_expense(picked)
            st.success("Expense deleted.")
            st.rerun()
