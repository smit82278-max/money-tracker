from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "secret123"

DB_NAME = "expenses.db"

# Users
USERS = {
    "neel": "neel@2026",
    "smit": "smit@2026",
    "suresh": "suresh@2026"
}

# Initialize DB
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

    # Optional: delete data older than 1 year
    c.execute("DELETE FROM expenses WHERE date < date('now', '-365 days')")

    conn.commit()
    conn.close()

init_db()

# 🔐 LOGIN
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


# 🏠 DASHBOARD (ONLY TODAY DATA)
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    # Only today's data
    c.execute(
        "SELECT * FROM expenses WHERE date LIKE ? ORDER BY id DESC",
        (today + '%',)
    )
    expenses = c.fetchall()

    # Today's total
    c.execute(
        "SELECT SUM(amount) FROM expenses WHERE date LIKE ?",
        (today + '%',)
    )
    total = c.fetchone()[0]

    conn.close()

    return render_template(
        'index.html',
        expenses=expenses,
        total=total or 0,
        user=session['user']
    )


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


# 📅 HISTORY PAGE (ALL DATA)
@app.route('/history')
def history():
    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT * FROM expenses ORDER BY date DESC")
    data = c.fetchall()

    conn.close()

    return render_template('history.html', data=data, user=session['user'])


# RUN APP
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
