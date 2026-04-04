from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Initialize Database
def init_db():
    conn = sqlite3.connect('expenses.db')
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
    conn = sqlite3.connect('expenses.db')
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
    name = request.form['name']
    title = request.form['title']
    amount = request.form['amount']
    location = request.form['location']
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()

    c.execute(
        "INSERT INTO expenses (name, title, amount, location, date) VALUES (?, ?, ?, ?, ?)",
        (name, title, amount, location, date)
    )

    conn.commit()
    conn.close()

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)