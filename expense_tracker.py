import json
import os
from datetime import date, datetime

DATA_FILE = "expenses.json"


# ---------- Saving / loading ----------
def load_expenses():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        print("Could not read the data file. Starting with an empty list.")
        return []


def save_expenses(expenses):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(expenses, f, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"Could not save expenses: {e}")


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
def add_expense(expenses):
    amount = ask_amount()
    category = ask_nonempty("Enter category: ").title()
    description = input("Enter description: ").strip()
    when = ask_date()
    expenses.append({
        "amount": amount,
        "category": category,
        "description": description,
        "date": when,
    })
    save_expenses(expenses)
    print("Expense added!")


def print_table(rows):
    print(f"\n{'#':<4}{'Date':<12}{'Amount':<15}{'Category':<15}Description")
    print("-" * 65)
    for i, e in rows:
        print(f"{i:<4}{e['date']:<12}₦{e['amount']:<14,.2f}{e['category']:<15}{e['description']}")


def view_expenses(expenses):
    if not expenses:
        print("No expenses recorded yet.")
        return
    print_table(list(enumerate(expenses, start=1)))


def total_expenses(expenses):
    total = sum(e["amount"] for e in expenses)
    print(f"Total spending: ₦{total:,.2f}")


def spending_by_category(expenses):
    if not expenses:
        print("No expenses recorded yet.")
        return
    totals = {}
    for e in expenses:
        totals[e["category"]] = totals.get(e["category"], 0) + e["amount"]
    print("\nSpending by category:")
    for cat, amt in sorted(totals.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat:<15}₦{amt:,.2f}")


def search_expenses(expenses):
    keyword = input("Search keyword (category or description): ").strip().lower()
    if not keyword:
        print("Please enter a keyword.")
        return
    matches = [
        (i, e) for i, e in enumerate(expenses, start=1)
        if keyword in e["category"].lower() or keyword in e["description"].lower()
    ]
    if matches:
        print_table(matches)
    else:
        print("No matching expenses found.")


def delete_expense(expenses):
    if not expenses:
        print("No expenses to delete.")
        return
    view_expenses(expenses)
    try:
        number = int(input("Enter the number of the expense to delete: "))
    except ValueError:
        print("Invalid number.")
        return
    if not 1 <= number <= len(expenses):
        print("That number is not in the list.")
        return
    removed = expenses[number - 1]
    confirm = input(
        f"Delete ₦{removed['amount']:,.2f} ({removed['category']})? (y/n): "
    ).strip().lower()
    if confirm == "y":
        expenses.pop(number - 1)
        save_expenses(expenses)
        print("Expense deleted.")
    else:
        print("Cancelled.")


# ---------- Main loop ----------
def main():
    expenses = load_expenses()
    while True:
        print("\n--- PERSONAL EXPENSE TRACKER ---")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Total Spending")
        print("4. Spending by Category")
        print("5. Search Expenses")
        print("6. Delete Expense")
        print("7. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_expense(expenses)
        elif choice == "2":
            view_expenses(expenses)
        elif choice == "3":
            total_expenses(expenses)
        elif choice == "4":
            spending_by_category(expenses)
        elif choice == "5":
            search_expenses(expenses)
        elif choice == "6":
            delete_expense(expenses)
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please pick 1-7.")


if __name__ == "__main__":
    main()
