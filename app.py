from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "secret123"   # required for login session

DB_NAME = "expenses.db"

# Static users (your requirement)
USERS = {
    "neel": "neel@2026",
    "smit": "smit@2026",
    "suresh": "suresh@2026"
}

# Initialize DB (removed name column)
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            amount REAL,
            location TEXT,
            date TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()


# 🔐 LOGIN PAGE
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in USERS and USERS[username] == password:
            session['user'] = username
            return redirect('/dashboard')
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')


# 🚪 LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


# 🏠 DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT * FROM expenses ORDER BY id DESC")
    expenses = c.fetchall()

    c.execute("SELECT SUM(amount) FROM expenses")
    total = c.fetchone()[0]

    conn.close()

    return render_template('index.html', expenses=expenses, total=total or 0, user=session['user'])


# ➕ ADD EXPENSE
@app.route('/add', methods=['POST'])
def add():
    if 'user' not in session:
        return redirect('/')

    title = request.form['title']
    amount = request.form['amount']
    location = request.form['location']
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute(
        "INSERT INTO expenses (title, amount, location, date) VALUES (?, ?, ?, ?)",
        (title, amount, location, date)
    )

    conn.commit()
    conn.close()

    return redirect('/dashboard')


# Run app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
