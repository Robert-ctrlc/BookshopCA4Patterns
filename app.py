from flask import Flask, render_template, request, redirect, url_for
from factories import BookFactory, UserFactory
from strategies import TitleSortStrategy, PriceSortStrategy, AuthorSortStrategy, PublisherSortStrategy

import sqlite3

app = Flask(__name__)

# ----------------- DATABASE CONNECTION ----------------- #
def get_db_connection():
    conn = sqlite3.connect('books.db')
    conn.row_factory = sqlite3.Row
    return conn

# ----------------- ROUTES ----------------- #

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        row = conn.execute('SELECT * FROM users WHERE name = ? AND password = ?', (username, password)).fetchone()
        user = UserFactory.create_user_from_row(row) if row else None

        conn.close()

        if user:
            return redirect(url_for('book_list', user_id=user['id']))
        else:
            error = "Invalid username or password."

    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    success = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']
        address = request.form['address']
        payment_method = request.form['payment_method']
        is_admin = 1 if request.form.get('is_admin') == 'on' else 0

        conn = get_db_connection()
        existing = conn.execute('SELECT * FROM users WHERE name = ?', (username,)).fetchone()

        if existing:
            error = "Username already taken."
        elif password != confirm:
            error = "Passwords do not match."
        else:
            conn.execute("INSERT INTO users (name, password, is_admin, address, payment_method) VALUES (?, ?, ?, ?, ?)",
                         (username, password, is_admin, address, payment_method))
            conn.commit()
            success = "Account created! Please log in."
        
        conn.close()

    return render_template('register.html', error=error, success=success)

@app.route('/books')
def book_list():
    user_id = request.args.get('user_id')
    sort_by = request.args.get('sort_by', 'title')

    search = request.args.get('search', '')
    author = request.args.get('author', '')
    category = request.args.get('category', '')
    publisher = request.args.get('publisher', '')

    conn = get_db_connection()
    row = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    user = UserFactory.create_user_from_row(row) if row else None

    query = 'SELECT * FROM books WHERE 1=1'
    params = []

    if search:
        query += ' AND title LIKE ?'
        params.append(f'%{search}%')
    if author:
        query += ' AND author LIKE ?'
        params.append(f'%{author}%')
    if category:
        query += ' AND category LIKE ?'
        params.append(f'%{category}%')
    if publisher:
        query += ' AND publisher LIKE ?'
        params.append(f'%{publisher}%')

    strategies = {
        'title': TitleSortStrategy(),
        'price': PriceSortStrategy(),
        'author': AuthorSortStrategy(),
        'publisher': PublisherSortStrategy()
    }

    sort_strategy = strategies.get(sort_by, TitleSortStrategy())
    query += f' {sort_strategy.sort_query()}'

    rows = conn.execute(query, params).fetchall()
    categories = conn.execute('SELECT DISTINCT category FROM books').fetchall()

    ratings = {
        row['book_id']: row['avg']
        for row in conn.execute('SELECT book_id, AVG(rating) AS avg FROM reviews GROUP BY book_id').fetchall()
    }

    conn.close()

    books_with_ratings = []
    for b in rows:
        b = dict(b)
        b['avg_rating'] = round(ratings.get(b['id'], 0), 1)
        books_with_ratings.append(b)

    return render_template('books.html', books=books_with_ratings, user=user, categories=categories, filters={
        'search': search,
        'author': author,
        'publisher': publisher,
        'category': category,
        'sort_by': sort_by
    })

