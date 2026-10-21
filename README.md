# 💸 Personal Expense Tracker

A Python expense tracker built in stages, from a simple command-line script to a web app.

## Features
- Add expenses (amount, category, description, date)
- View all expenses
- Total spending and spending by category (with chart)
- Search and filter by keyword or category
- Delete an expense
- Data saved in a SQLite database

## Project versions
| File | What it is |
|------|-----------|
| `expense_tracker.py` | Command-line version, saves to a JSON file |
| `expense_tracker_sqlite.py` | Command-line version, saves to SQLite |
| `app.py` | Streamlit web app, saves to SQLite |

## Run it locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

Command-line versions:
```bash
python expense_tracker.py
python expense_tracker_sqlite.py
```

## Live demo
Add your Streamlit link here after deploying.

## Built with
Python, SQLite, Streamlit, pandas
