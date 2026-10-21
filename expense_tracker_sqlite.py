import sqlite3
from datetime import date, datetime

DB_FILE = "expenses.db"


# ---------- Database ----------
def connect():
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


# ---------- Input helpers ----------
def ask_amount():
    while True:
        try:
            amount = float(input("Enter amount: ₦").replace(",", ""))
        except ValueError:
            print("Invalid amount. Please enter a number.")
            continue
        if amount <= 0:
            print("Amount must be greater than zero.")
            continue
        return amount


def ask_date():
    while True:
        text = input("Enter date (YYYY-MM-DD, press Enter for today): ").strip()
        if not text:
            return date.today().isoformat()
        try:
            return datetime.strptime(text, "%Y-%m-%d").date().isoformat()
        except ValueError:
            print("Invalid date. Use the format YYYY-MM-DD.")


def ask_nonempty(prompt):
    while True:
        text = input(prompt).strip()
        if text:
            return text
        print("This field cannot be empty.")


# ---------- Features ----------
def add_expense(conn):
    amount = ask_amount()
    category = ask_nonempty("Enter category: ").title()
    description = input("Enter description: ").strip()
    when = ask_date()
    conn.execute(
        "INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)",
        (amount, category, description, when),
    )
    conn.commit()
    print("Expense added!")


def print_table(rows):
    print(f"\n{'ID':<5}{'Date':<12}{'Amount':<15}{'Category':<15}Description")
    print("-" * 66)
    for id_, amount, category, description, when in rows:
        print(f"{id_:<5}{when:<12}₦{amount:<14,.2f}{category:<15}{description}")


def view_expenses(conn):
    rows = conn.execute(
        "SELECT id, amount, category, description, date FROM expenses ORDER BY date, id"
    ).fetchall()
    if not rows:
        print("No expenses recorded yet.")
        return False
    print_table(rows)
    return True


def total_expenses(conn):
    total = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses").fetchone()[0]
    print(f"Total spending: ₦{total:,.2f}")


def spending_by_category(conn):
    rows = conn.execute(
        "SELECT category, SUM(amount) FROM expenses GROUP BY category ORDER BY SUM(amount) DESC"
    ).fetchall()
    if not rows:
        print("No expenses recorded yet.")
        return
    print("\nSpending by category:")
    for category, amount in rows:
        print(f"  {category:<15}₦{amount:,.2f}")


def search_expenses(conn):
    keyword = input("Search keyword (category or description): ").strip()
    if not keyword:
        print("Please enter a keyword.")
        return
    like = f"%{keyword}%"
    rows = conn.execute(
        """
        SELECT id, amount, category, description, date FROM expenses
        WHERE category LIKE ? OR description LIKE ?
        ORDER BY date, id
        """,
        (like, like),
    ).fetchall()
    if rows:
        print_table(rows)
    else:
        print("No matching expenses found.")


def delete_expense(conn):
    if not view_expenses(conn):
        return
    try:
        expense_id = int(input("Enter the ID of the expense to delete: "))
    except ValueError:
        print("Invalid ID.")
        return
    row = conn.execute(
        "SELECT amount, category FROM expenses WHERE id = ?", (expense_id,)
    ).fetchone()
    if row is None:
        print("No expense with that ID.")
        return
    confirm = input(f"Delete ₦{row[0]:,.2f} ({row[1]})? (y/n): ").strip().lower()
    if confirm == "y":
        conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
        print("Expense deleted.")
    else:
        print("Cancelled.")


# ---------- Main loop ----------
def main():
    conn = connect()
    while True:
        print("\n--- PERSONAL EXPENSE TRACKER (SQLite) ---")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Total Spending")
        print("4. Spending by Category")
        print("5. Search Expenses")
        print("6. Delete Expense")
        print("7. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_expense(conn)
        elif choice == "2":
            view_expenses(conn)
        elif choice == "3":
            total_expenses(conn)
        elif choice == "4":
            spending_by_category(conn)
        elif choice == "5":
            search_expenses(conn)
        elif choice == "6":
            delete_expense(conn)
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please pick 1-7.")
    conn.close()


if __name__ == "__main__":
    main()
