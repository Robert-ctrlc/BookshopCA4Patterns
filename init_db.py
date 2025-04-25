
import sqlite3

conn = sqlite3.connect('books.db')
c = conn.cursor()

c.execute('DROP TABLE IF EXISTS books')
c.execute('DROP TABLE IF EXISTS users')
c.execute('DROP TABLE IF EXISTS orders')

# Books
c.execute('''
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    publisher TEXT,
    price REAL,
    category TEXT,
    isbn TEXT,
    stock INTEGER,
    image_url TEXT
)
''')

# Users
c.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    password TEXT,
    is_admin INTEGER
)
''')

# Orders
c.execute('''
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    book_id INTEGER,
    quantity INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(book_id) REFERENCES books(id)
)
''')

# Dummy books
c.execute('''INSERT INTO books (title, author, publisher, price, category, isbn, stock, image_url)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
          ("The Pragmatic Programmer", "Andy Hunt", "Addison-Wesley", 39.99, "Programming", "9780135957059", 10, "https://via.placeholder.com/100"))

c.execute('''INSERT INTO books (title, author, publisher, price, category, isbn, stock, image_url)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
          ("Clean Code", "Robert C. Martin", "Prentice Hall", 42.50, "Programming", "9780132350884", 5, "https://via.placeholder.com/100"))

# Dummy users
c.execute("INSERT INTO users (name, password, is_admin) VALUES (?, ?, ?)", ("alice", "pass123", 0))  # customer
c.execute("INSERT INTO users (name, password, is_admin) VALUES (?, ?, ?)", ("bob", "adminpass", 1))  # admin

conn.commit()
conn.close()

print("✅ Database initialized.")
