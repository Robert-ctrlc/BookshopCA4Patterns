from factories import BookFactory, UserFactory

class UserDAO:
    def __init__(self, conn):
        self.conn = conn

    def get_user_by_credentials(self, username, password):
        cur = self.conn.cursor()
        row = cur.execute('SELECT * FROM users WHERE name = ? AND password = ?', (username, password)).fetchone()
        if row:
            return UserFactory.create_user_from_row(row)
        return None

    def get_user_by_id(self, user_id):
        cur = self.conn.cursor()
        row = cur.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if row:
            return UserFactory.create_user_from_row(row)
        return None

class BookDAO:
    def __init__(self, conn):
        self.conn = conn

    def get_all_books(self, search, author, category, publisher, sort_strategy):
        cur = self.conn.cursor()
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

        query += f' {sort_strategy.sort_query()}'
        rows = cur.execute(query, params).fetchall()
        return [BookFactory.create_book_from_row(row) for row in rows]

    def get_categories(self):
        cur = self.conn.cursor()
        rows = cur.execute('SELECT DISTINCT category FROM books').fetchall()
        return rows

class UserDAO:
    def __init__(self, conn):
        self.conn = conn

    def get_user_by_id(self, user_id):
        cur = self.conn.cursor()
        row = cur.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if row:
            return UserFactory.create_user_from_row(row)
        return None

    def get_user_by_credentials(self, username, password):
        cur = self.conn.cursor()
        row = cur.execute('SELECT * FROM users WHERE name = ? AND password = ?', (username, password)).fetchone()
        if row:
            return UserFactory.create_user_from_row(row)
        return None
