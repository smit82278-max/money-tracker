from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

DB_NAME = "expenses.db"

# Initialize Database
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            title TEXT,
            amount REAL,
            location TEXT,
            date TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()


# Home Page
@app.route('/')
def index():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT * FROM expenses ORDER BY id DESC")
    expenses = c.fetchall()

    c.execute("SELECT SUM(amount) FROM expenses")
    total = c.fetchone()[0]

    conn.close()

    return render_template('index.html', expenses=expenses, total=total or 0)


# Add Expense
@app.route('/add', methods=['POST'])
def add():
    name = request.form.get('name')
    title = request.form.get('title')
    amount = request.form.get('amount')
    location = request.form.get('location')
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute(
        "INSERT INTO expenses (name, title, amount, location, date) VALUES (?, ?, ?, ?, ?)",
        (name, title, amount, location, date)
    )

    conn.commit()
    conn.close()

    return redirect('/')


# Run App (LOCAL + RENDER COMPATIBLE)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render uses PORT env
    app.run(host="0.0.0.0", port=port)