@app.route('/cart', methods=['POST'])
def cart():
    user_id = request.form.get('user_id')
    cart_items = []

    for key, value in request.form.items():
        if key.startswith('book_') and value.strip() and int(value) > 0:
            book_id = int(key.split('_')[1])
            qty = int(value)
            cart_items.append((book_id, qty))

    if not cart_items:
        return "No books selected. <a href='/books?user_id={0}'>Go back</a>".format(user_id)

    conn = get_db_connection()
    row = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    user = UserFactory.create_user_from_row(row) if row else None

    books = []
    total = 0

    for book_id, qty in cart_items:
        row = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
        book = BookFactory.create_book_from_row(row)
        if book:
            subtotal = qty * book['price']
            total += subtotal
            books.append({'book': book, 'qty': qty, 'subtotal': subtotal})

   
    order_count = conn.execute('SELECT COUNT(*) FROM orders WHERE user_id = ?', (user_id,)).fetchone()[0]
    orders_to_next_reward = 3 - (order_count % 3)
    show_loyalty_hint = orders_to_next_reward != 3

    
    discount_applied = total >= 100
    discount_amount = round(total * 0.10, 2) if discount_applied else 0

    conn.close()

    return render_template('cart.html',
        user=user,
        books=books,
        total=total,
        discount_applied=discount_applied,
        discount_amount=discount_amount,
        show_loyalty_hint=show_loyalty_hint,
        orders_to_next_reward=orders_to_next_reward if show_loyalty_hint else None
    )


@app.route('/checkout', methods=['POST'])
def checkout():
    user_id = request.form.get('user_id')
    conn = get_db_connection()

    total = 0
    order_items = []

    for key, value in request.form.items():
        if key.startswith('book_') and int(value) > 0:
            book_id = int(key.split('_')[1])
            qty = int(value)
            row = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
            book = BookFactory.create_book_from_row(row)
            if book:
                subtotal = qty * book['price']
                total += subtotal
                order_items.append((book_id, qty))

    
    discount_applied = total >= 100
    discount_amount = 0
    if discount_applied:
        discount_amount = round(total * 0.10, 2)
        total -= discount_amount

  
    for book_id, qty in order_items:
        conn.execute('INSERT INTO orders (user_id, book_id, quantity) VALUES (?, ?, ?)',
                 (user_id, book_id, qty))
    conn.execute('UPDATE books SET stock = stock - ? WHERE id = ? AND stock >= ?',
                 (qty, book_id, qty))


    conn.commit()

    order_count = conn.execute('SELECT COUNT(*) FROM orders WHERE user_id = ?', (user_id,)).fetchone()[0]
    loyalty_discount = 0
    if order_count % 3 == 0:
     loyalty_discount = 5
    total -= loyalty_discount

    conn.close()


    return render_template(
    'checkout_success.html',
    user_id=user_id,
    total=total,
    discount_applied=discount_applied,
    discount_amount=discount_amount,
    loyalty_discount=loyalty_discount  
)


@app.route('/admin')
def admin_dashboard():
    user_id = request.args.get('user_id')
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    user = UserFactory.create_user_from_row(row) if row else None


    if not user or user['is_admin'] != 1:
        conn.close()
        return "Access denied."

    books = conn.execute('SELECT * FROM books').fetchall()
    users = conn.execute('SELECT * FROM users').fetchall()
    orders = conn.execute('''
        SELECT o.id, u.name AS customer, b.title, o.quantity
        FROM orders o
        JOIN users u ON o.user_id = u.id
        JOIN books b ON o.book_id = b.id
        ORDER BY o.id DESC
    ''').fetchall()

    
    total_orders = conn.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
    total_books_sold = conn.execute('SELECT SUM(quantity) FROM orders').fetchone()[0] or 0
    total_revenue = conn.execute('''
        SELECT SUM(o.quantity * b.price)
        FROM orders o
        JOIN books b ON o.book_id = b.id
    ''').fetchone()[0] or 0
    total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    avg_rating = conn.execute('SELECT AVG(rating) FROM reviews').fetchone()[0] or 0

    best_seller = conn.execute('''
        SELECT b.title, SUM(o.quantity) AS sold
        FROM orders o
        JOIN books b ON o.book_id = b.id
        GROUP BY o.book_id
        ORDER BY sold DESC
        LIMIT 1
    ''').fetchone()

    conn.close()

    return render_template('admin.html',
                           user=user,
                           books=books,
                           users=users,
                           orders=orders,
                           total_orders=total_orders,
                           total_books_sold=total_books_sold,
                           total_revenue=round(total_revenue, 2),
                           total_users=total_users,
                           avg_rating=round(avg_rating, 1),
                           best_seller=best_seller)


