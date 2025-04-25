# app.py
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Helper: connect to database
def get_db_connection():
    conn = sqlite3.connect('books.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home redirect to login
@app.route('/')
def home():
    return redirect(url_for('login'))

# Login page + auth
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE name = ? AND password = ?', 
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            return redirect(url_for('book_list', user_id=user['id']))
        else:
            error = "Invalid username or password."

    return render_template('login.html', error=error)

# View books (with optional sorting)
@app.route('/books')
def book_list():
    user_id = request.args.get('user_id')
    sort_by = request.args.get('sort_by', 'title')

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    books = conn.execute(f'SELECT * FROM books ORDER BY {sort_by} ASC').fetchall()
    conn.close()

    return render_template('books.html', books=books, user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    success = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']
        is_admin = 1 if request.form.get('is_admin') == 'on' else 0

        conn = get_db_connection()
        existing = conn.execute('SELECT * FROM users WHERE name = ?', (username,)).fetchone()

        if existing:
            error = "Username already taken."
        elif password != confirm:
            error = "Passwords do not match."
        else:
            conn.execute('INSERT INTO users (name, password, is_admin) VALUES (?, ?, ?)', 
                         (username, password, is_admin))
            conn.commit()
            success = "Account created! Please log in."
        
        conn.close()

    return render_template('register.html', error=error, success=success)