@app.route('/admin/add_book', methods=['GET', 'POST'])
def add_book():
    user_id = request.args.get('user_id')
    if request.method == 'POST':
        data = request.form
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO books (title, author, publisher, price, category, isbn, stock, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['title'], data['author'], data['publisher'],
            data['price'], data['category'], data['isbn'],
            data['stock'], data['image_url']
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard', user_id=user_id))
    return render_template('book_form.html', user_id=user_id, action='Add')

@app.route('/admin/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    user_id = request.args.get('user_id')
    conn = get_db_connection()
    if request.method == 'POST':
        data = request.form
        conn.execute('''
            UPDATE books SET title=?, author=?, publisher=?, price=?, category=?, isbn=?, stock=?, image_url=?
            WHERE id=?
        ''', (
            data['title'], data['author'], data['publisher'],
            data['price'], data['category'], data['isbn'],
            data['stock'], data['image_url'], book_id
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard', user_id=user_id))

    row = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    book = BookFactory.create_book_from_row(row)
    conn.close()
    return render_template('book_form.html', book=book, user_id=user_id, action='Edit')

@app.route('/admin/delete_book/<int:book_id>')
def delete_book(book_id):
    user_id = request.args.get('user_id')
    conn = get_db_connection()
    conn.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard', user_id=user_id))

@app.route('/orders')
def order_history():
    user_id = request.args.get('user_id')
    conn = get_db_connection()

    row = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    user = UserFactory.create_user_from_row(row) if row else None


    if not user:
        conn.close()
        return "User not found."

    orders = conn.execute('''
        SELECT o.id, b.title, o.quantity, b.price, (o.quantity * b.price) AS total
        FROM orders o
        JOIN books b ON o.book_id = b.id
        WHERE o.user_id = ?
        ORDER BY o.id DESC
    ''', (user_id,)).fetchall()

    conn.close()
    return render_template('orders.html', user=user, orders=orders)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = request.args.get('user_id')
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    user = UserFactory.create_user_from_row(row) if row else None


    if request.method == 'POST':
        address = request.form['address']
        payment = request.form['payment_method']
        conn.execute('UPDATE users SET address = ?, payment_method = ? WHERE id = ?', (address, payment, user_id))
        conn.commit()
        row = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        user = UserFactory.create_user_from_row(row) if row else None


    conn.close()
    return render_template('profile.html', user=user)

@app.route('/admin/restock/<int:book_id>', methods=['POST'])
def restock_book(book_id):
    user_id = request.form['user_id']
    amount = int(request.form['amount'])

    conn = get_db_connection()
    conn.execute('UPDATE books SET stock = stock + ? WHERE id = ?', (amount, book_id))
    conn.commit()
    conn.close()

    return redirect(url_for('admin_dashboard', user_id=user_id))

@app.route('/logout')
def logout():
    return redirect(url_for('login'))

@app.route('/book/<int:book_id>', methods=['GET', 'POST'])
def book_detail(book_id):
    user_id = request.args.get('user_id')

    conn = get_db_connection()
    row = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    book = BookFactory.create_book_from_row(row)    
    row = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    user = UserFactory.create_user_from_row(row) if row else None


    if request.method == 'POST':
        rating = int(request.form['rating'])
        comment = request.form['comment']
        conn.execute('INSERT INTO reviews (user_id, book_id, rating, comment) VALUES (?, ?, ?, ?)',
                     (user_id, book_id, rating, comment))
        conn.commit()

    reviews = conn.execute('''
        SELECT r.rating, r.comment, u.name FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.book_id = ?
    ''', (book_id,)).fetchall()

    avg_rating = conn.execute('SELECT AVG(rating) AS avg FROM reviews WHERE book_id = ?', (book_id,)).fetchone()['avg']
    conn.close()

    return render_template('book_detail.html', book=book, user=user, reviews=reviews, avg_rating=avg_rating)

# ----------------- MAIN ----------------- #
if __name__ == '__main__':
    app.run(debug=True)
